from Yuras.machine_learning_ng.RechtspraakParser import RechtspraakParser

import networkx as nx
import numpy as np

import sys,os,pprint,collections,math,re,json
 
from nltk.tokenize import word_tokenize
import nltk.data
from sklearn.feature_extraction.text import CountVectorizer


class Summarizer():
	def __init__(self):
		pass
	
	def trainSummarizer(self):
		pass
	
	def summarize(self, text):
		pass
	
class SummarizeFragment(Summarizer):
	def __init__(self):
		self.sentence_tokenizer = PunktSentenceTokenizer()
		self.documents = []
		self.scores = collections.defaultdict(float)
		self.wordDocumentCount = collections.defaultdict(int)
		self.tagger = nltk.data.load("taggers/alpino_brill_aubt.pickle")
	
	def addDocument(self, document):
		self.documents.append(document)
		words = word_tokenize(document)
		for word in list(set(words)):
			self.wordDocumentCount[word]+=1	
			
	def getWordScore(self, word, words, location="body"):
		tf = float(words.count(word)) / len(words)
		idf = math.log( float(len(self.documents)) / (1 + self.wordDocumentCount[word]) )
		
		score = tf*idf*self.getMultiplier(location)		
		return score
		
	def getMultiplier(self, location="body"):
		# Location can be "body", "title" or "summary"
		multiplierDict = {
			"body"		: 1,
			"title"		: 10,
			"summary"	: 3
		}
		multiplier = multiplierDict.get(location, 1)
		return multiplier
	
	def getScoresForText(self, text, document, location="body"):
		tagged = self.tagger.tag(word_tokenize(text))
		nouns = set()
		for t in tagged:
			if t[1] == "noun" and len(t[0])>3:
				nouns.add(t[0])
		
		words = word_tokenize(document)
		for noun in nouns:
			self.scores[noun] += s.getWordScore(noun, words, location=location)
	
	
wetboekencsv = """algemene wet bestuursrecht;awb
wet op de ruimtelijke ordening;ruimtelijke ordening;wro
milieubeheer;wm;
planvoorschriften;
woningwet;
wetboek van strafrecht;wvs;sr;
verdrag tot bescherming van de rechten van de mens en de fundamentele vrijheden;
algemene wet inkomensafhankelijke regelingen;awir;
europees verdrag voor de rechten van de mens;evrm;
burgelijke rechtsvordering;rechtsvordering;rv
burgerlijk wetboek;bw;
arbeid vreemdelingen;
wegenverkeerswet 1994;wvw;
vreemdelingenwet 2000;vw 2000;vreemdelingenbesluit 2000;
geluidhinder;wgh;
natuurbeschermingswet 1998;nbw 1998;
habitatrichtlijn;
beleidsregels boeteoplegging wav 2007;
algemene wet inzake rijksbelastingen;
verdrag tot oprichting van de europese gemeenschap;
wetboek van strafvordering;wvs
gemeentewet;
bodembescherming;
opiumwet;ow;
wob;wet openbaarheid van bestuur;
wvo;wet op het voorgezet onderwijs;
monumentenwet 1988;
flora- en faunawet;ffw;
wet algemene bepalingen omgevingsrecht;wabo;
awr;algemene wet rijksbelasting;
rijkswet op het nederlanderschap;
grondwet;gw;
wapens en munitie;
ammoniak en veehouderij;wav;
verontreiniging oppervlaktewateren;
gemeentelijke basisadministratie persoonsgegevens;
drank- en horecawet;
ontgrondingenwet;
huisvestingswet;
inkomstenbelasting 1964;
wvg;wet voorziening gehandicapten;
verordening ruimte;
waardering onroerende zaken;
wgv;wet geurhinder en veehouderij;geurhinder;
woz;waardering onroerende zaken;
rwn;rijkswet op het nederlanderschap;
bhv;bedrijfshulpverlening;
huursubsidiewet;hsw;
monumentenwet;
bouwbesluit;
wte 1995;wet toezicht effectenverkeer 1995;
arbowet;arbobesluit;
reglement rijbewijzen;
waterwet;ww;waterschapswet;
besluit milieu-effectrapportage 1994;"""

wetboeken = [wb.strip(";").split(";") for wb in wetboekencsv.split("\n")]
	
if __name__ == "__main__":
	RP = RechtspraakParser()
	s = SummarizeFragment()
	
	n = 1000
	abstractive, fragments, unlabeled = RP.filterRechtspraakFolder(sys.argv[1], n=n, tokenizer=lambda x: [x])
	
	articleRegexString = "([Aa]rtikel(en)?|art\.) ((\d+|[IVX]+)([:\.]\d+)?([a-z]+)?( en |, ?)?)+ ?(([etdvzan][ewic][a-z]+?((d|st)e[^a-z]))?(lid|paragraaf|volzin)( \d+)?([, ])*)*((van|het|de|Wet|wet) )*( ?(([A-Z]([A-Z]{1,4}|[a-z]{1,2}))[^\w]) ?(\d{4})?|([\w\-]+ ?)+ ?(\d{4})?)"
	articleRegex = re.compile(articleRegexString)
	
	articleCount = collections.defaultdict(int)
	
	for percentage, document, summary, title in fragments:
		s.addDocument(document[0])
	
	for percentage, document, summary, title in fragments:				
		results = set()

		for result in articleRegex.finditer(document[0]):
			results.add(result.groups())

		categories = collections.defaultdict(int)
		filterwords = ["onder", "lid", "alinea"]
		for result in results:
			suffix = [g for g in result if g is not None][-2]
			if True not in [f in suffix for f in filterwords] and suffix not in list("0123456789"):
				found = False
				
				if suffix == "deze wet":
					articleName = " ".join([result[0], result[3], wetboek[0]])
					try:
						# Give the law the same category as the previous one, as "deze wet" refers to the previous law.
						categories[wetboek[0]]+=1
					except:
						pass
					continue
					
				for wetboek in wetboeken:
					if found:
						break
					for wb in wetboek:
						if wb in suffix:
							found = True
							categories[wetboek[0]]+=1
		
		scategories = sorted(categories.items(), key=lambda x: x[1])
			
		s.scores = collections.defaultdict(float)
		
		s.getScoresForText(document[0], document[0], "body")
		s.getScoresForText(title, document[0], "title")
		s.getScoresForText(summary[0], document[0], "summary")
		
		"""
		print title
		try:
			print scategories[-1][0]
		except:
			print "No valid category found."
		print ", ".join( dict(sorted(s.scores.items(), key=lambda x: x[1])[-10:] ).keys() )
		"""
		bestwords = dict(sorted(s.scores.items(), key=lambda x: x[1])[-10:] ).keys()
		while len(bestwords) < 10:
			bestwords.append("")
		
		if len(scategories) == 0 or scategories[-1][1] < 3:
			print '"'+"\",\"".join(bestwords+["unknown"])+'"'
		else:		
			print '"'+"\",\"".join(bestwords+[scategories[-1][0]])+'"'
		
		
		#exit()
	
	#print json.dumps([a for a in sorted(articleCount.items(), key=lambda x: x[1]) if a[1] > 2], indent=4)