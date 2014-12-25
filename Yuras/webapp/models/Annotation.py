from Yuras.common.StoredObject import StoredObject

class Annotation(StoredObject):
	def __init__(self):
		self.document = None
		self.location = [0,0]
		self.contents = ""
		
		super(Annotation, self).__init__(collection = "annotations")