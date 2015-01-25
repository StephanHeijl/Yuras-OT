import json, os, argparse, collections, re, math

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB,MultinomialNB,BernoulliNB

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
				
				if len(self.stopWords) > 0:
					for sw in self.stopWords:
						value = value.replace(sw, "")
				categorizedData[strippedKey].append(value)
				
				
		self.categorizedData = categorizedData
		
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
	
	def processDocuments(self, data):
		notwords = re.compile("[^a-z]")
		allDocumentWords = []
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
			tfidf = TfidfVectorizer()
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
			print "%s out of %s" % (i,x)
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

			#self.classifier = SGDClassifier(shuffle=True, n_jobs=-1, penalty='elasticnet', n_iter=math.ceil(10**6/(len(self.categorizedData.values())*(1-(1./x)))) )
			self.classifier = classifier
			classifier = self.teachMachine(trainDocuments, trainCategories)

			predictedTest = classifier.predict(testDocuments)

			print metrics.f1_score(testCategories, predictedTest, average='weighted'), metrics.accuracy_score(testCategories, predictedTest)
			
	def fullTraining(self):
		print "Performing a full training."
		trainDocuments, trainCategories = self.processDocuments(self.categorizedData)
		self.classifier = SGDClassifier(shuffle=True, n_jobs=-1, penalty='elasticnet', n_iter=1000 )
		classifier = self.teachMachine(trainDocuments, trainCategories)
		
		with open("Classifier.cpic","wb") as classifierStorage:
			pickle.dump(classifier, classifierStorage)
	
if __name__ == "__main__":
	lm = LearnModule()
	args = vars( lm.argparser.parse_args() )
	if "stopwords" in args:
		lm.getStopWords(args.get("stopwords",""))
	
	lm.analyzeJSON(args.get("in", None))
	#lm.fullTraining()
	
	print "Starting"
	clfs = [
		SVC(kernel="rbf", gamma=0.0),
		SVC(kernel="rbf", gamma=1.0),
		SVC(kernel="rbf", gamma=5.0),
		SVC(kernel="rbf", gamma=10.0),
		SVC(kernel="poly", gamma=0.0),
		SVC(kernel="poly", gamma=1.0),
		SVC(kernel="poly", gamma=5.0),
		SVC(kernel="poly", gamma=10.0),
		SVC(kernel="sigmoid", gamma=0.0),
		SVC(kernel="sigmoid", gamma=1.0),
		SVC(kernel="sigmoid", gamma=5.0),
		SVC(kernel="sigmoid", gamma=10.0),
		SGDClassifier(shuffle=True,loss='perceptron',alpha=0.0001,n_iter=100),
		SGDClassifier(shuffle=True,loss='perceptron',alpha=0.001,n_iter=100),
		SGDClassifier(shuffle=True,loss='perceptron',alpha=0.01,n_iter=100),
		SGDClassifier(shuffle=True,loss='hinge',alpha=0.0001,n_iter=100),
		SGDClassifier(shuffle=True,loss='hinge',alpha=0.001,n_iter=100),
		SGDClassifier(shuffle=True,loss='hinge',alpha=0.01,n_iter=100),
		SGDClassifier(shuffle=True,loss='log',alpha=0.0001,n_iter=100),
		SGDClassifier(shuffle=True,loss='log',alpha=0.001,n_iter=100),
		SGDClassifier(shuffle=True,loss='log',alpha=0.01,n_iter=100),
		MultinomialNB(alpha=0.1),
		MultinomialNB(alpha=1.0),
		MultinomialNB(alpha=10.0),
		MultinomialNB(alpha=100.0)
	]
	
	for clf in clfs:
		print repr(clf)
		lm.xfoldMachine(10, classifier=clf)
	