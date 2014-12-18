from Yuras.common.StoredObject import StoredObject

class Document(StoredObject):
	def __init__(self):
		self.title = "Document"
		self.createdDate = None
		self.modifiedDate = None
		self.contents = ""
		self.tags = []
		self.annotations = []
		
		self.secure = False
		
		super(Document, self).__init__(database = "Yuras1", collection = "documents")
		
	def save(self):
		contents = self.contents	
		
		super(Document, self).save()