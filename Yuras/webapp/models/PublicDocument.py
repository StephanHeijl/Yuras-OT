import json, pprint, re

from Yuras.webapp.models.Document import Document
from Yuras.common.Pandoc import Pandoc

from elasticsearch import Elasticsearch
from Yuras.common.QueryEngine import QueryEngine, SpellingEngine, ThesaurusEngine

class PublicDocument(Document):
	"""
	This class serves merely as a wrapper for public documents.
	Its contents are never encrypted by the storage engine.
	Its type is still Document, allowing it to be picked up by Document searches.

	This class also replaced the Mongo searches with Elasticsearch searches, 
	which perform way better and allow for more complex operations.
	"""
	def __init__(self, *args, **kwargs):
		self._encrypt = False
		self._type = "Document"
		return super(PublicDocument, self).__init__(*args, **kwargs)
	
	@staticmethod
	def search(query, category=None, skip=0, limit=24, filters=None):
		qe = QueryEngine()
		query = extendedQuery = qe.convert(query)
		
		es = Elasticsearch()
		# Give out extra points in the score for Title inclusion, but rate content occurences higher
		# This ensures that laws will always come up correctly
		esQuery = {
			  "query": {
				"bool": {
				  "should": [
					{
					  "query_string": {
						"query": query,
						"boost": 1,
						"default_field": "title"
					  }
					},
					{
					  "query_string": {
						"query": query,
						"boost":5,
						"default_field": "_all"
					  }
					}
				  ]
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
				"judicial_instance": {
				  "terms": {
					"field": "judicial_instance"
				  }
				},
				"document_type": {
				  "terms": {
					"field": "document_type"
				  }
				},
				"book": {
				  "significant_terms": {
					"field": "book"
				  }
				},
				"__Suggested_Terms": {
					"significant_terms": {
						"field": "contents"
					}
				}
			  }
			}
		
		if filters is not None:
			esQuery["query"]["bool"]["must"] = []
			for k,vs in filters.items():
				if not isinstance(vs,list):
					vs = [vs]
				for v in vs:
					esQuery["query"]["bool"]["must"] = {"term" : { k : v } }
				
		
		res = es.search(index="document", size=24, body=esQuery)
		  

		results = []
		for r in res['hits']['hits']:
			d = Document()
			for k,v in r['_source'].items():
				setattr(d, k, v)
			d.markedContents = r.get("highlight",{}).get("contents","")
			if d.markedContents == "":
				# Fallback summary
				d.markedContents = [Pandoc().convert("markdown_github", "plain", r["_source"].get("contents","No summary")[:300] )+"..."]
			else:
				# Strip loose tags from the end
				d.markedContents = [re.sub("\<[a-z\\\]+$", "", l) for l in d.markedContents]
			d.score = round(r.get("_score",0)/res['hits']['max_score'],2)*10 # Gives a score out of 10
			results.append(d)

		return results, query, res['aggregations']
	
	def getRelatedDocuments(self, tags=None, asJSON=True, exclude=None):
		""" Overwrite the getRelatedDocumentsByTags method and use the ElasticSearch methods. """
		es = Elasticsearch()

		res = es.search(index="document", size=10, body={"query": {
			"more_like_this" : {
				"like_text" : self.contents,
				"stop_words" : Document.getStopwords(),
				"ids": [str(self._id)],
				"exclude":True
			}
		}})
		
		if asJSON:
			return json.dumps([[ d["_id"], d["_source"]["title"], d["_score"]*3 ] for d in res['hits']['hits']])
		
	@staticmethod
	def getRelatedDocumentsFromSet(ids):
		if len(ids) == 0:
			return []
		es = Elasticsearch()
		
		docs = []
		for _id in ids:
			docs.append({
			  "_index": "document",
			  "_type": "document",
			  "_id": _id
			})		
		
		body = { "query": {
				"more_like_this": {
				  "fields": [
					"contents",
					"title",
					"summary"
				  ],
				  "docs": docs
				}
			  }
			}
		
		print body
		res = es.search(index="document", size=6, body=body)
		
		results = []
		for r in res['hits']['hits']:
			d = {}
			for k,v in r['_source'].items():
				d[k] = v
			d["score"] = round(r.get("_score",0)/res['hits']['max_score'],2)*10 # Gives a score out of 10
			results.append(d)
			
		return results
		
		