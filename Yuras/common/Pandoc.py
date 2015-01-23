# -*- coding: utf-8 -*-
import subprocess, tempfile, os

class Pandoc():
	""" Provides basic integration with pandoc for text conversion."""
	def __init__(self):
		self.baseCommand = "pandoc -f {from} -t {to} < {text}"
		self.fileOutputCommand = "pandoc -f {from} -t {to} -o {outputpath} < {text}"
		
	def convert(self, from_, to_, text):
		""" Converts a string from one format to another, returns the result.
		
:param from_: The initial format.
:param to_: The desired format.
:param text: The string to convert.
:returns: The converted result as a string.
		"""
		
		tmp = tempfile.NamedTemporaryFile(delete=False)
		try:
			tmp.write( text )
		except:
			tmp.write( text.encode('utf-8') )
			
		tmp.close()
		
		formatDict = {"from":from_, "to":to_, "text":tmp.name}
		command = self.baseCommand.format(**formatDict)
		pdp = subprocess.Popen(command,shell=True,executable='/bin/bash',stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		result = pdp.communicate()
		
		if "pandoc: Cannot write {to} output to stdout.".format(**formatDict) in result[1]:
			tmpout = tempfile.NamedTemporaryFile(delete=False)
			tmpout.close()
			formatDict["outputpath"] = tmpout.name
			command = self.fileOutputCommand.format(**formatDict)
			pdp = subprocess.Popen(command,shell=True,executable='/bin/bash',stdout=subprocess.PIPE)
			pdp.communicate()[0]
			with open(tmpout.name,"rb") as tmpoutFile:
				result = tmpoutFile.read()
			os.unlink(tmpout.name)
		else: 
			result = result[0]
			
		os.unlink(tmp.name)
		try:
			return result.decode('utf-8')
		except:
			return result
# TESTING #
def test_convert():
	p = Pandoc()
	result = p.convert("html", "markdown", "<h1>Index</h1><br/><h2>test</h2>")
	desiredResult = r"""Index
=====

\

test
----
"""
	assert result == desiredResult