"""
@name Singleton
@author Stephan Heijl
@module core
@version 0.1.0
"""

class Singleton(object):
	""" The base singleton class for Olympus. """
	
	_instance = None
	def __new__(cls, *args, **kwargs):
		""" This returns the existing instance of the class every time an attempt is made to instantiate it. """
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(
								cls, *args, **kwargs)
								
		cls.instantiated = False
		""" Is true if this object has already been instantiated once. """
		return cls._instance