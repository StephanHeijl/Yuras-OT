#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, os, pprint, numpy, re, math, operator, collections, requests, sys
from Yuras.common.Config import Config

from sklearn.multiclass import OneVsRestClassifier,OneVsOneClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from xml.dom.minidom import parse, parseString

#from Yuras.webapp.models.Document import Document

class RechtspraakParser():
	def __init__(self):
		self.rechtspraakFolder = Config().WebAppDirectory+"/../../rechtspraak"
		self.jsonFileName = "10krecords.json"
		self.delimitor = re.compile("[^a-z]*")
		
	def parseJson(self, filename):
		path = os.path.join(self.rechtspraakFolder,filename)
		documents = json.load(open(path))
		return documents		

	def learnArticles(self, documents):
		# This regex matches everything after the initial article number.
		articleRegex = re.compile(r"([Aa]rtikel(en)?|art\.) ((\d+|[IVX]+)([:\.]\d+)?([a-z]+)?( en |, ?)?)+ ?(([etdvzan][ewic][a-z]+?((d|st)e[^a-z]))?(lid|paragraaf|volzin)( \d+)?([, ])*)*((van|het|de|Wet|wet) )*( ?(([A-Z]([A-Z]{1,4}|[a-z]{1,2}))[^\w]) ?(\d{4})?|([\w\-]+ ?)+ ?(\d{4})?)")	
		articles = {}
		
		for _id,document in documents.items():
			contents = self.getDocumentContents(document)
			if contents is None:
				continue
				
			for article in articleRegex.finditer( contents ):
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
		$ for file in rechtspraak/results/*.json; do echo "$file" | cut -d "/" -f 2- | xargs python -m Yuras.machine_learning_ng.RechtspraakParser | mongoimport --db "Yuras1" -c documents ; done
		
		"""
		if filename is not None:
			documents = self.parseJson(filename)
		
		if document is not None:
			documents = {document["id"]:document}
			
		for _id, document in documents.items():
			print _id, document.keys()
			try:
				contents = document["contents"]["results"]["uitspraak"]
				case_id = document["contents"]["results"]["zaaknummer"]
			except KeyError as e:
				print e
				continue
				
			content_indication,procedures = None,None
			try:
				content_indication = document["Tekstfragment"]
				procedures = document["proceduresoorten"]
			except:
				pass
				
			d = {"documentid":_id,
				 "_encrypt":False,
				 "contents": "#" + document["Titel"] + "\n" + "\n".join(contents),
				 "category": ", ".join(document["Rechtsgebieden"]).replace(" ","_"),
				 "title": document["Titel"],
				 "published": document["Publicatiedatum"],
				 "document_type":"jurisprudence",
				 "source":document["Titel"].split(",")[0].replace(" ","_"),
				 "procedures": procedures,
				 "case_id": case_id,
				 "content_indication": content_indication
				}
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
		
		try:
			parsedDocument["Publicatiedatum"] = xml.getElementsByTagName("dcterms:issued")[0].firstChild.nodeValue
		except:
			pass
		try:
			parsedDocument["Rechtsgebieden"] = xml.getElementsByTagName("dcterms:subject")[0].firstChild.nodeValue
		except:
			pass
		try:
			parsedDocument["zaaknummer"] = xml.getElementsByTagName("psi:zaaknummer")[0].firstChild.nodeValue
		except:
			pass
		try:
			parsedDocument["bijzondere_kenmerken"] = xml.getElementsByTagName("dcterms:subject")[0].firstChild.nodeValue
		except:
			pass		
		try:
			parsedDocument["inhoudsindicatie"] = xml.getElementsByTagName("inhoudsindicatie")[0].firstChild.firstChild.nodeValue
		except:
			pass
		
		parsedDocument["contents"] = {"results":{"uitspraak": "\n".join(parsedDocument["uitspraak"])}}
		
		return parsedDocument
			
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
	
	xml = RP.parseXmlRechtspraak(sys.argv[1])
	RP.parseRechtspraak(document=xml)
	
	#RP.filterRechtspraakFolder(sys.argv[1])
		
	#articles = RP.downloadWetboeken()
	#documents = RP.parseJson(RP.jsonFileName)
	#RP.parseDocumentDict(dict(documents.items()[:1000]))
	#RP.learnArticles(dict(documents.items()[:100]))
	
