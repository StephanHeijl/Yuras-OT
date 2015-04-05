import json, os, argparse, collections, re, math, pprint

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.svm import SVC
from sklearn import metrics

import cPickle as pickle

class LearnModule():
	def __init__(self):
		self.categories = []
		self.files = []
		self.mappedData = {}
		self.argparser = argparse.ArgumentParser(description='Learn based on a JSON file')
		self.parseArguments()
		self.categorizedData = None
		self.stopWords = []
		self.tfidf = None
		
		"""
			Regex explained:
			
				((eer|twee|derd|vier|vijf|zes|zeven|acht|negen)(de|ste) lid van )? 						# Xde lid/paragraaf van... (Optional)
				[aA]rtikel(en)? \d+\w?(:\d+)? 															# Article number and suffix
				((.{1,3}(eer|twee|derd|vier|vijf|zes|zeven|acht|negen)(de|ste) lid)|.{1,3}lid (\d+)?)? 	# Xde lid/paragraaf van or lid/paragraaf X van (Optional)
				([^\.\n]{,10}(RV|BW|SV|Sr|PBW|EVRM))?													# Abbreviation suffix (Optional)
				[, ]?(( ?van ?)?( ?de ?)?( ?het ?)?([A-Z][A-Za-z\-]+ ?(([a-z\-]+)? )?)+)?				# Article book or source (Optional)
		
		"""
		
		articleRegexString = "(ECLI:[\w:]+|BNB \d+/\d+)|((eer|twee|derd|vier|vijf|zes|zeven|acht|negen)(de|ste) (lid|paragraaf) van )?[Aa]rtikel(en)? \d+\w?(:\d+)?((.{1,3}(eer|twee|derd|vier|vijf|zes|zeven|acht|negen)(de|ste) lid)|.{1,3}(lid|paragraaf) (\d+)?)?([^\.\n]{,10}(RV|BW|SV|Sr|PBW|EVRM))?[, ]?(( ?van ?)?( ?de ?)?( ?het ?)?([A-Z][A-Za-z\-]+ ?(([a-z\-]+)? )?)+)?"
		self.articleRegex = re.compile(articleRegexString)
			
	def parseArguments(self):
		self.argparser.add_argument("--in", type=str, help="The directory to walk.", required=True)
		self.argparser.add_argument("--stopwords", type=str, help="A file containing list of stopwords.")
		
	def analyzeJSON(self, path):
		data = json.load(open(path))
		flattenedData = self.__flatten(data)
		categorizedData = {}
		
		for key, value in flattenedData.items():
			strippedKey = key.split("_")[2]
			if ".html" in key:
				if strippedKey not in categorizedData:
					categorizedData[strippedKey] = []
				
				categorizedData[strippedKey].append(value)
		
		self.categorizedData = categorizedData
		
	def JSONtoCSV(self, path):
		data = json.load(open(path))
		flattenedData = self.__flatten(data)
		categorizedData = {}
		
		for key, value in flattenedData.items()[:1000]:
			cat = key.split("_")[2]
			if cat == "strafrecht":
				cat+= "-" + key.split("_")[3]
			categorizedData[key.split("_")[-1]] = (self.getArticlesFromContent(value), cat)
					
		articles = []
		for ararr in categorizedData.values():
			articles += ararr[0]
		articles = list(set(articles))
		
		print ",".join(["\""+s+"\"" for s in articles+["category"]])
		for t, (a, c) in categorizedData.items():
			data = []
			for ai in articles:
				if ai in a:
					data.append("\"y\"")
				else:
					data.append("\"n\"")
			print ",".join(data + ["\""+c+"\""])
		
		
	def __flatten(self,d, parent_key='', sep='_'):
		items = []
		for k, v in d.items():
			new_key = parent_key + sep + k if parent_key else k
			if isinstance(v, collections.MutableMapping):
				items.extend(self.__flatten(v, new_key, sep=sep).items())
			else:
				items.append((new_key, v))
		return dict(items)
	
	def getStopWords(self, path):
		with open(path) as stopWords:
			self.stopWords = stopWords.read().split("\n")
			
	def tokenizer(self, string):
		tokens = re.split("[^\w]", string)
		for sw in self.stopWords:
			tokens = filter(lambda t: t!=sw, tokens)
		
		articles = self.getArticlesFromContent(string)
		print articles
		tokens += articles*50
		return tokens
	
	def getArticlesFromContent(self, string):
		results = []
		
		for result in self.articleRegex.finditer(string):
			results.append(result.group(0).strip(",. "))
			
		filteredResults = [j for i, j in enumerate(results) if all(j not in k for k in results[i + 1:])]
		return filteredResults
		
	def processDocuments(self, data):
		allDocuments = []
		categoryList = []
		
		if isinstance(data, dict):
			data = data.items()
		
		for category, documents in data:
			for document in documents:
				if "binnen het geselecteerde document" in document or len(document) < 10:
					continue
				
				categoryList.append(category)
				allDocuments.append(document.lower())
				
		if self.tfidf is None:
			#tfidf = TfidfVectorizer(strip_accents='ascii', tokenizer=self.tokenizer)
			tfidf = TfidfVectorizer(stop_words=self.stopWords,analyzer="char", norm=None, ngram_range=(1,2))
			self.tfidf = tfidf
			return tfidf.fit_transform(allDocuments), categoryList
		else:
			return self.tfidf.transform(allDocuments), categoryList
	
	def teachMachine(self, targetDocuments=None, targetCategories=None):
		if targetDocuments is None and targetCategories is None:
			targetDocuments, targetCategories = self.processDocuments(self.categorizedData)
		
		try:
			return self.classifier.fit(targetDocuments,targetCategories)
		except:
			return self.classifier.fit(targetDocuments.toarray(),targetCategories)
	
	def __uniqify(self, seq, idfun=None): 
	   if idfun is None:
		   def idfun(x): return x
	   seen = {}
	   result = []
	   for item in seq:
		   marker = idfun(item)
		   if marker in seen: continue
		   seen[marker] = 1
		   result.append(item)
	   return result
	
	def xfoldMachine(self, x, classifier=None):
		for i in range(x):
			print "%s/%s" % (i,x)
			trainData = {}
			testData = {}
			for category in self.categorizedData:
				testData[category] = []
				trainData[category] = []

				documents = self.categorizedData[category]
				chunkSize = int(math.ceil(float(len(documents)) / float(x)))

				for ii in range(x):
					if ii == i:
						testData[category] += documents[chunkSize*ii:chunkSize*(ii+1)]
					else:
						trainData[category] += documents[chunkSize*ii:chunkSize*(ii+1)]

			testDocuments, testCategories = self.processDocuments(testData)
			trainDocuments, trainCategories = self.processDocuments(trainData)

			labels = self.__uniqify(testCategories)

			self.classifier = SVC(kernel="sigmoid", gamma=3.5, C=1)
			classifier = self.teachMachine(trainDocuments, trainCategories)

			predictedTest = classifier.predict(testDocuments)

			print metrics.classification_report(testCategories, predictedTest)
			print
			pprint.pprint(metrics.confusion_matrix(testCategories, predictedTest).tolist(),width=150)
			print
			print metrics.f1_score(testCategories, predictedTest, average='weighted'), metrics.accuracy_score(testCategories, predictedTest)
			print
			
	def fullTraining(self):
		print "Performing a full training."
		trainDocuments, trainCategories = self.processDocuments(self.categorizedData)
		self.classifier = SVC(kernel="sigmoid", gamma=3.5, C=1)
		classifier = self.teachMachine(trainDocuments, trainCategories)
		
		with open("Classifier.cpic","wb") as classifierStorage:
			pickle.dump(classifier, classifierStorage)
			
		with open("Vectorizer.cpic","wb") as vectorizerStorage:
			pickle.dump(self.tfidf, vectorizerStorage)
			
	
if __name__ == "__main__":
	lm = LearnModule()
	args = vars( lm.argparser.parse_args() )
	if "stopwords" in args:
		lm.getStopWords(args.get("stopwords",""))
	
	lm.JSONtoCSV(args.get("in", None))
	#lm.analyzeJSON(args.get("in", None))
	#lm.fullTraining()
	#lm.xfoldMachine(10, classifier=None)
	