import json, pprint

from Yuras.webapp.models.Document import Document

from elasticsearch import Elasticsearch

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
		