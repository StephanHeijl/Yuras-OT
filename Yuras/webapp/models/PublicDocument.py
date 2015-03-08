from Yuras.webapp.models.Document import Document

class PublicDocument(Document):
	""" This class serves merely as a wrapper for public documents.
	Its contents are never encrypted by the storage engine.
	Its type is still Document, allowing it to be picked up by Document searches.
	
	"""
	def __init__(self, *args, **kwargs):
		self._encrypt = False
		self._type = "Document"
		return super(PublicDocument, self).__init__(*args, **kwargs)