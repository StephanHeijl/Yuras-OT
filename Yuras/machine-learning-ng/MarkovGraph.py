from graph_tool.all import *
import pprint, random, re

class MarkovGraph():
	def __init__(self):
		self.text = ""
		self.tokens = []
	
	def getfile(self):
		with open("wbvstrafrecht.txt") as f:
			self.text = f.read()[:10000]
			
	def tokenize(self):
		text = self.text.replace(".", " . ")
		text = text.replace(",", " , ")
		tokens = re.split("[^a-zA-Z\,\.]", text.lower())
		self.tokens = [t for t in tokens if t!=""]
		print "Found",len(self.tokens),"tokens"
		
	def chain(self):
		chain = {}
		for t, token in enumerate(self.tokens):
			if token not in chain:
				chain[token] = {"total":0,"tokens":{}}
			try:
				nextt = self.tokens[t+1]
			except:
				continue
			if nextt not in chain[token]["tokens"]:
				chain[token]["tokens"][nextt] = 0
			chain[token]["tokens"][nextt]+=1
			chain[token]["total"]+=1
					
		nchain = {}
		for token in chain:
			nchain[token] = []
			total = float(chain[token]["total"])
			sortedNTokens = sorted(chain[token]["tokens"].items(), key=lambda t:t[1], reverse=True)
			for t,v in sortedNTokens:
				nchain[token].append((t,v/total))
				
		self.chain = nchain
		
	def creategraph(self):
		G = Graph()
		weights = []
		vertices = {}
		
		wordprop = G.new_vertex_property('string')
		weightprop = G.new_edge_property('double')
			
		for source,destinations in self.chain.items():
			sourcelabel = "".join([l for l in source if ord(l) < 128])
			if sourcelabel not in vertices:
				vertices[sourcelabel] = G.add_vertex()
				wordprop[vertices[sourcelabel]] = sourcelabel
			
			for dest, score in destinations:
				destlabel = "".join([l for l in dest if ord(l) < 128])
				if destlabel not in vertices:
					vertices[destlabel] = G.add_vertex()
					wordprop[vertices[destlabel]] = destlabel
					
				edge = G.add_edge(vertices[sourcelabel], vertices[destlabel])
				weightprop[edge] = score
				
				
				weights.append(score)		
		
		self.vertices = vertices
		return G, wordprop, weightprop
	
	def traverseGraph(self, g, wordprop, weightprop):
		target,destination = random.sample(self.vertices.values(),2)
		currentVertex = target
		maxSteps = 100
		step = 0
		chain = []
		
		while currentVertex != destination and step< maxSteps:
			step+=1
			edges = sorted( [(edge.target(), weightprop[edge]) for edge in currentVertex.out_edges() ], key=lambda e: e[1], reverse=True)
			choices = []
			for edge in edges:
				for e in range(int(edge[1]*100)+1):
					choices.append(edge)
			currentVertex = random.choice(choices)[0]
			chain.append( wordprop[currentVertex] )
			
		cap = True
		description = ""
		for word in chain:
			word = " "+word
			if cap:
				word = word[0].upper() + word[1:]
				cap = False
			if word[1] in [".",","]:
				word = word[1]	
				if word == ".":
					cap = True
			description+= word
			
		print description
		
		
	def drawGraph(self, G, wordprop, weightprop):		
		pos = sfdp_layout(G, eweight=weightprop, C=5, verbose=True)
		graph_draw(G, pos=pos, output="graph.pdf")
			
if __name__ == "__main__":
	mg = MarkovGraph()
	mg.getfile()
	mg.tokenize()
	mg.chain()
	graph, wordprop, weightprop = mg.creategraph()
	mg.traverseGraph(graph, wordprop, weightprop)
	#mg.drawGraph(graph, wordprop, weightprop)
	