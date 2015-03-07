from Yuras.webapp.models.Document import Document

class PublicDocument(StoredObject):
	def __init__(self, *args, **kwargs):
		self._encrypt = False
		return super(Document, self).__init__(*args, **kwargs)