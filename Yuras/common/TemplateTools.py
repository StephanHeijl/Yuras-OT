from Yuras.common.Singleton import Singleton

class TemplateTools(Singleton):
	""" This class contains a variety of functions that are useful when rendering templates.
		Yuras loads all these methods into the Jinja2 template environment by default. """
	
	def __init__(self):
		self.deferredJavascript = []
		
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
	