import os, threading, inspect, argparse
from Yuras.common.Config import Config
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask.ext.compress import Compress

from flask import Flask, render_template, abort, Response, request, redirect, url_for
from Yuras.webapp.routes import app

class Server(threading.Thread):
	def __init__(self):	
		self.argparser = argparse.ArgumentParser(description='Start a Yuras instance.')
		self.parseArguments()
		
		args = vars( self.argparser.parse_args() )
		
		self.PORT = args.get("port", 5000)
		self.CONFIG = args.get("config", None)
		super(Server, self).__init__()		
		
	def parseArguments(self):
		self.argparser.add_argument("--config", type=str, help="The config file to load.", required=False)
		self.argparser.add_argument("--port", type=int, help="The port to launch this server on.", default=5000, required=False)
	
	def checkWorkingDirectory(self):
		""" Checks the working directory and sets it to the webapp directory if needed. """
		print ("Current working directory: '%s'" % os.getcwd())
		startScriptDir = os.path.dirname(os.path.realpath(__file__))
		print ("Desired working directory: '%s'" % startScriptDir)
		if (os.getcwd() != startScriptDir):
			print("Changing working directory to: '%s'" % startScriptDir)
			os.chdir(startScriptDir)
	
	def storeWebAppDirectories(self):
		""" Stores the webapp directories into the config. """
		Config().WebAppDirectory = os.path.join(os.getcwd())
		Config().TemplatesDirectory = os.path.join(os.getcwd(), "templates") 
		Config().save()

	def startCompressed(self):
		""" This is a version of the server optimized for remote ends. The plaintext data is compressed before it is sent out for better transfer speeds."""
		
		print ("Starting Yuras Tornado HTTP Server")
		print ("----------------------------------")
		Config(self.CONFIG) # Initialize the Config before switching to the webapp directory to make sure it gets loaded correctly.

		self.checkWorkingDirectory()	
		self.storeWebAppDirectories()	
		
		print ("Starting on port %s..." % self.PORT)

		# Compress all plaintext communications
		Compress(app)
		app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript', 'image/svg+xml']
		app.config['COMPRESS_DEBUG'] = True
		
		serverStarted = False
		while not serverStarted and self.PORT < 10000:
			# Try adding 1 to the port every time we can't listen on the preferred port.
			try:
				http_server = HTTPServer(WSGIContainer(app))
				http_server.bind(self.PORT)
				http_server.start(0)
				IOLoop.instance().start()
				serverStarted = True
			except Exception as e:
				print e
				self.PORT +=1

	def startLocal(self):
		print ("Starting Yuras Tornado HTTP Server (LOCAL)")
		print ("------------------------------------------")
		Config(self.CONFIG) # Initialize the Config before switching to the webapp directory to make sure it gets loaded correctly.

		self.checkWorkingDirectory()	
		self.storeWebAppDirectories()
		
		serverStarted = False
		while not serverStarted and self.PORT < 10000:
			# Try adding 1 to the port every time we can't listen on the preferred port.
			try:
				print ("Starting on port %s..." % self.PORT)
				http_server = HTTPServer(WSGIContainer(app))
				http_server.bind(self.PORT)
				http_server.start(0)
				IOLoop.instance().start()
				serverStarted = True
			except Exception as e:
				print e
				self.PORT +=1
		
	def run(self):
		#self.startLocal()
		self.startCompressed()
	
if __name__ == "__main__":
	Server().run()
	
# TESTS #

def test_checkWorkingDirectory():
	s = Server()
	s.checkWorkingDirectory()
	startScriptDir = os.path.dirname(os.path.realpath(__file__))
	assert startScriptDir == os.getcwd() , "Something went wrong whilst changing working directories."
	
def test_storeWebAppDirectories():
	s = Server()
	s.storeWebAppDirectories()
	assert hasattr(Config(), "RootDirectory")