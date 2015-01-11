""" Document finding and parsing consolidated into a neater class form. """

from Yuras.common.Pandoc import Pandoc

import json, os, argparse, re

class ParseModule():
	def __init__(self):
		self.categories = []
		self.files = []
		self.mappedData = {}
		self.argparser = argparse.ArgumentParser(description='Parse a directory full of files.')
		self.parseArguments()
		
	def parseArguments(self):
		self.argparser.add_argument("--in", type=str, help="The directory to walk.", required=True)
		self.argparser.add_argument("--out", type=str, help="The JSON file to ouput the parsed categories/file map to.")
		self.argparser.add_argument("--pretty", help="Output is indented and neatly formatted",action='store_true')
	
	def walkDirectory(self, path):		
		href = re.compile("href=\"([^\.].+?\.html)")
		
		if path is None:
			raise ValueError, "Need a path"
		for root, dirs, files in os.walk(path):
			category = root.split(os.path.sep)
			
			for f in files:
				with open( os.path.join(root, f) ) as html:
					contents = html.read().decode(errors="ignore")
					
					if "bevat binnen het geselecteerde onderwerp nog geen" in contents:
						continue
					
					urls = href.findall(contents)
					for url in urls:
						u = url
						if u.startswith("http") or "#" in u or "-" not in u or ">" in u:
							continue
						try:
							self.addDocument( os.path.join(root.replace("jurisprudence","wiki"),u))
						except Exception as e:
							print e
							pass
					
						
						
	def addDocument(self, path):
		md = self.mappedData
		pandoc =  Pandoc()
		category = os.path.dirname(path).split(os.path.sep)
		for c in category:
			if len(c) == 0:
				continue
			if c not in md.keys():
				md[c] = {}
			md = md[c]
			
		with open( path ) as html:
			contents = html.read()
			splitOne = '<div class="content-box-content">'
			splitTwo = '</div>'
			
			contents = contents.split(splitOne)[1]
			contents = contents.split(splitTwo)[0]
			
			if "binnen het geselecteerde onderwerp" in contents:
				return None
				
			if len(contents.strip("\n \t")) == 0:
				return None
									
			markdown = pandoc.convert("html","plain",contents)
			
			md[path] = markdown
	
	def export(self, out=None, pretty=False):		
		indent = None
		if pretty:
			indent = 4
		if out is None:
			print json.dumps(self.mappedData,indent=indent)
		else:
			with open(out,"w") as output:
				json.dump(self.mappedData,output,indent=indent)
	
if __name__ == "__main__":
	pm = ParseModule()
	args = vars( pm.argparser.parse_args() )
	
	pm.walkDirectory(args.get("in", None))
	pm.export(args.get("out", None),args.get("pretty",False))	
	