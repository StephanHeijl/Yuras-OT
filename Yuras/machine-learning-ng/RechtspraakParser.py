import json, os, pprint, numpy, re, math, operator, collections
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
		self.rechtspraakFolder = Config().WebAppDirectory+"/../../rechtspraak/ImportIOFormat"
		self.jsonFileName = "10krecords.json"
		self.delimitor = re.compile("[^a-z]*")
		
	def parseJson(self, filename):
		path = os.path.join(self.rechtspraakFolder,filename)
		documents = json.load(open(path))
		return documents
		
	def parseDocumentDict(self, documents):
		results = []
		ids = []
		
		trainingChunk = int(len(documents)*0.9)
		
		trainingDocuments = dict(documents.items()[:trainingChunk])
		testingDocuments = dict(documents.items()[trainingChunk:])
		
		categories = self.getDocumentIndicatorWords(trainingDocuments,n=3)
		
		for _id in categories.keys()[:]:
			document = trainingDocuments[_id]
			contents = self.getDocumentContents(document)
			if contents is not None:
				results.append( contents )
				ids.append(_id)
			else:
				del categories[_id]
			
		vectorizer = TfidfVectorizer()
		X = vectorizer.fit_transform(results)
		Y = categories.values()
		
		#Y = MultiLabelBinarizer().fit_transform(Y)
				
		classifier = LinearSVC()
		classifier.fit(X,Y)
		
		for _id,document in testingDocuments.items():
			contents = self.getDocumentContents(document)
			if contents is None:
				continue
			v = vectorizer.transform([contents])
			p = classifier.predict(v)[0]
			
			overlap = set(p).intersection(set( self.delimitor.split(contents.lower()) ))
			if len(p) == 0:
				continue
				
			print _id, len(p), len(overlap), overlap				
			if len(overlap) > 0:
				print "\t",overlap
			else:
				print "\t",p

	def getDocumentContents(self, document):
		try:
			return " ".join( document["contents"]["results"][0]["uitspraak"] )
		except:
			return None
		
	def getDocumentIndicatorWords(self,documents, n=5):
		indicators = {}
		words = set()
		stopwords = Document.getStopwords()
		
		for _id,document in documents.items():
			indicators[_id] = {}
			try: 
				indicators[_id]["content"] = self.delimitor.split(
					document["contents"]["results"][0]["inhoudsindicatie"].lower()
				)
			except:
				del indicators[_id]
				continue
				
			for term in indicators[_id]["content"][:]:
				if term in stopwords:
					indicators[_id]["content"].remove(term)
				
			indicators[_id]["term_frequencies"] = {}
				
			for word in indicators[_id]["content"]:
				words.add(word)
				indicators[_id]["term_frequencies"][word] = indicators[_id]["content"].count(word)
				
		words = list(words)
		indlen = len(indicators)
		idfs = {}
		for word in words:
			df = 0
			for doc in indicators.values():
				if word in doc["content"]:
					df+=1
			idf = 1+ math.log(indlen/df)
			idfs[word] = idf
			
		categories = {}
		for _id,document in indicators.items():
			tfidfs = {}
			for term, freq in indicators[_id]["term_frequencies"].items():
				tfidfs[term] = freq*idfs[term]
			
			categories[_id] = []
			for t,s in sorted(tfidfs.items(), key=lambda t: t[1], reverse=True)[:n]:
				#print "\t %s - %s" % (t,round(s,2))
				categories[_id].append(t)
				
		return categories
	
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
				
	
if __name__ == "__main__":
	RP = RechtspraakParser()
	documents = RP.parseJson(RP.jsonFileName)
	#RP.parseDocumentDict(dict(documents.items()[:10000]))
	RP.learnArticles(dict(documents.items()[:100]))