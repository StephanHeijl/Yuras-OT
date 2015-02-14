from Yuras.common.StoredObject import StoredObject

class Case(StoredObject):
	def __init__(self):	
		self.title = "Case"
		self.documents = []
		self.user = None
		
		super(Case, self).__init__(collection = "cases")