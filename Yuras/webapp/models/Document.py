from Yuras.common.StoredObject import StoredObject
from Yuras.common.Pandoc import Pandoc
from Yuras.common.Config import Config

from Yuras.webapp.models.Annotation import Annotation
from Yuras.webapp.models.User import User
from Yuras.webapp.models.Category import Category

import re, base64, collections, os, urllib2, json, pprint, multiprocessing, scrypt, math

from bson.objectid import ObjectId

from flask import abort, Response

class Document(StoredObject):
	def __init__(self):
		self.title = "Document"
		self.createdDate = None
		self.modifiedDate = None
		self.contents = ""
		self.tags = {}
		self.annotations = []
		self.category = None
		self.wordcount = {}
		
		self.accessible = True
		
		self.secure = False
		
		super(Document, self).__init__(collection = "documents")
		
	def matchObjects(self, match, limit=None, skip=0, fields={"wordcount":0}, sort=None,reverse=False):
		# Does not return wordcount by default
		return super(Document, self).matchObjects(match,limit,skip,fields,sort,reverse)
	
	@staticmethod
	def getStopwords():
		with open(os.path.join( Config().WebAppDirectory, "../..", "stopwords.txt"), "r") as swf:
			stopwords = swf.read().split("\n")
		return stopwords
	
	def plainWordCount(self, filterStopwords=True):
		plainContents = Pandoc().convert("markdown_github", "plain", self.contents.lower())
		plainWordRegex = re.compile("[a-z]{2,}")
		words = plainWordRegex.findall(self.title.lower()) + plainWordRegex.findall(plainContents)
		wordCount = collections.defaultdict(int)
		
		if filterStopwords:
			stopwords = Document.getStopwords()
			words = [ word for word in words if word not in stopwords ] # Remove all stopwords		
		
		for word in words:
			wordCount[word] += 1
		
		return words, wordCount
	
	def hashedWordCount(self, plainWordCount, results):
		b64enc = base64.b64encode
		hashedWordCount = collections.defaultdict(int)
		salt = str(Config().database)
		for word, count in plainWordCount:
			key = b64enc(scrypt.hash(str(word), salt, N=1<<9))
			hashedWordCount[key] = count
		results += dict(hashedWordCount).items()
	
	def countWords(self, store=True):
		words, plainWordCount = self.plainWordCount()
		
		manager = multiprocessing.Manager()
		results = manager.list()

		cores = multiprocessing.cpu_count()
		chunkSize = len(plainWordCount)/cores

		pool = []
		for core in range(cores):
			p = multiprocessing.Process(
				target=self.hashedWordCount,
				args = (
					plainWordCount.items()[int(chunkSize*core):int(chunkSize*(core+1))],
					results
				)
			)
			p.start()
			pool.append( p )

		for p in pool:
			p.join()
		
		hashedWordCount = dict(results)
		
		if store:
			self.wordcount = hashedWordCount
		
		return hashedWordCount
	
	def __storeAnnotations(self, annotations):
		print annotations
		annotations = json.loads(annotations)
		print annotations
		for anno_id, annotation in annotations.items():
			try:
				a = Annotation().getObjectsByKey("_id", anno_id)[0]
			except:
				a = Annotation()

			a.contents = annotation["text"].encode('utf-8')
			a.location = [int(i) for i in annotation["location"].split(",")]
			a.document = unicode(self._id)
			a.page = int(annotation.get("page",0))
			a.document_title = str(self.title)
			a.selected_text = annotation["selected_text"].encode('utf-8')
			a.linked_to = int(annotation["linked-to"])
						
			a.save()
		
	def save(self, title, contents, category, annotations):
		# Set contents
		contents_escaped = urllib2.unquote( contents )
		contents_md = unicode(Pandoc().convert("html","markdown_github",contents_escaped))
		self.contents = contents_md.encode('utf-8')
		
		# Set title
		title = urllib2.unquote( title )
		self.title = title	
		
		# Set category
		category = urllib2.unquote( category )		
		if len(Category().getObjectsByKey("name", category)) == 0:
			c = Category()
			c.name = category
			c.save()

		self.category = category
		
		# Set annotations
		annotations = urllib2.unquote( annotations )
		self.__storeAnnotations(annotations)

		super(Document, self).save()
		return True
	
	def quickSearch(self, words):
		matchedObjects = {}
		
		for word in words:
			key = base64.b64encode(scrypt.hash(str(word), str(Config().database), N=1<<9))
			matchedObjects["tags."+key] = { "$exists": True }
		
		results = self.matchObjects(matchedObjects, fields={"_id":True,"title":True})
		
		return json.dumps(dict([(str(document._id), document.title) for document in results ]))
	
	def download(self, filetype):
		filetypes = {
			"docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
			"pdf":"application/pdf",
			"txt":"text/plain",
		}

		pandoc_filetypes = {
			"docx":"docx",
			"pdf":"latex --latex-engine=pdflatex",
			"txt":"plain"
		}

		if filetype in filetypes:
			responseContents = Pandoc().convert("markdown_github", pandoc_filetypes[filetype], self.contents, filetype=filetype)
			response = Response(responseContents, mimetype=filetypes[filetype])

			filename = self.title + "." + filetype

			response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
			return response
		else:
			return abort(405)
	
	def __loopTermFrequencies(self, termFrequencies, tfidf, documentCount, wordCountsByKey ):
		# This function is paralellized due to the large amount of words and long CPU times.
		for word, (count, tf) in termFrequencies:
			key = base64.b64encode(scrypt.hash(str(word), str(Config().database), N=1<<9))
			idf = math.log(float(documentCount) / (1+wordCountsByKey.get(key,0)))			
			tfidf[word] = (idf*tf, key)
		print "ltf done"
		
	def documentAnalysis(self):
		if len(self.tags) == 0 or not isinstance(self.tags, dict):
			self.tfidf()
			
		return json.dumps( self.getRelatedDocumentsByIndividualTags(self.tags) )
	
	def getRelatedDocumentsByIndividualTags(self, tags):
		results = {}
		print tags
		for key,word in tags.items():
			related = Document().matchObjects(
				{"$and": [
						{"wordcount."+key : { "$exists": True }},
						{"_id": {"$ne": ObjectId(self._id)}} # A conversion to ObjectId is needed for Mongo/Toku
					]},
				fields = {"title":True, "_id":True,"wordcount."+key:True},
				sort = "wordcount."+key,
				reverse=True
			)
			relatedResults = []
			for r in related[:3]:
				relatedResults.append(
					{
						"title":r.title,
						"_id":str(r._id)
					}
				)
			results[word] = relatedResults
		
		return results
			
	def getRelatedDocumentsByTags(self):
		matchTags = []
		tags = self.tags.keys()
		for tag in tags:
			matchTags.append({"tags."+tag: {"$exists":True}})

		match = {"$or": matchTags, "_id": {"$ne": self._id}}

		allDocuments = Document().matchObjects(
			match,
			fields={"title":True, "_id":True,"tags":True}
		)
		tagsSet = set(tags)

		for d in allDocuments:
			d.tagsIntersect = list(tagsSet.intersection(set(d.tags.keys())))

		if len(allDocuments) == 0:
			return "{}"

		allDocuments.sort(key=lambda d: len(d.tagsIntersect), reverse=True)
		maxIntersectLength = len(allDocuments[0].tagsIntersect)*0.5
		
		return json.dumps([(str(d._id), 
							d.title, 
							float(len(d.tagsIntersect)) / float(len(allDocuments[0].tagsIntersect))
							) for d in allDocuments if len(d.tagsIntersect)>maxIntersectLength])
				
	def tfidf(self, allDocuments=None, multiprocessLTF=True):
		manager = multiprocessing.Manager()
		words,wordcount = self.plainWordCount()
		
		wordslen = len(words)
		termFrequencies = {}
		for word in words:
			termFrequencies[word] = (wordcount[word], float(wordcount[word])/wordslen)
			
		if allDocuments is None:
			allDocuments = self.matchObjects(
				{"category":self.category},
				fields={"wordcount":True}
			)
		
		documentCount = len(allDocuments)

		allWordCounts = []
		for d in allDocuments:
			allWordCounts += d.wordcount.keys()

		wordCountsByKey = collections.defaultdict(int)
		for k in allWordCounts:
			wordCountsByKey[k] += 1

		tfidf = manager.dict()
		managerWordCountsByKey = manager.dict(wordCountsByKey)
		
		if multiprocessLTF:
			cores = multiprocessing.cpu_count()
			chunkSize = len(termFrequencies)/cores
			pool = []
			for core in range(cores):
				p = multiprocessing.Process(
					target=self.__loopTermFrequencies,
					args = (
						termFrequencies.items()[int(chunkSize*core):int(chunkSize*(core+1))],
						tfidf,
						documentCount,
						managerWordCountsByKey
					)
				)
				p.start()
				pool.append( p )

			for p in pool:
				p.join()
		else:
			self.__loopTermFrequencies(termFrequencies.items(), tfidf, documentCount, managerWordCountsByKey)

		results = {}
		
		sortedItems = sorted( tfidf.items(), key=lambda x: x[1][0], reverse=True )
		percentile = 0.05
		maxitems = int((len(sortedItems)*percentile)+1)
		
		tags = {}
		for item in sortedItems[:maxitems]:
			tags[item[1][1]] = item[0]
			
		self.tags = tags
		super(Document, self).save()
	
	@staticmethod
	def __flatten(d, parent_key='', sep='_'):
		items = []
		for k, v in d.items():
			new_key = parent_key + sep + k if parent_key else k
			if isinstance(v, collections.MutableMapping):
				items.extend(Document.__flatten(v, new_key, sep=sep).items())
			else:
				items.append((new_key, v))
		return dict(items)
	
	@staticmethod
	def generateJurisprudenceDocuments():
		jurisprudence = json.load( open(os.path.join( Config().WebAppDirectory, "..", "..", "jurisprudence.json"), "r") )
		
		stopwords = Document.getStopwords()
		
		categorized = {}
		wiki = jurisprudence["Yuras"]["wiki"]
		flatWiki = Document.__flatten(wiki)
		dCounter = 1
		dTotal = len(flatWiki)
		for key, document in flatWiki.items():
			title = key.split("_")[-1].strip(".html").split("/")[-1].replace("-"," ")
			title = title[0].upper() + title[1:]
			key = key.split("_")[0]

			if key not in categorized:
				categorized[key] = []
				if len(Category().getObjectsByKey("name", key)) == 0:
					c = Category()
					c.name = key
					c.save()

			if len(Document().getObjectsByKey("title", title)) == 0:
				d = Document()
				d.title = title
				d.category = key
				d.contents = Pandoc().convert("html","markdown_github", document)
				d.author = "Yuras"
				d.countWords()
				super(Document, d).save()

			categorized[key].append(document)
			print title, "saved", dCounter, "/", dTotal
			dCounter += 1