from graph_tool.all import *
import pprint, random, re, time

class MarkovGraph():
	def __init__(self):
		self.text = ""
		self.tokens = []
		with open("stopwords.txt") as stopwords:
			self.stopwords = stopwords.read().split("\n")
	
	def getfile(self):
		with open("wbvstrafrecht.txt") as f:
			self.text = f.read()[:100000]
			
	def tokenize(self):
		text = self.text.replace(".", " . ")
		text = text.replace(",", " , ")
		tokens = re.split("[^a-zA-Z\,\.]", text.lower())
		self.tokens = [t for t in tokens if t!="" and t not in self.stopwords]
		print "Found",len(self.tokens),"tokens"
		
		
	def graphTokens(self, rootName="*"):
		G = Graph()
		root = G.add_vertex()
		
		wordprop = G.new_vertex_property('string')
		weightprop = G.new_edge_property('int')
		
		currentVertex = root
		wordprop[root] = rootName
		
		for token in self.tokens:
			if token in [",","."]:
				currentVertex = root
				continue
			
			foundVertex = False			
			
			for e in currentVertex.out_edges():
				if wordprop[e.target()] == token:
					currentVertex = e.target()
					weightprop[e] += 1
					foundVertex = True
					break
			
			if foundVertex:
				continue
			
			v = G.add_vertex()
			wordprop[v] = token
			e = G.add_edge(currentVertex, v)
			currentVertex = v
			weightprop[e] = 1
			
		self.graph = G
		self.wordprop = wordprop
		self.weightprop = weightprop
			
	def visGraph(self):
		G = self.graph
		pos = radial_tree_layout(G, 0)
		graph_draw(G, pos=pos, output="graph.png",output_size=(10000, 10000))
		
	def findWord(self, word):
		wordprop = self.wordprop
		weightprop = self.weightprop
		G = self.graph
		
		results = []
		
		for i in range(len(self.tokens)):
			try:
				v = G.vertex(i)
				wprop = wordprop[v]
			except:
				break
				
			if wprop == word:
				results.append( {"v":v} )

		return results
		
		
	def constructSentence(self, word):
		results = self.findWord(word)
		root = self.graph.vertex(0)
		sentence = []
		
		for result in results:
			v = result["v"]
			currentVertex = v

			while currentVertex!=root:
				sentence.append( self.wordprop[currentVertex])
				for e in currentVertex.in_edges():
					currentVertex = e.source()
					
			sentence.reverse()
			
			outedges = [e for e in currentVertex.out_edges()]
			while len(outedges) > 0:
				edges = [(e,self.weightprop[e]) for e in outedges]
				edges.sort(key=lambda e: e[1], reverse=True)
				currentVertex = edges[0][0].target()
				print currentVertex
				sentence.append(self.wordprop[currentVertex])
				outedges = [e for e in currentVertex.out_edges()]
					
			print " ".join(sentence)
			
			print 
				
				
				
			
if __name__ == "__main__":
	mg = MarkovGraph()
	mg.getfile()
	mg.tokenize()
	
	mg.graphTokens(rootName="*")
	mg.constructSentence("wet")
	
	mg.visGraph()
	
	#mg.chain()
	
	
	
	#graph, wordprop, weightprop = mg.creategraph()
	#mg.traverseGraph(graph, wordprop, weightprop)
	#mg.drawGraph(graph, wordprop, weightprop)
	