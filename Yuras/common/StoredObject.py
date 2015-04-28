"""
This module was originally programmed for Olympus, but can now be used as a component for Yuras.
"""

from abc import ABCMeta, abstractmethod
from Yuras.common.Storage import Storage
from Yuras.common.Config import Config
import random, time, datetime, copy,pprint

class StoredObject():
	""" This is a StoredObject, the base class of anything that is to be stored in our database.
	Inheriting from this in lieu of communicating directly with PyMongo or Storage() will allow you to instantaneously save, merge and remove your objects. As this is an abstract class it cannot be instantiated directly and must therefor be subclassed.
	"""
	__metaclass__ = ABCMeta
	
	def __init__(self, database=None, collection=None, name = ""):
		""" Sets up the object
		
		:param database: Optional, the database where this object is to be stored. Defaults to the database stored in Config.
		:param collection: Optional, the collecion where this object is to be stored.
		:param name: The pretty name of this object.
		"""
		if database is None:
			self._database = Config().database
		else:
			self._database = database
		self._collection = collection
		self.__storage = Storage()
		self.name = name
		self._created = datetime.datetime.now()
		self._type = self.__class__.__name__
		if not hasattr(self, "_encrypt"):
			self._encrypt = True
	
	def setDatabase(self,database):
		"""Sets the database for this object."""
		self._database = database
		
	def setCollection(self, collection):
		"""Sets the collection for this object. This is analogous to a table in relational databases."""
		self._collection = collection
	
	def save(self):
		"""Save this object into the database with all its public attributes."""
		# Can't save without a database or a table
		if self._database is None:
			raise ValueError, "No database has been selected."
		if self._collection is None:
			raise ValueError, "No collection has been selected."
	
		# Check private variables. We shouldn't store these.
		document = {}	
		for key, value in self.__dict__.items():
			key = key.replace("_"+self._type, "")
			key = key.replace("_StoredObject", "")
			if key.startswith("__"):
				continue
			document[key] = value
		
		# Let's store this object
		storage = self.__storage
		storage.getDatabase(self._database)
		storage.getCollection(self._collection)
		
		if hasattr(self, "_id"):
			storage.saveDocument(document)
		else:
			storage.insertDocument(document)
			self._id = document["_id"]
	
	def loadFromRawData(self, data):
		""" This will create an object of the given class from a raw dictionary. Typically this would be what comes out of a the database, but it can also be used to initiate a whole new object from scratch.
		
		:param data: A dictionary containing the data to be set for this new object.
		:rtype: A new instance of this class with all the data specified pre set.
		"""
		newObject = self.__class__()
		for key, value in data.items():
			setattr(newObject, key, value)
			
		return newObject
	
	def getObjectsByKey(self, key, value, limit=None, skip=0):
		""" This will retrieve documents from the database and collection specified by this object based on one of their keys and convert them to their proper Python object state.
		
		:param key: The key to select on.
		:param value: The value to search for.
		:param limit: The maximum amount of objects to return. Will return all results by default.
		:param skip: The amount of objects to skip, basically an offset.
		:rtype: All the matching objects stored in the database.
		"""
		
		return self.matchObjects({key:value}, limit, skip)
	
	def __multi_get(self, d, attr, default = None):
		""" Get a the value of a nested key in a dictionary
		
		:param obj: Object to get attrs from.
		:param attr: Attribute (chain) should be a string.
		:param default: The default return value for this operation.
		:rtype: The nested attribute

		"""
		attributes = attr.split(".")
		for i in attributes:
			try:
				d = d.get(i)
			except AttributeError as e:
				if default is not None:
					return default
				else:
					raise
		return d
	
	def matchObjects(self, match, limit=None, skip=0, fields=None, sort=None, reverse=False):
		""" This method allows you to match a StoredOject directly. It allows for more advanced queries.
		
		:param match: A query dictionary.
		:param limit: The maximum amount of objects to return. Will return all results by default.
		:param skip: The amount of objects to skip, basically an offset.
		:param fields: The fields to return for this object.
		:param sort: The documents are sorted by the given indices. This will be slower on encrypted documents, as they are sorted in Python instead of in the database.
		:param reverse: Whether or not documents are returned in reverse. False by default.
		:rtype: All the matching objects stored in the database.
		"""
		
		if fields is None:
			fields = {}
		storage = self.__storage
		database = self._database
		collection = self._collection
		
		if database is None or collection is None:
			raise ValueError, "The object needs to be assigned a database and a collection."
		
		storage.getDatabase(database)
		storage.getCollection(collection)
		
		# Always try to add the _encrypt key, to ensure unencrypted documents won't have an attempted decryption
		if 0 not in fields.values() and False not in fields.values() and len(fields) > 0:
			fields["_encrypt"] = True
						
		if getattr(self, "_encrypt", True) and Config().encryptDocuments:		
			sortDecrypted = True
			documents = storage.getDocuments(match, limit, skip, fields, sort=None)
		else:
			sortDecrypted = False
			documents = storage.getDocuments(match, limit, skip, fields, sort=sort, _encrypted=False)
					
		if sort is not None and sortDecrypted:
			documents.sort(key=lambda d: self.__multi_get(d, sort, default=""), reverse=reverse)
		else:
			if reverse:
				documents.reverse()
				
		objects = [ self.loadFromRawData( data ) for data in documents ]
		
		return objects
		
	def remove(self):
		""" Removes this object from the database. It will still remain in memory, however, and can be resaved at a later time provided that the original reference is maintained."""
		storage = self.__storage
		database = self._database
		collection = self._collection
		
		if database is None or collection is None:
			raise ValueError, "The object needs to be assigned a database and a collection."
		
		storage.getDatabase(database)
		storage.getCollection(collection)
		documents = storage.removeDocuments({"_id":self._id})
		
	def setAttribute(self, attr, source, value):
		""" Set the given attribute to this value. It will overwrite any previous data.
		
		:param attr: The name of the attribute.
		:param source: The source of data to be set.
		:param value: The value that should be set for this source.
		"""
		attribute = {}
		attribute[source] = value
		setattr(self,attr,attribute)
		
	def addAttribute(self, attr, source, value):
		""" Add the given attribute to this value. It will retain any other data from other sources, but will overwrite any data from the same source in this attribute.
		
		:param attr: The name of the attribute.
		:param source: The source of data to be set.
		:param value: The value that should be set for this source.
		"""
		attribute = getattr(self, attr, {})
		attribute[source] = value
		setattr(self,attr,attribute)

	def getAttribute(self, attr, source=None):
		""" Will return the data stored in this attribute from the given source.
		
		:param attr: The name of the attribute.
		:param source: The source of data to be set. (Optional)
		:rtype: The data stored in this attribute from this source.
		"""
		if not hasattr(self, attr):
			return None			
		attribute = getattr(self, attr, {})
		if source == None:
			return attribute
		return attribute.get(source, None)
		
	def __add__(self, other):
		""" Overloads the + (plus) operator and uses it to merge two objects. If there is a conflict for a key the value from the first object in the equation will be chosen.
		
		For example::
			
			ProteinOne = Protein()
			ProteinTwo = Protein()
			ProteinOne.setAttribute("attribute", "source", "ValueOne")
			ProteinOne.setAttribute("attribute", "source", "ValueTwo")
			
			ProteinMerged = ProteinOne + ProteinTwo
			ProteinMerged.getAttribute("attribute","source") == "ValueOne" # Yields True
		
		The original two objects will not be affected.
		
		:param other: The object that this object will be merged with.
		:rtype: A new object with the merged date from the two given objects.
		"""
		attributes = self.mergeObjects(self,other)
		newObject = self.__class__()
		newObject.__dict__ = attributes
		return newObject
		
	def mergeObjects(self, objectOne, objectTwo, path=None):
		""" Takes the attributes from two objects and attempts to merge them. If there is a conflict for a key the value from the first object in will be chosen.
		
		:param objectOne: The first object
		:param objectTwo: The second object
		:param path: The root of the merger.
		:rtype: A dictionary of merged values.
		"""		
		
		a = copy.deepcopy(dict([(k,v) for k,v in objectOne.__dict__.items() if not k.startswith("_StoredObject__")]))
		b = copy.deepcopy(dict([(k,v) for k,v in objectTwo.__dict__.items() if not k.startswith("_StoredObject__")]))
		
		attributes = self.merge(a,b,path)
		return attributes
		
	def merge(self, a, b, path=None):
		""" Recursively merges two dictionaries. If there is a conflict for a key the value from the first object in will be chosen. All the changes are inserted into the first dictionary.
		
		:param a: The first dictionary.
		:param b: The second dictionary.
		:param path: The root of the merger.
		:rtype: A dictionary of merged values.
		"""
		if path is None: path = []
		for key in b:
			if key in a:
				if isinstance(a[key], dict) and isinstance(b[key], dict):
					self.merge(a[key], b[key], path + [str(key)])
				elif a[key] == b[key]:
					pass # same leaf value
				else:
					# Conflict, use the value from A
					pass
					
			else:
				a[key] = b[key]
		return a
		
		
