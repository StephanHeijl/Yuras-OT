from nose import with_setup
from collections import defaultdict

from Yuras.common.Singleton import Singleton
from Yuras.common.Config import Config
from Yuras.webapp.models.PublicDocument import PublicDocument as Document

import json, re
		
class ThesaurusEngine(Singleton):
	def __init__(self):
		self.words = []
		self.thesaurus = defaultdict(set)
	
	def parseOpentaalThesaurus(self, thesaurus):
		""" Parses the OpenTaal Thesaurus file format.
		This will accept a string containing the OpenTaal Thesaurus and output a dictionary 
		with every word as a key and each of its """
		
		for line in thesaurus.split("\n"):
			words = line.split(";")
			for word in words:
				synonyms = set([ w.decode("ascii", errors="ignore") for w in words if w != word])
				word = word.decode("ascii", errors="ignore")
				self.thesaurus[word] = self.thesaurus[word].union( synonyms )
				
		for word in self.thesaurus.keys():
			self.thesaurus[word] = list(self.thesaurus[word])
			
		self.words = self.thesaurus.keys()
		return True	
	
	def getSynonyms(self, word):
		return self.thesaurus.get(word, [])
	
############################# TEST THESAURUSENGINE ############################

def setup_func():
	global te, thesaurus
	with open("thesaurus.txt") as thesaurusFile:
		thesaurus = thesaurusFile.read()
	te = ThesaurusEngine()

def teardown_func():
	global te,thesaurus
	del te
	del thesaurus

@with_setup(setup_func, teardown_func)
def test_te_init():
	assert isinstance(te, ThesaurusEngine)
	
@with_setup(setup_func, teardown_func)
def test_te_parseOpentaalThesaurus():
	assert te.parseOpentaalThesaurus(thesaurus)
	assert len(te.thesaurus)>0
	assert len(te.words)>0
	
@with_setup(setup_func, teardown_func)
def test_te_getSynonyms():
	te.parseOpentaalThesaurus(thesaurus)
	# Sort results and expected values because order does not matter for this test
	assert sorted(te.getSynonyms("toelaatbaar")) == sorted(["toegestaan","geoorloofd","duldbaar"])
	assert sorted(te.getSynonyms("hangwerk")) == sorted(["hangconstructie"])
	assert sorted(te.getSynonyms("Jezus")) == sorted(["Jezus Christus", "Messias", "Christus"])
	assert sorted(te.getSynonyms("Christus")) == sorted(["Jezus Christus", "Messias", "Jezus"])
	
###############################################################################

class SpellingEngine(Singleton):
	""" A spelling correction engine for queries. Adapted from http://norvig.com/spell-correct.html """
	def __init__(self):
		self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
		self.model = None
		
	def trainWithDatabaseDocuments(self, limit=None):
		""" Trains the spelling engine with Documents, using their built in wordcount function. """
		documents = Document().matchObjects({}, limit=limit)
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
	
	
###############################################################################
	
class MongoQueryEngine():
	def __init__(self, query, field):
		self.__query = query
		self.__field = field
		
		self.__or = ["OR","or","Or","|","||","OF"]
		self.__and = ["AND","and","And","&","&&","EN"]
		
	def __convertToOrArray(self, *args):
		return json.dumps({"$or":args})
		
	def convert(self):
		result = {}
		elements = self.__query.strip(" ").split(" ")
				
		if len(elements) == 0 or len(elements[0]) == 0:
			return "{}"
		if len(elements) >= 1:
			result[self.__field] = " ".join(elements)
			return json.dumps(result)			
			
###############################################################################
			
