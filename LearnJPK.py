import os, re
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn import metrics

import numpy as np
from sklearn.externals import joblib

from pprint import pprint as pp

specialCharacters = re.compile("[^ a-z\-]")

stopWords = []

def custom_tokenizer(string):
	tokens = []
	words = string.split(" ")
	tokens+=words
	tokens = tuple(tokens)
	return tokens


def tfidfDirectory(d, count_vect=None,tf_transformer=None):
	allContents = []
	target = []
	docs = []

	for directory in os.listdir(d):
		print directory

		for file in os.listdir(os.path.join(d,directory)):
			print "\t",file
			target.append(directory)
			docs.append(file)
			f = open(os.path.join(d,directory,file))
			contents = f.read().lower()

			if "Dit document bevat privacygevoelige informatie en is om die reden alleen toegankelijk voor advocaten en andere juridische professionals." in contents:
				continue

			contents = specialCharacters.sub("", contents)
			contents = " ".join(filter(lambda w: len(w) > 0 and w not in stopWords, contents.split(" ")))

			allContents.append(contents)

	if count_vect == None:
		count_vect = CountVectorizer(tokenizer=custom_tokenizer)
		X_train_counts = count_vect.fit_transform(allContents)
	else:
		X_train_counts = count_vect.transform(allContents)

	if tf_transformer == None:
		tf_transformer = TfidfTransformer(use_idf=True)
		X_train_tfidf = tf_transformer.fit_transform(X_train_counts)
	else:
		X_train_tfidf = tf_transformer.transform(X_train_counts)

	return X_train_tfidf, docs, target, count_vect, tf_transformer



X_train_tfidf, docs, target_train, count_vect, tf_transformer = tfidfDirectory("output-learn")

#joblib.dump(count_vect, "trainedModels/fittedCounter.cnt")
#joblib.dump(tf_transformer, "trainedModels/fittedTransformer.trf")

clf = GaussianNB().fit(X_train_tfidf.toarray(), target_train)

#joblib.dump(clf, "trainedModels/trainedModel.mod")

# Let's test
X_test_tfidf, docs, target_test, count_vect, tf_transformer  = tfidfDirectory("output-test",count_vect = count_vect,tf_transformer=tf_transformer)

predicted_test = clf.predict(X_test_tfidf.toarray())

#correct = 0
#for doc, category, t in zip(docs, predicted_test, target):
#	if category == t:
#		correct += 1
#	print("\t".join([str(s) for s in [doc,category, t, int(category == t)]]))

#print float(correct)/float(len(target)) * 100

print('Prediction accuracy for the test dataset')
print('{:.2%}\n'.format(metrics.accuracy_score( predicted_test, target_test )))

print('Classification report')
report = metrics.classification_report(predicted_test, target_test)
print(report)
