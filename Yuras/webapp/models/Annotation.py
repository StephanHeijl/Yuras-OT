from Yuras.common.webapp import StoredObject

class Annotation(StoredObject):
	def __init__(self):
		self.document = None
		self.location = [0,0]
		self.contents = ""