class QueryEngine():
	""" Converts text queries it to MongoDB match queries or a ElasticSearch Queries. """
	def __init__(self):
		self.__query = None
		self.__field = "contents"
		self.SpellingEngine = None
		self.ThesaurusEngine = None
	
	def convert(self, query):
		self.__query = query
		self.__spellCheck()
		self.__synonymCheck()
		
	def __spellCheck(self):			
		query = self.__query
		words = query.split(" ")
		spellchecked = " ".join([self.SpellingEngine.correct(word) for word in words])
		self.__query = spellchecked
		
	def __synonymCheck(self):
		query = self.__query
		words = query.split(" ")
		synonyms = " ".join([ "(%s)" % "|".join([word] + self.ThesaurusEngine.getSynonyms(word)) for word in words])
		self.__query = synonyms
	
	def __convertToMongo(self):
		return MongoQueryEngine(self.__query, self.__field).convert()
	
	def __convertToElasticSearch(self):
		pass
	
	def __getEmpty(self):
		""" Returns the default response when a conversion type is unknown. Currently `None`."""
		return None	
	
	def get(self, queryType):
		""" Returns the converted query in the specified format, if it is available.
		
		:param queryType: Type of query that needs to be retrieved. Either `mongo` or `elasticsearch`.
		:rtype: String, the resulting query.
		"""
		queryTypes = {
			"mongo":self.__convertToMongo,
			"elasticsearch":self.__convertToElasticSearch
		}
		return queryTypes.get(queryType, self.__getEmpty)()
	
	
############################# TEST QUERYENGINE ################################

def setup_func():
	global qe
	qe = QueryEngine()

def teardown_func():
	global qe
	del qe

@with_setup(setup_func, teardown_func)
def test_qe_init():
	assert isinstance(qe, QueryEngine)
	
@with_setup(setup_func, teardown_func)
def test_qe_convert():
	assert True
	
@with_setup(setup_func, teardown_func)
def test_qe_convertToMongo():	
	plain = [
		"",
		"SearchTerm",
		"SearchTerm ZoekTerm",
	]
	
	expected = [
		'{}',
		'{"contents": "SearchTerm"}',
		'{"contents": "SearchTerm ZoekTerm"}'
	]
	
	for p, e in zip(plain,expected):
		qe._QueryEngine__query = p
		r = qe._QueryEngine__convertToMongo()
		assert r == e
		
@with_setup(setup_func, teardown_func)
def test_qe_convertToElasticSearch():
	assert True
	
@with_setup(setup_func, teardown_func)
def test_qe_getEmpty():
	assert qe._QueryEngine__getEmpty() == None
	
@with_setup(setup_func, teardown_func)
def test_qe_get():
	qe._QueryEngine__query = "SearchTerm"
	assert qe.get("elasticsearch") == qe._QueryEngine__convertToElasticSearch()
	assert qe.get("mongo") == qe._QueryEngine__convertToMongo()
	assert qe.get("thisisunavailable") == None
	assert qe.get(1) == None
	
@with_setup(setup_func, teardown_func)
def test_qe_spellcheck():
	se = SpellingEngine()
	se.model = se.trainWithDatabaseDocuments(limit=25)
	qe.SpellingEngine = se
	
	qe._QueryEngine__query = "hoge raad"
	qe._QueryEngine__spellCheck()
	assert qe._QueryEngine__query == "hoge raad"
	
	qe._QueryEngine__query = "wetboek van starfrecht"
	qe._QueryEngine__spellCheck()
	assert qe._QueryEngine__query == "wetboek van strafrecht"
	
	qe._QueryEngine__query = "sector kanton regtbank mastricht"
	qe._QueryEngine__spellCheck()
	assert qe._QueryEngine__query == "sector kanton rechtbank maastricht"
	
@with_setup(setup_func, teardown_func)
def test_qe_synonymcheck():
	te = ThesaurusEngine()
	with open("thesaurus.txt") as thesaurusFile:
		thesaurus = thesaurusFile.read()
	te.parseOpentaalThesaurus(thesaurus)
	qe.ThesaurusEngine = te
	
	qe._QueryEngine__query = "hoge raad"
	qe._QueryEngine__synonymCheck()
	assert qe._QueryEngine__query == "(hoge) (raad|raadgeving|advies|adviesraad)"
	
	qe._QueryEngine__query = "sector kanton rechtbank maastricht"
	qe._QueryEngine__synonymCheck()
	assert qe._QueryEngine__query == "(sector|deel) (kanton) (rechtbank|hof|gerecht|toonbank|balie|gerechtshof|tribunaal) (maastricht)"

	