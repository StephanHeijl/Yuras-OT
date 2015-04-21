from nose import with_setup
from collections import defaultdict

from Yuras.common.Singleton import Singleton
from Yuras.common.Config import Config

import json, re

class ThesaurusEngine(Singleton):
	def __init__(self):
		if self.instantiated:
			return
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
	
	def __convertToRomanNumerals(self, integer):
		""" Convert an integer to a Roman numeral. Part of the synonym process. Source: https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch03s24.html """
		if not isinstance(integer, type(1)):
			raise TypeError, "expected integer, got %s" % type(integer)
		if not 0 < integer < 4000:
			raise ValueError, "Argument must be between 1 and 3999"
		ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
		nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
		result = []
		for i in range(len(ints)):
			count = int(integer / ints[i])
			result.append(nums[i] * count)
			integer -= ints[i] * count
		return ''.join(result)
	
	def getSynonyms(self, word):
		try:
			# Tries to convert every word to a Roman numeral, instantly fails when integer casting fails.
			return [self.__convertToRomanNumerals(int(word))]
		except:
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
	
@with_setup(setup_func, teardown_func)
def test_te_convertToRomanNumerals():
	assert te._ThesaurusEngine__convertToRomanNumerals(12) == "XII"
	assert te._ThesaurusEngine__convertToRomanNumerals(9) == "IX"
	assert te._ThesaurusEngine__convertToRomanNumerals(50) == "L"
	assert te._ThesaurusEngine__convertToRomanNumerals(2013) == "MMXIII"