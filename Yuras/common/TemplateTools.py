from Yuras.common.Singleton import Singleton
from Yuras.common.Config import Config

import json, os

class TemplateTools(Singleton):
	""" This class contains a variety of functions that are useful when rendering templates.
		Yuras loads all these methods into the Jinja2 template environment by default. """
	
	def __init__(self):
		self.deferredJavascript = []
		#if self.instantiated:
		#	return
		self.localizationDict = None
		
	def deferJS(self, url, position=0):
		""" Defers loading a script to when the page has loaded, in the order defined by `position`. 
		
		:param url: The URL of the script.
		:param position: The position in the order of scripts to load. Use this to make sure libraries load later than scripts using them.
		:rtype: An empty string.
		"""
		
		self.deferredJavascript.append( ( "<script src='%s'></script>" % (url), position ) )
		return ""
		
	def deferInlineJS(self, string, position=0):
		""" Defers loading a script to when the page has loaded, in the order defined by `position`. 
		
		:param url: The URL of the script.
		:param position: The position in the order of scripts to load. Use this to make sure libraries load later than scripts using them.
		:rtype: An empty string.
		"""
		
		self.deferredJavascript.append( ( "<script>%s</script>" % (string), position ) )
		return ""
		
	def renderJS(self, clearDeferred=True):
		""" Renders all the deferred Javascript scripts that were added by deferJS. They will be rendered in the order of their position, or when their positions are the same, based on the order they were inserted in.
		
		:param clearDeferred: By default, this methods clears all the deferred scripts that have been added. You can retain them by setting this to False. Please note that not clearing them will result in the deferred scripts persisting throughout the life of the server process, possibly accumulating a large amount of memory space.
		:rtype: A string of <script> tags in their defined order.
		"""		

		seen = set()
		dJS = []		
		for url, position in self.deferredJavascript:
			if url not in seen:
				dJS.append((url,position))
				seen.add(url)
		
		dJS.sort(key=lambda s: s[1])
		
		html = []
		for script, pos in dJS:
			html.append( script )
			
		if clearDeferred:
			self.deferredJavascript = []
			
		return "\n".join(html)
	
	def translate(self, key, language="default"):
		""" Takes a phrase and translates it to a given language based on the internationalization file. """		
		localizationPath = os.path.join( Config().WebAppDirectory, "../..", "localization.json")
		if self.localizationDict is None:
			with open(localizationPath, "r") as ld:
				self.localizationDict = dict(json.load(ld))
		
		if language == "default":
			language = Config().language
			
		if language == "en_US":
			return key
				
		translation = self.localizationDict.get(language, {}).get(key, key+"**")
		if translation.endswith("**") and language in self.localizationDict:
			self.localizationDict[language][key+"**"] = "NEEDSTRANSLATION"
			with open(localizationPath, "w") as ld:
				json.dump(self.localizationDict, ld, indent=4)	
		
		return translation
	
	def _(self, *args, **kwargs):
		""" Translate alias """
		return self.translate(*args, **kwargs)
	
	def is_dict(self, v):
		return isinstance(v, dict)
		
		
# TESTING #

def test_deferJS():
	tt = TemplateTools()
	tt.deferJS("test.js")
	assert len(tt.deferredJavascript) == 1
	
def test_renderJS():
	tt = TemplateTools()
	tt.deferJS("test.js")
	assert tt.renderJS(False) == "<script src='test.js'></script>"
	assert tt.renderJS(True) == "<script src='test.js'></script>"
	
def test_is_dict():
	tt = TemplateTools()
	assert tt.is_dict({})
	assert not tt.is_dict("")
	