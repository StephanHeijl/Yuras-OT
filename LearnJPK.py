import os, sys, collections,re 
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib

specialCharacters = re.compile("[^ a-z\-]")

stopWords = ['deze', 'en', 'haar', 'is', 'in', 'niet', 'zijn', 'door', 'het', 'heeft', 'van', 'rechtbank', 'te', 'zij', 'bij', 'de', 'dat', 'met', 'worden', 'die', 'voor', 'een', 'op', 'ze', 'of', 'aan']

def tfidfDirectory(d, count_vect=None,tf_transformer=None):
	allContents = []
	target = []
	docs = []

	for directory in os.listdir(d):
		print directory
		directoryContents = [] 

		for file in os.listdir(os.path.join(d,directory)):
			target.append(directory)
			docs.append(file)
			f = open(os.path.join(d,directory,file))
			contents = f.read().lower()
			contents = specialCharacters.sub("", contents)
			contents = " ".join(filter(lambda w: len(w) > 0 and w not in stopWords, contents.split(" ")))

			directoryContents.append(contents)
			allContents.append(contents)

	
	if count_vect == None:
		count_vect = CountVectorizer()
		X_train_counts = count_vect.fit_transform(allContents)
	else:
		X_train_counts = count_vect.transform(allContents)

	if tf_transformer == None:
		tf_transformer = TfidfTransformer(use_idf=True)
		X_train_tfidf = tf_transformer.fit_transform(X_train_counts)
	else:
		X_train_tfidf = tf_transformer.transform(X_train_counts)
		
	return X_train_tfidf, docs, target, count_vect, tf_transformer



X_train_tfidf, docs, target, count_vect, tf_transformer = tfidfDirectory("output-learn")
clf = SGDClassifier(n_iter=100,shuffle=True).fit(X_train_tfidf, target)

# Let's test
X_test_tfidf, docs, target, count_vect, tf_transformer  = tfidfDirectory("output-test",count_vect = count_vect,tf_transformer=tf_transformer)

joblib.dump(clf, "trainedModel.mod")
joblib.dump(clf, "fittedCounter.cnt")
joblib.dump(clf, "fittedTransformer.trf")
predicted = clf.predict(X_test_tfidf)
correct = 0
for doc, category, t in zip(docs, predicted, target):
	if category == t:
		correct += 1
	print("\t".join([str(s) for s in [doc,category, t, int(category == t)]]))
	
print float(correct)/float(len(target)) * 100