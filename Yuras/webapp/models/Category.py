from Yuras.common.StoredObject import StoredObject

class Category(StoredObject):
	def __init__(self):		
		super(Category, self).__init__(collection = "categories")