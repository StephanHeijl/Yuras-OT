"""
This module was originally programmed for Olympus, but can now be used as a component for Yuras.
It has also been extended with encryption and decryption on save and restore respectively.
"""

from Yuras.common.Singleton import Singleton
from Yuras.common.Config import Config
from pymongo import MongoClient
from bson.objectid import ObjectId

import datetime, base64

# Crypto imports
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto import Random
from Crypto.Random import random

class Storage(Singleton):
	""" The storage module provides a layer of abstraction over PyMongo. 
		This will allow us to, if needed, exchange the databases without breaking countless modules 
		that are dependent on database access.
		
		**A note on IV usage in this module:**
		While it is considered bad practice to use the same IV values across a whole database, this mode of 
		operation is still preferable to ECB mode.
		It should be taken into account that the encrypted data should *AT NO TIME* be exposed to the public.
		The values are only to be used internally.
		Also, while the IV is the same across a single database, it should be changed (just like the encryption key)
		for each new DB and client. This allows for less collisions in the initial block.
		Finally, this layer of encryption is the absolute minium amount of security each piece of data receives.
		Any piece of data that is on any higher level of security will have additional layers of security caked on top.
		This base layer is only suitable for basic (public) information like email adresses and names that are non-confidential.
		
		Nonetheless, it is important to take this vurnerability into account.
		
		Special note: this security layer is NOT INTENDED to store plaintext passwords. At no point in time should you
		ever store a password in a production database as plaintext.
		
	"""
	def __init__(self, encryptDocuments=True):
		""" Initializes the connection with the Mongo database. 
		As this is a Singleton, this is only done **once** per instance of GuardStore resulting in lower connection time overhead (unless `reconnect` is called.)
		This might pose problems if the ongoing connection is forcefully closed for whatever reason.
		"""
		
		dbAddress = Config().MongoServer
		dbAddressComponents = dbAddress.split(":")
		host = dbAddressComponents[0]
		port = 27017 # The default MongoDB port.
		
		if len(dbAddressComponents) > 1:
			port = int(dbAddressComponents[1])
		
		self.__client = MongoClient(host, port)
		self.__currentCollection = None
		self.__currentDatabase = None
		self.__encryptDocuments = encryptDocuments
		
		if encryptDocuments:
			try:
				self.iv = base64.b64decode( Config().iv )
			except:
				self.iv = Random.new().read(AES.block_size)
				Config().iv = base64.b64encode( self.iv )
				Config().save()
		
	def reconnect(self):
		""" Executes the initialization function again. This will reconnect the instance to the server. """
		self.__init__()
		
	def getHost(self):
		""" Returns the database host. """
		return self.__client.host
		
	def getPort(self):
		""" Returns the database port. """
		return self.__client.port
		
	def isAlive(self):
		""" Checks whether or not the connection to the database is alive.

		:rtype: Returns the state of the connection as a boolean.
		"""
		return self.__client.alive()
	
	def getDatabase(self, database):
		""" Sets the database to the one specified. If it does not yet exist, it will be created when a document is inserted.
		
		:param database: The name the database that is to be accessed.
		:rtype: The name of the database that is currently being accessed.
		"""
		self.__currentDatabase = self.__client[database]
		return self.__currentDatabase
		
	def dropDatabase(self, database):
		""" Drops the currently selected database.

		:rtype: True if the database was dropped succesfully.
		"""
		self.__client.drop_database(database)
		return True
	
	def getCollection(self, collection):
		""" Sets the collection to the one specified. If it does not yet exist, it will be created when a document is inserted.
		Will throw a ValueError if no database has been selected.
		
		:param collection: The name of the collection that is to be accessed.
		:rtype: The name of the collection that is currently being accessed.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
		
		self.__currentCollection = self.__currentDatabase[collection]
		return self.__currentCollection
		
	def dropCollection(self, collection):
		""" Drops the currently selected collection.
		Will throw a ValueError if no collection has been selected.

		:rtype: True if the collection was dropped succesfully.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
		
		self.__currentDatabase[collection].drop()
		return True		
	
	def __padObject(self,obj):
		""" Converts an object to a string and pads it to the correct length for encryption. 
		Adds the original type to allow for recasting to the original type.
		
:param obj: The object to pad.
:returns: A padded string with type included.
		"""
		objType = type(obj)
		try:
			objString = base64.b64encode( str(obj)  )
		except:
			objString = base64.b64encode( obj.encode('utf-8') )
		
		paddingChar = "{"
		blockSize = AES.block_size
		
		fullString = objString + paddingChar + str(objType)
		
		return fullString + (blockSize - len(fullString) % blockSize) * paddingChar
	
	def __unpadString(self, fullString):
		""" Undoes the padding and type concatenation from `Storage.__padObject`.
		
:param fullString: The padded string.
:returns: The unpadded object in its original form, if possible.		
		"""		
		paddingChar = "{"
		blockSize = AES.block_size
		fullString = fullString.strip(paddingChar)
		stringTypeSplit = fullString.split(paddingChar)
		
		objString = base64.b64decode(paddingChar.join(stringTypeSplit[:-1]))
		objType = stringTypeSplit[-1].split("'")[1]
				
		obj = self.__convert(objString,objType)
		
		return obj
	
	def __convert(self,value, type_):
		""" Converts a string value to a type derived from the `type` function in Python. Will attempt to import 
		a module if the original type is not found as a Python builtin.
		
:param value: The string value.
:param type_: The value derived from `type()` without the xml-like markup and quotes.
:returns: A properly cast object.
		"""
		import importlib
		
		if type_ == "NoneType":
			return None
		if type_ == "bool":
			return type_ == "True"
		if type_ == "datetime.datetime":
			return datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S.%f')
		if type_ == "str":
			return value.decode('utf-8')
				
		try:
			# Check if it's a builtin type
			module = importlib.import_module('__builtin__')
			cls = getattr(module, type_)
		except AttributeError:
			# if not, separate module and class
			module, type_ = type_.rsplit(".", 1)
			module = importlib.import_module(module)
			cls = getattr(module, type_)
		
		try:
			return cls(value)
		except:
			return value
	
	def __encryptDocument(self, document):
		""" Encrypts a dictionary/document for before storage. Skips the ID field for retreival purposes. Field names are left intact.
		Structural information will also be maintained.
		
:param document: The document that should be encrypted. This is a normal MongoDB document (dictionary).
:returns: The MongoDB document with encrypted, base64 encoded values.
		"""
		if isinstance(document, list):
			encryptedDocument = []
			
			for value in document:
				if isinstance(value, list) or isinstance(value, dict):
					encryptedDocument.append(self.__encryptDocument(value))
					continue
				
				cipher = AES.new(Config().encryptionKey, AES.MODE_CBC, self.iv)
				paddedValue = self.__padObject(value)
				encryptedValue = cipher.encrypt( paddedValue )
				encryptedDocument.append(base64.b64encode( encryptedValue ))
			
		elif isinstance(document, dict):
			encryptedDocument = {}
			for key, value in document.items():
				if key == "_id": # Do not encrypt _id field.
					encryptedDocument["_id"] = value
					continue

				if isinstance(value, list) or isinstance(value, dict):
					encryptedDocument[key] = self.__encryptDocument(value)
					continue

				cipher = AES.new(Config().encryptionKey, AES.MODE_CBC, self.iv)
				paddedValue = self.__padObject(value)
				encryptedValue = cipher.encrypt( paddedValue )
				encryptedDocument[key] = base64.b64encode( encryptedValue )
				
		else:
			raise ValueError, "Not a valid encryptable object."
		
		return encryptedDocument
	
	def __decryptDocument(self, document):
		""" Decrypts a dictionary/document for before retrieval.
		
:param document: The document that should be decrypted. This is a normal MongoDB document (dictionary) with encrypted values.
:returns: The MongoDB document with decrypted values.		
		"""
		
		if isinstance(document, list):
			decryptedDocument = []
			
			for value in document:
				if isinstance(value, list) or isinstance(value, dict):
					decryptedDocument[key] = self.__decryptDocument(value)
					continue
				
				value = base64.b64decode(value)			
				cipher = AES.new(Config().encryptionKey, AES.MODE_CBC, self.iv)

				decryptedValue = cipher.decrypt( value )
				try:
					unpaddedValue = self.__unpadString(decryptedValue)
				except UnicodeDecodeError:
					print "Decryption error, wrong key used."

				decryptedDocument.append(unpaddedValue)			
			
		elif isinstance(document, dict):
			decryptedDocument = {}

			for key, value in document.items():
				if key == "_id": # Do not decrypt _id field.
					decryptedDocument["_id"] = value
					continue
					
				if isinstance(value, list) or isinstance(value, dict):
					decryptedDocument[key] = self.__decryptDocument(value)
					continue

				value = base64.b64decode(value)			
				cipher = AES.new(Config().encryptionKey, AES.MODE_CBC, self.iv)

				decryptedValue = cipher.decrypt( value )
				unpaddedValue = self.__unpadString(decryptedValue)

				decryptedDocument[key] = unpaddedValue
				
		else:
			raise ValueError, "Not a valid decryptable object."
		
		
		return decryptedDocument
		
	def insertDocument(self, document):
		""" Inserts a document into the currently selected collection in the currently selected database.
		Will throw a ValueError if no database or collection has been selected.
		
		:param document: A dictionary that will be stored as a document. Its contents can include strings, numbers and several types of native objects, like `datetime`.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
			
		if self.__encryptDocuments:
			encryptedDocument = self.__encryptDocument(document)
			self.__currentCollection.insert( encryptedDocument )
			document["_id"] = encryptedDocument["_id"]
		else:
			self.__currentCollection.insert(document)
		
	def saveDocument(self, document):
		""" Inserts a document into the currently selected collection in the currently selected database.
		Will throw a ValueError if no database or collection has been selected.
		
		:param document: A dictionary that will be stored as a document. Its contents can include strings, numbers and several types of native objects, like `datetime`.
		"""
		
		if not hasattr(document, "_id") and "_id" not in document.keys():
			raise ValueError, "This document does not have a Mongo ID"
		
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
			
		if self.__encryptDocuments:
			document = self.__encryptDocument(document)
						
		self.__currentCollection.save( document )
		
	def removeDocuments(self, match):
		""" Removes all documents that match the give query. 
		Refer to the [MongoDB documentation](http://docs.mongodb.org/manual/tutorial/query-documents) on this subject for more information on queries.
		
		:param match: A query for the database to match documents to.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
			
		self.__currentCollection.remove(match)
		return True
		
	def getDocuments(self, match, limit=None):
		""" Returns all documents that match the give query, up until `limit` is reached. By default, this will return every single result.
		Refer to the [MongoDB documentation](http://docs.mongodb.org/manual/tutorial/query-documents) on this subject for more information on queries.
		This method will also work if documents are encrypted.
		
		:param match: A query for the database to match documents to.
		:param limit: The maximum amount of documents to return.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
					
		# Auto fix id requests
		if "_id" in match and (isinstance(match["_id"], str) or isinstance(match["_id"], unicode)):
			match["_id"] = ObjectId(match["_id"])			
			
		if self.__encryptDocuments:
			match = self.__encryptDocument(match)
			
		if limit is None:
			documents = self.__currentCollection.find(match)
		else:
			documents = self.__currentCollection.find(match).limit(limit)
		
		if self.__encryptDocuments:
			return [self.__decryptDocument(d) for d in documents]
		else:
			return list(documents)
		
	def __del__(self):
		""" Gracefully closes the connection to the server when this singleton is deleted. """
		self.__client.close()
		
# Testing Plain Database
		
def test_Storage(encryptDocuments=False):
	storage1 = Storage(encryptDocuments=True)
	storage2 = Storage(encryptDocuments=False)
	assert storage1 == storage2, "Storage is not a singleton"
	
def test_getHost():
	storage = Storage(encryptDocuments=False)
	storage.getHost()
	
def test_getPort():
	storage = Storage(encryptDocuments=False)
	storage.getPort()
	
def test_reconnect():
	storage = Storage(encryptDocuments=False)
	# Temporarily set the Config details to a different server, without saving the Config.
	Config().MongoServer = 	"127.0.0.1:27017"
	# The storage details should not yet have changed.
	assert Config().MongoServer != "%s:%s" % (storage.getHost(), storage.getPort())
	storage.reconnect()
	# The storage details should have changed.
	assert Config().MongoServer == "%s:%s" % (storage.getHost(), storage.getPort())
	
def test_isAlive():
	storage = Storage(encryptDocuments=False)
	assert storage.isAlive(), "The connection has failed for some reason"
	
def test_getDatabase():
	storage = Storage(encryptDocuments=False)
	
def test_getCollection():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	
def test_insertDocument():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.insertDocument({"name":"test_document"})
	
def test_getDocuments():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	assert len(storage.getDocuments({"name":"test_document"})) > 0, "Document was not inserted."
	
def test_saveDocument():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	
	doc = {"name":"test_document_save", "version":1}
	storage.insertDocument(doc)
	ndoc = storage.getDocuments({"name":"test_document_save"})[0]
	ndoc["version"] = 2
	storage.saveDocument(ndoc)
	assert len(storage.getDocuments({"name":"test_document_save"})) == 1, "Document was duplicated."
	assert storage.getDocuments({"name":"test_document_save"})[0]["version"] == 2, "Document was not saved properly"
	
def test_removeDocuments():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.removeDocuments({"name":"test_document"})
	storage.removeDocuments({"name":"test_document_save"})
	
def test_dropCollection():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.dropCollection("test_collection")
	
def test_dropDatabase():
	storage = Storage(encryptDocuments=False)
	storage.getDatabase("test_database")
	storage.dropDatabase("test_database")
	
# Testing Encrypted Database	

def test_padObject():
	storage = Storage()
	assert storage._Storage__padObject("A") == "A{<type 'str'>{{"
	assert storage._Storage__padObject(1) == "1{<type 'int'>{{"
	assert storage._Storage__padObject(1.0) == "1.0{<type 'float'>{{{{{{{{{{{{{{"

def test_unpadString():
	storage = Storage()
	assert storage._Storage__unpadString("A{<type 'str'>{{") == "A"
	assert storage._Storage__unpadString("1{<type 'int'>{{") == 1
	assert storage._Storage__unpadString("1.0{<type 'float'>{{{{{{{{{{{{{{") == 1.0

def test_Encrypted_insertDocument():
	storage = Storage()
	storage.getDatabase("test_Encrypted_database")
	storage.getCollection("test_Encrypted_collection")
	storage.insertDocument({"name":"test_Encrypted_document"})
	
def test_Encrypted_getDocuments():
	storage = Storage()
	storage.getDatabase("test_Encrypted_database")
	storage.getCollection("test_Encrypted_collection")
	assert len(storage.getDocuments({"name":"test_Encrypted_document"})) > 0, "Document was not inserted."
	
def test_Encrypted_saveDocument():
	storage = Storage()
	storage.getDatabase("test_Encrypted_database")
	storage.getCollection("test_Encrypted_collection")
	
	doc = {"name":"test_Encrypted_document_save", "version":1, "list-test":[1,2,3,4,5,"six"]}
	storage.insertDocument(doc)
	ndoc = storage.getDocuments({"name":"test_Encrypted_document_save"})[0]
	ndoc["version"] = 2
	storage.saveDocument(ndoc)
	assert len(storage.getDocuments({"name":"test_Encrypted_document_save"})) == 1, "Document was duplicated."
	assert storage.getDocuments({"name":"test_Encrypted_document_save"})[0]["version"] == 2, "Document was not saved properly"
	
def test_Encrypted_removeDocuments():
	storage = Storage()
	storage.getDatabase("test_Encrypted_database")
	storage.getCollection("test_Encrypted_collection")
	storage.removeDocuments({"name":"test_Encrypted_document"})
	storage.removeDocuments({"name":"test_Encrypted_document_save"})
	
def test_Encrypted_dropCollection():
	storage = Storage()
	storage.getDatabase("test_Encrypted_database")
	storage.getCollection("test_Encrypted_collection")
	storage.dropCollection("test_Encrypted_collection")
	
def test_Encrypted_dropDatabase():
	storage = Storage()
	storage.getDatabase("test_Encrypted_database")
	storage.dropDatabase("test_Encrypted_database")
