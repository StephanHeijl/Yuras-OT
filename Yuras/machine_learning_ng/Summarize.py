from Yuras.machine_learning_ng.RechtspraakParser import RechtspraakParser
import re,sys,pprint,collections,math,itertools

import numpy as np
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import SGDClassifier as Classifier
#from sklearn.naive_bayes import GaussianNB as Classifier
from sklearn.metrics import matthews_corrcoef,classification_report,confusion_matrix
from sklearn.cross_validation import KFold

class Summarizer():
	def __init__(self):
		pass
	
	def trainSummarizer(self):
		pass
	
	def summarize(self, text):
		pass
	
class SummarizeFragment(Summarizer):
	def __init__(self):
		self.model = None
		self.lidwoordRegex = re.compile("de|het|een")
		
	def getPredictionSet(self, data):
		contentHighlyRelevantOccurences = {}
		
		threshold = 2
		
		for document in data:
			p, contents, summary = document
			termFrequencies = collections.defaultdict(int)
			
			for sentence in contents[:]:
				if len(sentence) < 3:
					contents.remove(sentence)
				
							
			for sentence in contents:
				for word in sentence.split():
					termFrequencies[word]+=1
					
			contentsResults = {}
			for sentence in contents:
				for word in set(sentence.split()):
					contentsResults[word] = termFrequencies[word] * math.log(float(len(data))/(self.documentsContaining[word]+1))
			
			for sentence in contents:
				score = 0
				words = sentence.split()
				for word in words:
					if contentsResults[word]>threshold:
						score += 1
				senlen = len(words)+1
				
				lidwoorden = self.lidwoordRegex.findall(sentence)
				contentHighlyRelevantOccurences[sentence] = ([float(score), senlen, len(lidwoorden)])
		
		return contentHighlyRelevantOccurences
	
	def getDataSet(self, data):
		documentsContaining = collections.defaultdict(int)
		for d in data:
			try:
				content = d[1]
			except:
				continue
			for sentence in content:
				for word in set(sentence.split()):
					documentsContaining[word] += 1	
				
		contentHighlyRelevantOccurences, summaryHighlyRelevantOccurences = [],[]
		
		threshold = 2
		contentTermFrequencies = collections.defaultdict(int)
		summaryTermFrequencies = collections.defaultdict(int)
		
		for document in data:
			percentageInContents, contents, summary = document
			termFrequencies = collections.defaultdict(int)
			
			for sentence in contents[:]:
				if sentence in summary or len(sentence.split()) < 1:
					contents.remove(sentence)
							
			for sentence in contents:
				for word in sentence.split():
					termFrequencies[word]+=1
					contentTermFrequencies[word]+=1
					
			for sentence in summary[:]:
				if len(sentence.split()) == 0:
					summary.remove(sentence)
					continue
				for word in sentence.split():	
					summaryTermFrequencies[word]+=1
				
			contentsResults = {}
			for sentence in contents:
				for word in set(sentence.split()):
					contentsResults[word] = termFrequencies[word] * math.log(float(len(data))/(documentsContaining[word]+1))
			
			summaryResults = {}
			for sentence in summary:
				for word in set(sentence.split()):
					summaryResults[word] = termFrequencies[word] * math.log(float(len(data))/(documentsContaining[word]+1))
			
			for sentence in contents:
				score = 0
				words = sentence.split()
				for word in words:
					if contentsResults[word]>threshold:
						score += 1
				senlen = len(words)+1
				
				lidwoorden = self.lidwoordRegex.findall(sentence)
				contentHighlyRelevantOccurences.append([float(score), senlen, len(lidwoorden)])
				
			for sentence in summary:
				score = 0
				words = sentence.split()
				for word in words:
					if summaryResults[word]>threshold:
						score += 1
				
				senlen = len(words)+1
				
				lidwoorden = self.lidwoordRegex.findall(sentence)
				summaryHighlyRelevantOccurences.append([float(score), senlen, len(lidwoorden)])
		
		#self.calculateTermFrequencyDifferences(contentTermFrequencies, summaryTermFrequencies)
		#exit()
			
		#pprint.pprint(contentHighlyRelevantOccurences[:10])
		#pprint.pprint(summaryHighlyRelevantOccurences[:10])
		
		self.documentsContaining = documentsContaining
		return contentHighlyRelevantOccurences, summaryHighlyRelevantOccurences
	
	def calculateTermFrequencyDifferences(self, contentTermFrequencies, summaryTermFrequencies):
		# Normalize the term frequencies
		#avgContentFrequency = sum(contentTermFrequencies.values())/float(len(contentTermFrequencies))
		#avgSummaryFrequency = sum(summaryTermFrequencies.values())/float(len(summaryTermFrequencies))
		#ratio = avgContentFrequency/avgSummaryFrequency
		
		ratio = contentTermFrequencies["de"] / float(summaryTermFrequencies["de"])
		print ratio
		
		tfDifferences = {}
		
		for key in contentTermFrequencies.keys():
			#print contentTermFrequencies[key]/ratio, contentTermFrequencies[key], summaryTermFrequencies[key], (contentTermFrequencies[key]/ratio) - summaryTermFrequencies[key]
			tfDifferences[key] = (contentTermFrequencies[key]/ratio) - summaryTermFrequencies[key]
			
		print "|".join([w[0] for w in sorted(tfDifferences.items(), key=lambda x: x[1])[-100:]])
		
	
	def visualizeOccurences(self, *args):
		import numpy as np
		import matplotlib.pyplot as plt
		from mpl_toolkits.mplot3d import Axes3D
		x = [o[1]*10 for o in itertools.chain(*args)]
		y = [o[0]*3 for o in itertools.chain(*args)]
		z = [o[2]*10 for o in itertools.chain(*args)]
		colornames = ['blue','red','green','yellow']
		colors = []
		for a,arg in enumerate(args):
			colors += [colornames[a] for c in arg]
		
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		
		plt.scatter(x, y, zs=z, c=colors)
		#plt.ylim(0,max(y)+1)
		#plt.xlim(0,max(x)+1)
		
		ax.set_ylim(0,100)
		ax.set_zlim(0,300)
		ax.set_xlim(0,1000)
		plt.show()
		#plt.savefig("results.png", dpi=1000)
	
	def trainSummarizer(self, X, y):
		#clf = SGDClassifier(n_jobs=-1,n_iter=1, shuffle=True)
		clf = Classifier()
		#rbf_feature = RBFSampler(gamma=2000, random_state=1)
		#X_features = rbf_feature.fit_transform(X)
		clf.fit(X, y )		
		self.model = clf
		#self.rbf_feature = rbf_feature
	
	def testSummarizer(self,X_test,y_true ):
		y_pred = []
		
		#X_features = self.rbf_feature.transform(X_test)
		
		for x in X_test:
			prediction = self.model.predict(x)[0]
			y_pred.append(prediction)
						
		mcc = matthews_corrcoef(y_true, y_pred)
		print classification_report(y_true, y_pred)
		print confusion_matrix(y_true, y_pred)
		print mcc
		return mcc
	
	
