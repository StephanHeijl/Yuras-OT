#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, os, pprint, re, math, operator, collections, requests, sys,time
from Yuras.common.Config import Config

from xml.dom.minidom import parse, parseString

#from Yuras.webapp.models.Document import Document

def memodict(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret 
    return memodict().__getitem__

def persist_to_file(file_name):
    def decorator(original_func):
        try:
            cache = json.load(open(file_name, 'r'))
        except (IOError, ValueError):
            cache = {}

        def new_func(param):
            if param not in cache:
                cache[param] = original_func(param)
                json.dump(cache, open(file_name, 'w'))
            return cache[param]

        return new_func

    return decorator

class RechtspraakParser():
	def __init__(self):
		self.rechtspraakFolder = Config().WebAppDirectory+"/../../rechtspraak"
		self.jsonFileName = "10krecords.json"
		self.delimitor = re.compile("[^a-z]*")
		self.articleRegex = re.compile(r"([Aa]rtikel(en)?|art\.) ((\d+|[IVX]+)([:\.]\d+)?([a-z]+)?( en |, ?)?)+ ?(([etdvzan][ewic][a-z]+?((d|st)e[^a-z]))?(lid|paragraaf|volzin)( \d+)?([, ])*)*((van|het|de|Wet|wet) )*( ?(([A-Z]([A-Z]{1,4}|[a-z]{1,2}))[^\w]) ?(\d{4})?|([\w\-]+ ?)+ ?(\d{4})?)")	
		
	def parseJson(self, filename):
		path = os.path.join(self.rechtspraakFolder,filename)
		documents = json.load(open(path))
		return documents		

	def learnArticles(self, documents):
		# This regex matches everything after the initial article number.
		articles = {}
		
		for _id,document in documents.items():
			contents = self.getDocumentContents(document)
			if contents is None:
				continue
				
			for article in self.articleRegex.finditer( contents ):
				normArticle = article.group(0).strip(",.() ").replace("art.", "artikel").replace("Artikel","artikel")
				articles[normArticle] = article
				
		strafrechtArticles = [ art for art in articles if "strafrecht" in art.lower()]
		
		with open(Config().WebAppDirectory+"/../../wbvstrafrecht.txt") as f:
			wbvstrafrecht = f.read().decode('ascii',errors="replace")
		
		for art in strafrechtArticles:
			numbers = list(set([ "".join(nr) for nr in re.findall("(\d+|[IVX]+)([:\.]\d+)?([a-z]+)?",art)]))
			for number in numbers:
				key = "**artikel "+number
				
				try:
					#print key
					index = wbvstrafrecht.lower().index(key)
					print wbvstrafrecht[index:wbvstrafrecht.index("**A", index+20)]
					print "-"*80
				except:
					pass
				
	def listGet(self, l, idx, default):
		try:
			return l[idx]
		except IndexError:
			return default
				
	def parseWetboek(self, filename):
		f = open(filename)
		
		articles = [[]]
		currentArticleIndex = 0
		lastRealArticleIndex = -1
		for line in f:
			if line == "\n":
				continue
			if line.startswith("**"):
				if re.match("\*\*([\w°])+(\.)",line):
					line = line.replace("*"," ")
				else:
					articles[-1].append(line.strip("* \n"))
					currentArticleIndex = len(articles)-1
					continue

			if len(articles[currentArticleIndex]) == 0:
				continue
				
			if not isinstance(articles[currentArticleIndex][-1], list):
				articles[currentArticleIndex].append([])
			articles[currentArticleIndex][-1].append(line.strip(" \n"))

			if len(articles[currentArticleIndex]) >= 3:
				lastRealArticleIndex = currentArticleIndex

			if len(articles[-1]) > 0:
				if len(articles[-1]) < 3 and lastRealArticleIndex >= 0:
					articles[lastRealArticleIndex][-1] += [ " ".join(articles[-1][:-1]) + " ".join(articles[-1][-1]) ]
					del articles[-1]
				articles.append([])
		
		structuredArticles = []
		chapterRegex = re.compile("hoofdstuk", flags=re.IGNORECASE)
		articleRegex = re.compile("art(ikel|\.)", flags=re.IGNORECASE)
		paragraphRegex = re.compile("paragraaf|§", flags=re.IGNORECASE)
		bookRegex = re.compile("boek", flags=re.IGNORECASE)
		documentTitle = articles[0][0]
		
		for a in articles:
			prevN = None
			try:
				law, structuredlaw = a[-1],{}
			except:
				continue
				
			book = self.listGet([ i for i in a[:-1] if bookRegex.search(i) is not None ], 0, documentTitle)
			paragraph = self.listGet([ i for i in a[:-1] if paragraphRegex.search(i) is not None ], 0, None)
			art = self.listGet([ i for i in a[:-1] if articleRegex.search(i) is not None ], 0, None)
			chapter = self.listGet([ i for i in a[:-1] if chapterRegex.search(i) is not None ], 0, None)
				
			if len(a[-1]) > 0:
				for i,sublaw in enumerate(law):
					n = re.search("^([\w ]{0,40})(\.|:)", sublaw)

					if n is not None:
						n = n.group(1)
						sublaw = sublaw[len(n)+1:]
						slaw = structuredlaw
						
						if re.match("\d",n):
							prevN = n
						else:
							if prevN is not None:
								#n = prevN.strip(".")+"."+n.strip(".")
								if not isinstance( structuredlaw[prevN], dict):
									structuredlaw[prevN] = {"":structuredlaw[prevN]}
								slaw = structuredlaw[prevN]								

						slaw[n.strip(".")] = sublaw.decode('ascii', errors="ignore").strip(" ")
					elif i == 0:
						structuredlaw[""] = sublaw.decode('ascii', errors="ignore").strip(" ")

			else:
				try:
					law = law[0]
				except:
					continue

			title = ", ".join([ e for e in [book, chapter, art, paragraph] if e is not None])
			contents = "#"+ title + "\n\n" + "\n".join(law)
			structuredArticles.append( {"book":book, "chapter":chapter,"art":art,"contents": contents, "paragraph":paragraph, "structuredlaw":structuredlaw, "title":title, "_encrypt":False, "document_type":"lawbook"} )
			
		print json.dumps(structuredArticles, indent=4)
		
	def downloadWetboeken(self):
		url = "http://epub.overheid.nl/default.aspx"
		epubUrl = re.compile("href=\"(/epub/[\w \/_\.]+)\"")
		urls = []
		for letter in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
			r = requests.post(url, params={"zoekletter":letter})
			urls += epubUrl.findall(r.text)
			
		for url in urls:
			print url
			
	def parseRechtspraak(self, filename=None, document=None):
		"""
		Used in conjuction with
		$ for file in rechtspraak/results/*.json; do echo "$file"; python -m Yuras.machine_learning_ng.RechtspraakParser $file | mongoimport --db "Yuras1" -c documents ; done
		
		"""
		if filename is not None:
			documents = self.parseJson(filename)
		
		if document is not None:
			documents = {document["id"]:document}
			
		for _id, document in documents.items():
			try:
				contents = document["contents"]["results"]["uitspraak"]
			except KeyError as e:
				continue
				
			d = {"document_id":_id,
				 "_encrypt":False,
				 "contents": "#" + document["Titel"] + "\n" + contents,
				 "category": document["Rechtsgebieden"].replace(" ","_"),
				 "title": document["Titel"],
				 "published": document["Publicatiedatum"],
				 "document_type":"jurisprudence",
				 "source":document["Titel"].split(",")[0].replace(" ","_"),
				}
			
			english_map = {
				"Instantie":"judicial_instance",
				"latitude":"location_lat",
				"longtitude":"location_lng",
				"Zittingsplaats":"location",
				"Zaaknummer":"case_id",
				"Procedure":"procedurals",
				"summary":"summary",
				"Beslissing":"decision",
				"ProsecutionScore":"prosecution_score"
			}
			
			for source,target in english_map.items():
				try:
					d[target] = document[source]
				except:
					pass
			
			print json.dumps(d)
			
			
	def parseXmlRechtspraak(self, filename):
		parsedDocument = {}
		
		with open(filename) as f:
			xml = parseString(f.read())
			
		try:
			uitspraak = xml.getElementsByTagName("uitspraak")[0]
		except:
			exit()

		parsedDocument["uitspraak"] = []
		for para in uitspraak.getElementsByTagName("para"):
			try:
				parsedDocument["uitspraak"].append(para.firstChild.nodeValue)
			except:
				pass
			
		parsedDocument["id"] = xml.getElementsByTagName("dcterms:identifier")[0].firstChild.nodeValue
		
		pointsOfInterest = {
			"Publicatiedatum":"dcterms:issued",
			"Rechtsgebieden":"dcterms:subject",
			"Zittingsplaats":"dcterms:spatial",
			"Publicatiedatum":"dcterms:issued",
			"Instantie":"dcterms:creator",
			"Titel":"dcterms:title",
			"Zaaknummer":"psi:zaaknummer",
			"Procedure":"psi:procedure",
		}
		
		for key, tagname in pointsOfInterest.items():		
			try:
				parsedDocument[key] = xml.getElementsByTagName(tagname)[0].firstChild.nodeValue
			except:
				pass
			
		try:
			coordinates = RechtspraakParser.getLatLong( parsedDocument["Instantie"] )
			parsedDocument["latitude"] = coordinates["lat"]
			parsedDocument["longtitude"] = coordinates["lng"]
		except Exception as e:
			pass
			
			
		parsedDocument["Wetboeken"] = []
		for reference in xml.getElementsByTagName("dcterms:references"):
			parsedDocument["Wetboeken"].append(reference.firstChild.nodeValue)
		try:
			parsedDocument["inhoudsindicatie"] = xml.getElementsByTagName("inhoudsindicatie")[0].firstChild.firstChild.nodeValue
		except:
			pass
		
		sections = xml.getElementsByTagName("section")
		for section in sections:
			try:
				section.attributes["role"].value
			except:
				continue
				
			sectionContents = []
			for para in section.getElementsByTagName("para"):
				try:
					sectionContents.append(para.firstChild.nodeValue)
				except:
					pass

			parsedDocument[section.attributes["role"].value.capitalize()] = "\n".join(sectionContents)
			
		joinedUitspraak = "\n".join(parsedDocument["uitspraak"])
		if "Beslissing" not in parsedDocument and "De beslissing" in joinedUitspraak:
			parsedDocument["Beslissing"] = joinedUitspraak[joinedUitspraak.index("De beslissing"):]
			
		if "Beslissing" in parsedDocument:
			prosecutionScore = self.classifyJudgement(parsedDocument["Beslissing"])
			if prosecutionScore is not None:
				parsedDocument["ProsecutionScore"] = int(round(prosecutionScore,2)*100)
		
		parsedDocument["contents"] = {"results":{"uitspraak": joinedUitspraak}}
		
		parsedDocument["summary"] = self.generateSummary(parsedDocument)
		
		return parsedDocument
	
	def getWetboekAbbr(self, wetboeken, articles):
		possibleAbbreviations = {}
		letters = list("abcdefghijklmnopqrstuvwxyz")
		stopwords = ["op","de","het","van","bij","een","voor"]
		for wetboek in wetboeken:
			fullAbbreviation = "".join([word[0].lower() for word in wetboek.split(" ")])
			letterAbbreviation = "".join([word[0].lower() for word in wetboek.split(" ") if word[0].lower() in letters])
			noStopWordsAbbreviation = "".join([word[0].lower() for word in wetboek.split(" ") if word[0].lower() in letters and word not in stopwords])
				
			possibleAbbreviations[fullAbbreviation] = wetboek 
			possibleAbbreviations[letterAbbreviation] = wetboek 
			possibleAbbreviations[noStopWordsAbbreviation] = wetboek 

		for a,article in enumerate(articles):
			for abbr,wb in possibleAbbreviations.items():
				if abbr in article.lower():
					articles[a] = re.sub(" "+abbr+" ?", " "+wb+" ", article, flags=re.IGNORECASE)
				
		return articles
			
	@staticmethod
	@persist_to_file("location.json")
	def getLatLong(place):
		mapsUrl = "https://maps.googleapis.com/maps/api/geocode/json?address="+place
		r = requests.get(mapsUrl)
		try:
			return r.json()["results"][0]["geometry"]["location"]
		except:
			return {"lat":None,"lng":None}
	
	def generateSummary(self, document):
		summary = ["Deze rechtzaak is gepubliceerd op %s in de categorie %s." % (document["Publicatiedatum"], document["Rechtsgebieden"])]
		try:
			summary.append( "De instantie was %s." % document["Instantie"])
		except:
			pass
		try:
			summary.append( "De zittingsplaats was %s." % document["Zittingsplaats"])
		except:
			pass
		
		try:
			summary.append( "\n".join(document["Procesverloop"].split("\n")) )
		except:
			pass
		
		try:
			summary.append( "\n".join(document["Beslissing"].split("\n")[:-2]) )
			if document["ProsecutionScore"] > -1:
				summary.append( "De beslissing van dit proces werd beoordeeld met %s punten voor de vervolging." % document["ProsecutionScore"] )
		except:
			pass
		
		articles = self.articleRegex.findall("\n".join(document["uitspraak"]))
		if len(document["Wetboeken"]) > 0:
			summary.append("Dit stuk jurisprudentie refereert naar de volgende wetboeken.")
			for wb in list(set(document["Wetboeken"])):
				summary.append("- %s" % wb)
		
		articles = [a.group(0) for a in self.articleRegex.finditer("\n".join(document["uitspraak"]))]
		
		articles = self.getWetboekAbbr(document["Wetboeken"], articles)
		
		if len(articles) > 0:
			summary.append("Dit stuk jurisprudentie refereert naar de volgende artikelen.")
			for article in list(set(articles))[:3]:
				summary.append("- %s" % article.strip(",. "))
			if len(articles) > 3:
				summary.append("en meer.")
				
		return "\n".join(summary)
			
	def determineDecision(self, document):
		""" Dit is voor de judgement processor. """
		try:
			document["Beslissing"]
		except:
			return False
		
		tagger = nltk.data.load("taggers/alpino_NaiveBayes.pickle")
		dump = open("decisionData.json.comp","a+")
		csv = open("decisionData.csv","a+")
		
		for line in document["Beslissing"].split("\n"):
			if len(line.strip()) < 5:
				continue
			
			print line
			suggested = self.classifyJudgementSentence(line.lower())
			
			# Y = Ja, N = Nee, S = Zegt niks, Q = Quit
			classified_as = raw_input("Duidt deze zin schuldigheid aan? (y/n/s/q) (Press enter to enter suggested: %s) " % suggested)
			if classified_as == "q":
				time.sleep(1)
				exit()
			if classified_as not in "yns" or len(classified_as)==0:
				classified_as = suggested			

			taggedDocument = tagger.tag(line.lower().split(" "))
			decisionData = {"text":taggedDocument,"classified_as":classified_as}
			dump.write( json.dumps( decisionData ) + "\n")
			csv.write( '"%s","%s"\n'.encode("ascii", "ignore") % (line.encode("ascii", "ignore"), classified_as) )
			
	def classifyJudgementSentence(self, sentence):
		s = sentence.lower()
		""" Judgment sentences are can be classified using the following tree:
			vrij <= 0
			|   veroordeelt <= 0
			|   |   verklaart <= 0
			|   |   |   vernietigt <= 0
			|   |   |   |   met <= 0
			|   |   |   |   |   af <= 0: s (409.0/38.0)
			|   |   |   |   |   af > 0: n (10.0/1.0)
			|   |   |   |   met > 0
			|   |   |   |   |   artikel <= 0: s (21.0/2.0)
			|   |   |   |   |   artikel > 0: y (4.0)
			|   |   |   vernietigt > 0: n (14.0/4.0)
			|   |   verklaart > 0
			|   |   |   gegrond <= 0
			|   |   |   |   hun <= 0
			|   |   |   |   |   uitvoerbaar <= 0: y (70.0/13.0)
			|   |   |   |   |   uitvoerbaar > 0: s (3.0)
			|   |   |   |   hun > 0: n (2.0)
			|   |   |   gegrond > 0: n (2.0)
			|   veroordeelt > 0
			|   |   benadeelde <= 0: y (31.0/1.0)
			|   |   benadeelde > 0: s (2.0)
			vrij > 0: n (28.0/2.0)
		
			Returns a float indicating the odds of this sentence indicating succesful prosecution. Will return -1 if this sentence does not indicate any such sentiment.
		"""
		
		if "vrij" in s:
			return (2./30.)
		
		if "veroordeelt" in s:
			if "benadeelde" in s:
				return None
			else:
				return (31./32.)
		if "verklaart" in s:
			if "gegrond" in s:
				return 0.
			if "hun" in s:
				return 0.
			if "uitvoerbaar" in s:
				return None
			return (70./83.)
		
		if "vernietigt" in s:
			return (4./18.)
		
		if "met" in s:
			if "artikel" in s:
				return 1.
			return None
		
		if "af" in s:
			return (1./11.)
		
		return -1	
			
	def classifyJudgement(self, decision):
		""" This classification is based on a J48 tree, tested with a subset of judgements. """
		total = 0
		score = 0
		for line in decision.split("\n"):
			s = self.classifyJudgementSentence(line)
			if s is not None:
				total+=1
				score+=s
		
		try:
			return score/total
		except:
			return None
			
	def filterRechtspraak(self, filename, tokenizer=None, inContentsThreshold=97):
		rechtspraak = json.load(open(filename))
		abstractive, fragment, unlabeled = [],[],[]
		if tokenizer is None:
			tokenizer = string.split
		
		for document in rechtspraak.values():
			title = document["Titel"]
			try:
				contents = tokenizer( " ".join( document["contents"]["results"]["uitspraak"] ).lower() )
			except:
				continue
				
			if None in contents:
				continue
				
			# Check of this the document contains a summary
			try:
				summary = document["Tekstfragment"].lower()
			except:
				unlabeled.append( (0, contents, "", title) )
				continue
			
			summary = tokenizer(summary)
			if len(summary) == 0 or (len(summary) == 1 and len(summary[0]) < 20) :
				unlabeled.append( (0, contents, "", title) )
				continue
			
			percentageInContents = 0
			if len(summary) == 1 and len(contents) == 1:
				if summary[0] in contents[0]:
					percentageInContents = 100
					
			for token in summary:
				if token in contents:
					percentageInContents += (100.0/len(summary))
			
			if percentageInContents > inContentsThreshold: # More then 97% is probably copied directly from the text.
				fragment.append( ( percentageInContents, contents, summary, title ) )
			else:
				pass
				abstractive.append( ( percentageInContents, contents, summary, title ) )
						
		return abstractive, fragment, unlabeled
		
	def filterRechtspraakFolder(self, directory, tokenizer=None, n=100):
		abstractive, fragment, unlabeled = [],[],[]
		
		if tokenizer is None:
			tokens = re.compile("[^\w]+")
			tokenizer = tokens.split
		
		for f in os.listdir(directory)[:n]:
			a, frag, u = self.filterRechtspraak(os.path.join(directory, f), tokenizer)
			#abstractive += a
			fragment += frag
			#unlabeled += u

		#del abstractive
		#del unlabeled
		
		#self.visualizeFilteredRechtspraakElements(fragment)
		
		return abstractive, fragment, unlabeled
		
		abstractive.sort(key=lambda a: a[0])
		fragment.sort(key=lambda a: a[0])

		json.dump(abstractive, open("abstractive.json","w"))
		json.dump(fragment, open("fragment.json","w"))
		json.dump(unlabeled, open("unlabeled.json","w"))
		
	def visualizeFilteredRechtspraakElements(self, data ):
		""" This method will produce a histogram showing the percentage of words with a high TFIDF score. """
		import numpy as np
		import matplotlib.pyplot as plt
		
		documentsContaining = collections.defaultdict(int)
		for d in data:
			content = d[1]
			for word in set(content):
				documentsContaining[word] += 1	
				
		contentHighlyRelevantOccurences, summaryHighlyRelevantOccurences = [],[]
		for document in data:
			percentageInContents, contents, summary = document
			termFrequencies = collections.defaultdict(int)
			for word in contents:
				termFrequencies[word]+=1
				
			contentsResults = {}
			for word in set(contents):
				contentsResults[word] = termFrequencies[word] * math.log(float(len(data))/(documentsContaining[word]+1))
			
			summaryResults = {}
			for word in set(summary):
				summaryResults[word] = termFrequencies[word] * math.log(float(len(data))/(documentsContaining[word]+1))
				
			threshold = 2
			contentHighlyRelevantOccurences.append( round(len([w for w in contentsResults if contentsResults[w] > threshold])/float(len(content))*2,2)/2 )
			summaryHighlyRelevantOccurences.append( round(len([w for w in summaryResults if summaryResults[w] > threshold])/float(len(summary))*2,2)/2 )
			
		del data	
		
		countedContentResults = collections.Counter(contentHighlyRelevantOccurences)
		countedSummaryResults = collections.Counter(summaryHighlyRelevantOccurences)
		precision = 200
		
		labels = [float(n)/precision for n in range(precision)]
		
		ind = np.arange(precision)  # the x locations for the groups
		barsContents = [countedContentResults.get(l,0) for l in labels]
		barsSummary = [countedSummaryResults.get(l,0) for l in labels]
		
		del countedContentResults
		del countedSummaryResults
				
		fig = plt.figure()
		ax = fig.add_subplot(111)
		
		width = 0.35
		ax.set_xlim(-width,len(ind)+width)
		
		ax.bar(ind, barsContents, width)
		ax.bar(ind+width, barsSummary,width,color='red')
		
		plt.xticks(ind, labels, rotation=45)
		plt.show()
				
	
if __name__ == "__main__":
	RP = RechtspraakParser()
	#articles = RP.parseWetboek(sys.argv[1])
	#RP.parseRechtspraak(filename=sys.argv[1])
	
	document = RP.parseXmlRechtspraak(sys.argv[1])
	RP.parseRechtspraak(document=document)
	
	#RP.filterRechtspraakFolder(sys.argv[1])
		
	#articles = RP.downloadWetboeken()
	#documents = RP.parseJson(RP.jsonFileName)
	#RP.parseDocumentDict(dict(documents.items()[:1000]))
	#RP.learnArticles(dict(documents.items()[:100]))
	
