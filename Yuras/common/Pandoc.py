# -*- coding: utf-8 -*-
import subprocess, tempfile, os

class Pandoc():
	""" Provides basic integration with pandoc for text conversion."""
	def __init__(self):
		self.baseCommand = "~/.cabal/bin/pandoc {text} -f {from} -t {to}"
		self.fileOutputCommand = "~/.cabal/bin/pandoc {text} -f {from} -t {to} -o {outputpath}"
		
		
		
	def convert(self, from_, to_, text, filetype=None):
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
		if filetype is None:
			command = self.baseCommand.format(**formatDict)
			pdp = subprocess.Popen(command,shell=True,executable='/bin/bash',stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			result = pdp.communicate()
		
		if filetype is not None or "pandoc: Cannot write {to} output to stdout.".format(**formatDict) in result[1]:
			suffix = '' if filetype is None else '.' + (filetype.strip('.')) # Needs a . before the extension
			tmpout = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
			tmpout.close()
			formatDict["outputpath"] = tmpout.name
			command = self.fileOutputCommand.format(**formatDict)
			pdp = subprocess.Popen(command,shell=True,executable='/bin/bash',stdout=subprocess.PIPE)
			print command
			print pdp.communicate()
			with open(tmpout.name,"rb") as tmpoutFile:
				result = tmpoutFile.read()
			os.unlink(tmpout.name)
		else: 
			result = result[0]
			
		if len(result) == 0:
			# Retry with legacy commands
			legacyBaseCommand = "~/.cabal/bin/pandoc -f {from} -t {to} < {text}"
			legacyFileOutputCommand = "~/.cabal/bin/pandoc -f {from} -t {to} -o {outputpath} < {text}"
			if self.baseCommand != legacyBaseCommand:			
				self.baseCommand = legacyBaseCommand
				self.fileOutputCommand = legacyFileOutputCommand
			
				result = self.convert(from_,to_,text, filetype)
			
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