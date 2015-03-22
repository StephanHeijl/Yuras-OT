import json, pprint, re

from Yuras.webapp.models.Document import Document

from elasticsearch import Elasticsearch
from Yuras.common.QueryEngine import QueryEngine, SpellingEngine, ThesaurusEngine

class PublicDocument(Document):
	"""
This class serves merely as a wrapper for public documents.
Its contents are never encrypted by the storage engine.
Its type is still Document, allowing it to be picked up by Document searches.

	This class also replaced the Mongo searches with Elasticsearch searches, which perform way better.	
	"""
	def __init__(self, *args, **kwargs):
		self._encrypt = False
		self._type = "Document"
		return super(PublicDocument, self).__init__(*args, **kwargs)
	
	@staticmethod
	def search(query, category=None, skip=0, limit=24):
		qe = QueryEngine()
		query = extendedQuery = qe.convert(query)		
		
		es = Elasticsearch()

		res = es.search(index="document_contents", size=24, body={"query": {
			"query_string" : {
				"query" : query
			}
		}})

		results = []
		for r in res['hits']['hits']:
			d = Document()
			for k,v in r['_source'].items():
				setattr(d, k, v)
			results.append(d)

		stopwords = Document.getStopwords()

		pattern = "" + ("|".join([w for w in re.split("[^\w]+",query) if len(w)>2])) + ""
		markedWords = re.compile(pattern, flags=re.IGNORECASE)
		for result in results:
			result.markedContents = []
			for word in query.split(" "):
				if word in stopwords:
					continue
				surroundLength = 20
				try:
					wordIndex = result.contents.lower().index(word)
				except:
					continue

				start = wordIndex - surroundLength
				if start < 0:
					start = 0
				end = wordIndex + len(word) + surroundLength
				surroundingText = result.contents[start:end]
				markedString = markedWords.sub('<span class="marked">\g<0></span>', surroundingText) 

				if len(markedString) > 1:
					result.markedContents.append( markedString )

		return results, query
	
	def getRelatedDocumentsByTags(self, tags=None, asJSON=True, exclude=None):
		""" Overwrite the getRelatedDocumentsByTags method and use the ElasticSearch methods. """
		es = Elasticsearch()

		res = es.search(index="document_contents", size=10, body={"query": {
			"more_like_this" : {
				"like_text" : self.contents,
				"stop_words" : Document.getStopwords(),
				"ids": [str(self._id)],
				"exclude":True
			}
		}})
		
		if asJSON:
			return json.dumps([[ d["_id"], d["_source"]["title"], d["_score"]*3 ] for d in res['hits']['hits']])
		