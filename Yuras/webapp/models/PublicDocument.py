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
		
		esQuery = {
			  "query": {
				"query_string": {
				  "query": query
				}
			  },
			  "size": 20,
			  "highlight": {
				"fields": {
				  "contents": {}
				},
				"pre_tags": [
				  "<span class='marked'>"
				],
				"post_tags": [
				  "</span>"
				]
			  },
			  "aggs": {
				"articles": {
				  "terms": {
					"field": "document.chapter",
					"include": "\\d+(\\.?\\d+)?",
					"size": 20
				  }
				},
				"chapters": {
				  "terms": {
					"field": "document.chapter",
					"exclude": "\\w{1,4}|i+|\\d+|hoofdstuk|algeme[en]{2}",
					"size": 10
				  }
				},
				"book": {
				  "terms": {
					"field": "document.book",
					"exclude": "\\w{1,4}|i+|\\d+|wetboek|algeme[en]{2}",
					"size": 10
				  }
				}
			  }
			}
		
		res = es.search(index="document", size=24, body=esQuery)
		  

		results = []
		for r in res['hits']['hits']:
			d = Document()
			for k,v in r['_source'].items():
				setattr(d, k, v)
			d.markedContents = r.get("highlight",{}).get("contents","")
			d.score = round(r.get("_score",0)/res['hits']['max_score'],2)*10
			results.append(d)

		stopwords = Document.getStopwords()

		

		return results, query
	
	def getRelatedDocumentsByTags(self, tags=None, asJSON=True, exclude=None):
		""" Overwrite the getRelatedDocumentsByTags method and use the ElasticSearch methods. """
		es = Elasticsearch()

		res = es.search(index="document", size=9, body={"query": {
			"more_like_this" : {
				"like_text" : self.contents,
				"stop_words" : Document.getStopwords(),
				"ids": [str(self._id)],
				"exclude":True
			}
		}})
		
		if asJSON:
			return json.dumps([[ d["_id"], d["_source"]["title"], d["_score"]*3 ] for d in res['hits']['hits']])
		