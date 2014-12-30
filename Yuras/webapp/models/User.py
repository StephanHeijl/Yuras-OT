from Yuras.common.StoredObject import StoredObject

class User(StoredObject):
	def __init__(self):
		self.username = ""
		
		self.firstname = ""
		self.lastname = ""
		
		self.email = ""
		self.password = ""
		self.documents = []
		
		super(User, self).__init__(collection = "users")