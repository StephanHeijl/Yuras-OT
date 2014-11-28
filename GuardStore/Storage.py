"""
This module was originally programmed for Olympus, but can now be used as a component for Yuras.
"""

from Yuras.GuardStore.Singleton import Singleton
from Yuras.GuardStore.Config import Config
from pymongo import MongoClient

class Storage(Singleton):
	""" The storage module provides a layer of abstraction over PyMongo. 
		This will allow us to, if needed, exchange the databases without breaking countless modules 
		that are dependent on database access.
	"""
	def __init__(self):
		""" Initializes the connection with the Mongo database. 
		As this is a Singleton, this is only done **once** per instance of Olympus resulting in lower connection time overhead (unless `reconnect` is called.)
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
		
		:param collection: The name the collection that is to be accessed.
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
		
	def insertDocuments(self, document):
		""" Inserts a document into the currently selected collection in the currently selected database.
		Will throw a ValueError if no database or collection has been selected.
		
		:param document: A dictionary that will be stored as a document. Its contents can include strings, numbers and several types of native objects, like `datetime`.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
			
		self.__currentCollection.insert( document )
		
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
		
		:param match: A query for the database to match documents to.
		:param limit: The maximum amount of documents to return.
		"""
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
		
		if limit is None:
			return self.__currentCollection.find(match)
		else:
			return self.__currentCollection.find(match).limit(limit)
			
	def __del__(self):
		""" Gracefully closes the connection to the server when this singleton is deleted. """
		self.__client.close()
		
def test_Storage():
	storage1 = Storage()
	storage2 = Storage()
	assert storage1 == storage2, "Storage is not a singleton"
	
def test_getHost():
	storage = Storage()
	storage.getHost()
	
def test_getPort():
	storage = Storage()
	storage.getPort()
	
def test_reconnect():
	storage = Storage()
	# Temporarily set the Config details to a different server, without saving the Config.
	Config().MongoServer = 	"127.0.0.1:27017"
	# The storage details should not yet have changed.
	assert Config().MongoServer != "%s:%s" % (storage.getHost(), storage.getPort())
	storage.reconnect()
	# The storage details should have changed.
	assert Config().MongoServer == "%s:%s" % (storage.getHost(), storage.getPort())
	
def test_isAlive():
	storage = Storage()
	assert storage.isAlive(), "The connection has failed for some reason"
	
def test_getDatabase():
	storage = Storage()
	
def test_getCollection():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	
def test_insertDocuments():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.insertDocuments({"name":"test_document"})
	
def test_getDocuments():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	assert storage.getDocuments({"name":"test_document"}).count() > 0, "Document was not inserted."
	
def test_saveDocument():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	
	doc = {"name":"test_document_save", "version":1}
	storage.insertDocuments(doc)
	ndoc = storage.getDocuments({"name":"test_document_save"})[0]
	ndoc["version"] = 2
	storage.saveDocument(ndoc)
	assert storage.getDocuments({"name":"test_document_save"}).count() == 1, "Document was duplicated."
	assert storage.getDocuments({"name":"test_document_save"})[0]["version"] == 2, "Document was not saved properly"
	
def test_removeDocuments():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.removeDocuments({"name":"test_document"})
	storage.removeDocuments({"name":"test_document_save"})
	
def test_dropCollection():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.dropCollection("test_collection")
	
def test_dropDatabase():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.dropDatabase("test_database")
	
	
	
	
	