if __name__ == "__main__":
	RP = RechtspraakParser()
	s = SummarizeFragment()
	
	sentenceRegex = re.compile("\.\s*(?!\d)")
	n = 100
	abstractive, fragments, unlabeled = RP.filterRechtspraakFolder(sys.argv[1], n=n, tokenizer=sentenceRegex.split)
	contentHighlyRelevantOccurences, summaryHighlyRelevantOccurences = s.getDataSet(fragments)
	
	#print unlabeled
	unlabeledSet = s.getPredictionSet(unlabeled)
	
	#s.visualizeOccurences(contentHighlyRelevantOccurences, summaryHighlyRelevantOccurences)
	#s.visualizeOccurences(contentHighlyRelevantOccurences[:1000], summaryHighlyRelevantOccurences[:1000])
	#exit()
	
	X = np.asarray( contentHighlyRelevantOccurences + summaryHighlyRelevantOccurences)
	y = np.asarray(["content" for c in contentHighlyRelevantOccurences] + ["summary" for su in summaryHighlyRelevantOccurences] )
	
	kf = KFold(len(X), n_folds=10,shuffle=True)
	mcc = []
	for train, test in kf:
		X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
		s.trainSummarizer( X_train, y_train )
		mcc.append( s.testSummarizer( X_test , y_test ) )
	
	print sum(mcc) / len(mcc)
	"""
	summaries = []
	contents = []
	for x in unlabeledSet.values():
		#print sentence
		p = s.model.predict(s.rbf_feature.transform(x))
		if p[0] == "content":
			contents.append(1)
		else:
			summaries.append(1)
			
	print len(summaries),len(contents)
	#pprint.pprint(summaries)
	
	s.trainSummarizer( X, y )
	summaries = []
	contents = []
	#X_values = s.rbf_feature.transform(unlabeledSet.values())
	for sentence,values in unlabeledSet.items():
		#print sentence
		p = s.model.predict(s.rbf_feature.transform(values))
		if p[0] == "content":
			contents.append(sentence)
		else:
			summaries.append(sentence)
	
	print len(summaries),len(contents)
	pprint.pprint(summaries)
	
"""