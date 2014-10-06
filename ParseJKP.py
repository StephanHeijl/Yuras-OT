import sys, os, re, json, shutil, random, math
from pprint import pprint as pp
from bs4 import BeautifulSoup

class JKPParser():
	def __init__(self, inPath, outPath, *args, **kwargs):
		self.inPath = inPath
		self.outPath = outPath
		
		self.documentCount = 0
		self.documents = {}
		
		self.fileNameFilter = kwargs.get("fileNameFilter", ".")
		
	def filterInPath(self):
		fnfPattern = re.compile(self.fileNameFilter)
		
		i = 0
		
		for root, dirs, files in os.walk(self.inPath):
			for file in files:
				if fnfPattern.match(file):
					path = os.path.join(root,file)
					content = self.getContent(path)
					
			i+=1				
			if i > 50:
				#break
				pass
		
		#with open("output.json", "w") as f:
		#	f.write(json.dumps(self.documents, indent=4))
			
		reducedDocuments = self.reduceDepth(self.documents)
		
		#with open("output-reduced.json", "w") as f:
		#	f.write(json.dumps(reducedDocuments, indent=4))
			
		self.divideAndSave(reducedDocuments)
					
					
	def getContent(self, path):
		contentSelector = ".content-box-content"
		
		with open(path) as openHTML:
			html = openHTML.read()
		
		soup = BeautifulSoup(html)		
		
		contentBox = soup.select(contentSelector)[0]
		if "Nieuw document plaatsen" in contentBox.get_text():
			return False
		
		
		for link in soup.select(".content-subbox a"):
			linkText = unicode.encode(link.get_text(),errors="ignore")
			if linkText == "Bekijk het document.":
				docname = os.path.join( os.path.dirname(path), link["href"])
				directory = os.path.dirname( docname )
				directory = re.sub("^"+self.inPath+"[\\\/]*", "", directory)
				category = re.split("[\\\/]+", directory)
				
				print docname
				self.addDocument(category, docname)
				self.documentCount += 1
					
		return True
			
	def addDocument(self, keys, value):
		currentIndex = self.documents
		for i,key in enumerate(keys):
			if key not in currentIndex and i < len(keys)-1:
				currentIndex[key] = {}
			if key not in currentIndex and i == len(keys)-1:
				currentIndex[key] = []
			
			currentIndex = currentIndex[key]
			
		currentIndex.append(value)
		
	def reduceDepth(self, dictionary):
		newDict = {}
		for key in dictionary:
			if key == "strafrecht": # Such a broad term, it needs an exception
				for k in dictionary[key]:
					newDict["%s-%s" % (key,k)] = self.walk(dictionary[key][k]) # We still want a single level to reduce complexity
			else:
				newDict[key] = self.walk(dictionary[key])
		return newDict
			
	def walk(self,node):
		if isinstance(node,list):
			return node
		
		foundItems = []
		for key, item in node.items():
			if isinstance(item,dict):
				self.walk(item)
			else:
				foundItems+=item
		return foundItems
		
	def divideAndSave(self,directories):
		for key in directories:
			learndirectory = os.path.join(self.outPath+"-learn",key)
			testdirectory  = os.path.join(self.outPath+"-test",key)
			
			try:
				os.makedirs(learndirectory)
			except:
				pass
			
			try:
				os.makedirs(testdirectory)
			except:
				pass
			
			documents = directories[key]
			random.shuffle(documents)
			splitAt = int(math.floor(len(documents)*0.9))
			
			for i, document in enumerate(documents):
				print document
				if i < splitAt:
					newPath = os.path.join(learndirectory, os.path.basename(document))
				else:
					newPath = os.path.join(testdirectory, os.path.basename(document))
				
				if not re.match(".+?\.txt?$", newPath):
					newPath += ".txt"
				
				with open(document) as html:
					html = html.read()
					soup = BeautifulSoup(html)	
					
					text = soup.select(".content-box-content")[0].get_text()
					text = unicode.encode(text,errors="ignore")
					
					output = open(newPath,"w")
					output.write(text)
					output.close()
				
			
		
if __name__ == "__main__":
	jkpp = JKPParser(sys.argv[1],sys.argv[2],fileNameFilter=".+?d47e.html$")
	jkpp.filterInPath()
	print "Documents: %s"  % jkpp.documentCount