from nose import with_setup
from collections import defaultdict

from Yuras.common.Singleton import Singleton
from Yuras.common.Config import Config
import Yuras.webapp.models.PublicDocument

import json, re

class SpellingEngine(Singleton):
	""" A spelling correction engine for queries. Adapted from http://norvig.com/spell-correct.html """
	def __init__(self):
		self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
		if self.instantiated:
			return
		self.model = None
		
	def trainWithDatabaseDocuments(self, limit=None):
		""" Trains the spelling engine with Documents, using their built in wordcount function. """
		documents = Yuras.webapp.models.PublicDocument.PublicDocument().matchObjects({}, limit=limit)
		model = defaultdict(lambda: 1)
		for d in documents:
			words, wordcount = d.plainWordCount(filterStopwords=False)
			for f, c in wordcount.items():
				model[f] += c
		
		return model			
	
	def train(self,features):
		""" Used to train the model with a list of features. """
		model = defaultdict(lambda: 1)
		for f in features:
			model[f.lower()] += 1
		return model
	
	def edits1(self,word):
		splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
		deletes	= [a + b[1:] for a, b in splits if b]
		transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
		replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
		inserts	= [a + c + b for a, b in splits for c in self.alphabet]
		return set(deletes + transposes + replaces + inserts)

	def known_edits2(self,word):
		return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.model)
	
	def known(self,words): return set(w for w in words if w in self.model)

	def correct(self,word):
		word = word.lower()
		candidates = self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word) or [word]
		return max(candidates, key=self.model.get)
	
############################# TEST SPELLINGENGINE #############################

###############################################################################

def setup_func():
	global se
	se = SpellingEngine()

def teardown_func():
	global se
	del se

@with_setup(setup_func, teardown_func)
def test_se_init():
	assert isinstance(se, SpellingEngine)
	
@with_setup(setup_func, teardown_func)
def test_se_trainWithDatabaseDocuments():
	model = se.trainWithDatabaseDocuments(limit=5)
	assert model[model.keys()[0]] > 1
	assert model["de"] > 1
	assert model["flurgeldurk"] == 1 # Test TF smoothing. If 'flurgeldurk' is an actual word that occurs in your featureset, this will be invalid.
	assert model[" "] == 1 # Your featureset should not contain spaces.
	
@with_setup(setup_func, teardown_func)
def test_se_known():
	model = se.trainWithDatabaseDocuments(limit=5)
	se.model = model
	assert se.known(["de","het","een","flurgeldurk"]) == set(["het","de","een"])
	
@with_setup(setup_func, teardown_func)
def test_se_correct():
	model = se.trainWithDatabaseDocuments(limit=25)
	se.model = model
	assert se.correct("starfrecht") == "strafrecht"
	assert se.correct("hfo") == "hof"
	assert se.correct("hoeg") == "hoge"
	assert se.correct("regtbank") == "rechtbank"
	assert se.correct("flurgeldurk") == "flurgeldurk" # Test negative spell correction