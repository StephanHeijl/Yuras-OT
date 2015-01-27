from Yuras.common.StoredObject import StoredObject

class Document(StoredObject):
	def __init__(self):
		self.title = "Document"
		self.createdDate = None
		self.modifiedDate = None
		self.contents = ""
		self.tags = []
		self.annotations = []
		self.category = None
		
		self.accessible = True
		
		self.secure = False
		
		super(Document, self).__init__(collection = "documents")
		
	def save(self):
		contents = self.contents	
		
		super(Document, self).save()
		
	def matchObjects(self, match, limit=None, skip=0, fields={"wordcount":0}):
		# Does not return wordcount by default
		return super(Document, self).matchObjects(match,limit,skip,fields)