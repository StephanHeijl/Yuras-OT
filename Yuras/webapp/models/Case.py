from Yuras.common.StoredObject import StoredObject
from Yuras.webapp.models.Document import Document

from bson.objectid import ObjectId

class Case(StoredObject):
	def __init__(self):	
		self.title = "Case"
		self.documents = []
		self.user = None
		
		super(Case, self).__init__(collection = "cases")
		
	def insertDocument(self, _id):
		""" Adds a document to this case.
		
		:param _id: The ID of the document that will be added.
		:rtype: True if add succeeded.		
		"""
		
		print _id
		if _id == None:
			return False
		try:
			document = Document().getObjectsByKey("_id", _id)[0]
		except Exception as e:
			print e
			return False
		
		self.documents.append({"title":document.title, "id":_id})
		self.save()
		return True
	
	def removeDocument(self, _id):
		""" Removes a document from this case. Does not check if a document exists before removing from case.
		
		:param _id: The ID of the document that will be removed.
		:rtype: True if add succeeded.		
		"""
		if _id == None:
			return False
		
		try:
			for document in self.documents[:]:
				if document["id"] == _id:
					self.documents.remove(document)
			self.save()
			return True
		except Exception as e:
			print self.documents
			print e
			return False

	def getDocuments(self):
		match = {"_id": {"$in":[ ObjectId(d["id"]) for d in self.documents] }}
		documents = Document().matchObjects( match )
		return documents
		
	def getFullCaseRecommendations(self,tags = None):
		if tags is None:
			documents = self.getDocuments()
			tags = []
			for d in documents:
				tags+=d.tags.keys()
			tags = list(set(tags))
			
		related = Document().getRelatedDocumentsByTags(tags=tags,asJSON=False,exclude=[ObjectId(d["id"]) for d in self.documents])
		print related, type(related)
		return related