from nose import with_setup
from collections import defaultdict

from Yuras.common.Singleton import Singleton
from Yuras.common.Config import Config
from Yuras.common.SpellingEngine import SpellingEngine
from Yuras.common.ThesaurusEngine import ThesaurusEngine

import json, re

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
			
class QueryEngine(Singleton):
	""" Converts text queries to extended text queries, including spell checking and synonym checking. """
	def __init__(self):
		self.__query = None
		if self.instantiated:
			return
		
		self.__field = "contents"
		self.SpellingEngine = None
		self.ThesaurusEngine = None
		self.instantiated = True
	
	def convert(self, query):
		self.__query = query
		if self.SpellingEngine is not None:
			self.__spellCheck()
		if self.ThesaurusEngine is not None:
			self.__synonymCheck()
		return self.__query
		
	def __spellCheck(self):			
		query = self.__query
		words = query.split(" ")
		spellchecked = " ".join([self.SpellingEngine.correct(word.strip("() *[]:")) if word not in ["AND","OR","(",")"] else word for word in words ])
		self.__query = spellchecked
		
	def __synonymCheck(self):
		query = self.__query
		words = query.split(" ")
		synonyms = []
		for word in words:
			if word.lower() in ["and","or","(",")"]:
				synonyms.append(word.upper())
				continue
			synonyms.append("(%s)" % " OR ".join([word+"^2"] + self.ThesaurusEngine.getSynonyms(word.strip("() *[]:"))))
		
		synonyms = " ".join(synonyms)
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
	print qe._QueryEngine__query
	assert qe._QueryEngine__query == "(hoge^2) (raad^2 OR raadgeving OR advies OR adviesraad)"
	
	qe._QueryEngine__query = "sector kanton rechtbank maastricht"
	qe._QueryEngine__synonymCheck()
	print qe._QueryEngine__query
	assert qe._QueryEngine__query == "(sector^2 OR deel) (kanton^2) (rechtbank^2 OR hof OR gerecht OR toonbank OR balie OR gerechtshof OR tribunaal) (maastricht^2)"

	
@with_setup(setup_func, teardown_func)
def test_qe_convert():
	te = ThesaurusEngine()
	with open("thesaurus.txt") as thesaurusFile:
		thesaurus = thesaurusFile.read()
	te.parseOpentaalThesaurus(thesaurus)
	qe.ThesaurusEngine = te
	
	se = SpellingEngine()
	se.model = se.trainWithDatabaseDocuments(limit=25)
	qe.SpellingEngine = se
	
	assert qe.convert("sector kanton regtbank mastricht") == "(sector^2 OR deel) (kanton^2) (rechtbank^2 OR hof OR gerecht OR toonbank OR balie OR gerechtshof OR tribunaal) (maastricht^2)"
	