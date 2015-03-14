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

from Yuras.webapp.models.Document import Document

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
			
	def parseRechtspraak(self, filename):
		documents = self.parseJson(filename)
		for _id, document in documents.items():
			try:
				contents = document["contents"]["results"]["uitspraak"]
			except KeyError:
				continue
			d = {"documentid":_id,
				 "_encrypt":False,
				 "contents": "#" + document["Titel"] + "\n" + "\n".join(contents),
				 "category": ", ".join(document["Rechtsgebieden"]),
				 "title": document["Titel"],
				 "published": document["Publicatiedatum"],
				 "document_type":"jurisprudence"
				}
			print json.dumps(d)
	
if __name__ == "__main__":
	RP = RechtspraakParser()
	#articles = RP.parseWetboek(sys.argv[1])
	RP.parseRechtspraak(sys.argv[1])
	#articles = RP.downloadWetboeken()
	#documents = RP.parseJson(RP.jsonFileName)
	#RP.parseDocumentDict(dict(documents.items()[:1000]))
	#RP.learnArticles(dict(documents.items()[:100]))
	