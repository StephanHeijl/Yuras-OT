from Yuras.common.Singleton import Singleton
import json, os, sys

class Config(Singleton):
	""" Config is a Singleton that persistently stores settings and configurations for guardStore. 
	When called upon, it will export these to the configuration file for later retrieval.
	Among other things, it stores your username, your email for Entrez notifications and the enabled guardStore modules.
	The configuration files are set to be stored in a 'pretty' format, so as to be easily human-readable and -editable.
	"""
	
	def __init__(self):
		if self.instantiated:
			return 
		currentDir = os.path.dirname(__file__)
		# guardStore.conf is the configuration file that is loaded for guardStore
		guardStoreConfName = "../GuardStore.conf"
		guardStoreConfPath = os.path.abspath(os.path.join(currentDir,guardStoreConfName))
		# Default.conf is loaded if guardStore.conf is not available.
		# It provides a safe fallback for testing purposes. If you are setting up your
		# own guardStore you should copy this and work from there.
		defaultConfName = "./default.conf"
		defaultConfPath = os.path.abspath(os.path.join(currentDir,defaultConfName))
		
		self.configFileName = ""
		""" This attribute stores the location where the configuration is to be saved. """
		
		if os.path.exists(guardStoreConfPath):
			self.setConfig(json.load( open(guardStoreConfPath, "r") ))
			self.configFileName = guardStoreConfPath
		else:
			try:
				self.setConfig(json.load( open(defaultConfPath, "r") ))
				self.configFileName = defaultConfPath
			except:
				raise IOError, "No default configuration file found, you need a configuration file to use this module."
		
		self.applyConfig()
		self.instantiated = True
		""" Is true if this object has already been instantiated once. """
		
	def clear(self):
		""" Clears the Config instance from any and all attributes """
		self.__dict__ = {}
		
	def delete(self, key):
		""" Deletes a single key and its respective value from the Config
		
		:param key: The attribute that should be removed.
		"""
		delattr(self, key)
		
	def setConfig(self, config):
		""" Adds a while dictionary to set as a configuration file.
		After it has been set it should still be applied with `applyConfig()`.
		This will overwrite any attributes with the same key.
		
		:param config: The dictionary that should be set for the configuration. """
		self.conf = config
		
	def applyConfig(self):
		""" Applies the configuration dictionary that was set with `setConfig()`. 
		
		:rtype: returns True if the configuration was set successfully. False if otherwise."""
		if not hasattr(self, "conf"):
			return False
		
		for key,value in self.conf.items():
			setattr(self, key, value)
			
		del self.conf
		return True
			
	def addAttribute(self, key, value=None):
		""" Adds an attribute to the Config. 
		If the key does not yet exist, it will be added to the Config and placed in a list.
		If the key already exists and is not a list, it will be converted to a list containing the original value and the new value.
		
		:param key: The key of the attribute
		:param value: The value that will be added.
		"""
		
		if key not in self.__dict__:
 			if value!=None:
 				setattr(self, key, [value])
 			else:
 				setattr(self, key, {})
  		else:
  			if isinstance(self.key, list):
  				self.key.append(value)
  			else:
  				self.key = [self.key, value]
	
	def getAttributes(self):
		""" Returns all the attributes currently in this Config.
			
		:rtype: A dictionary containing all the attributes in this Config.
		"""
		return self.__dict__
	
	def save(self):
		""" Saves the Config to the file it was initialized from. By default, this is `default.conf`. """
		confFile = open(self.configFileName, "w")
		# Store the configFileName attribute to make sure it won't be stored in the configuration file.
		configFileName = self.configFileName
		del self.configFileName
		json.dump(self.getAttributes(), confFile, sort_keys=True, indent=4, separators=(',', ': '))
		confFile.close()
		self.configFileName = configFileName

def test_Config():
	c = Config()
	assert c.__dict__["username"] == c.username
	assert c.username == "default" or c.username == "guardstore"

def test_addAttribute():
	c = Config()
	c.addAttribute("a", "b")
	print c.a
	assert c.a == ["b"]

def test_getAttributes():
	c = Config() # Config is a singleton so the 'a' value should have been carried over.
	assert c.getAttributes()["a"] == ["b"]
	
def test_save():
	c = Config()
	c.save()
	print c.configFileName
	assert False
	
def test_clear():
	c = Config()
	c.clear()
	assert not hasattr(c, "a")
	
def test_save():
	c = Config()
	oldName = c.configFileName
	nameParts = c.configFileName.split("/")
	newName = "/".join(nameParts[:-1]) + "/test.conf"
	c.configFileName = newName
	c.save()
	os.remove(newName)
	c.configFileName = oldName