# For testing purposes only #
		
class TestObject(StoredObject):
	""" TestObject implements only the most basic of the StorageObject's methods for testing purposes. """
	def __init__(self):
		super(TestObject, self).__init__(database = "test_database", collection = "test_collection")

import random
r = random.randrange(1000000000,9999999999)
		
def test_setAttribute():
	t = TestObject()
	t.setAttribute("random", "python", r)
	assert t.random["python"] == r
	
def test_addAttribute():
	t = TestObject()
	t.addAttribute("random", "python", r)
	t.addAttribute("random", "lua", r+1)
	assert t.random["python"] == r
	assert t.random["lua"] == r+1
	
def test_getAttribute():
	t = TestObject()
	t.addAttribute("random", "python", r)
	assert t.getAttribute("random", "python") == r
		
def test_createTestObject():
	t = TestObject()
	t.random = r
	t.save()
	assert t.random == r

def test_findTestObject():
	t = TestObject().getObjectsByKey("random",r)
	assert len(t) > 0
	assert t[0].random == r
	
def test_removeObject():
	t = TestObject().getObjectsByKey("random",r)
	if isinstance(t[0], TestObject):
		t[0].remove()
	else:
		t[0]().remove()
	
def test_loadFromRawData():
	t = TestObject().loadFromRawData({"r":r})
	assert t.r == r
	
def test_mergeObjects():
	t1 = TestObject()
	t2 = TestObject()
	
	t1.addAttribute("rand", "python", r)
	t2.addAttribute("rand", "lua", r+1)
	resultingAttributes = TestObject().mergeObjects(t1,t2)
	
	assert resultingAttributes["rand"]["python"] == r
	assert resultingAttributes["rand"]["lua"] == r+1
	
def test_mergeByAddOperator():
	t1 = TestObject()
	t2 = TestObject()
	t1.addAttribute("rand", "python", r)
	t2.addAttribute("rand", "lua", r+1)
	
	t3 = t1+t2
	assert t3.getAttribute("rand", "python") == r
	assert t3.getAttribute("rand", "lua") == r+1
