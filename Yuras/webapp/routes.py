import os, re
from flask import Flask,render_template,abort, Response
from Yuras.common.TemplateTools import TemplateTools

from Yuras.webapp.models.Document import Document

templatesFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./templates")
assetsFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./public/assets")
print templatesFolder
app = Flask(__name__, template_folder=templatesFolder)

# LOAD TEMPLATE TOOLS #
tools = TemplateTools()
for attribute in dir(tools):
	if not attribute.startswith("__") and hasattr(getattr(tools, attribute), "__call__"):
		app.jinja_env.globals[attribute] = getattr(tools, attribute)
		
# ROUTES #

@app.route("/")
def index():
	users = ["Jan", "Piet", "Klaas", "Yuri"]
	documents = Document().matchObjects(
		{},
		limit=10)
	news = ["First mockup released"]
	return render_template("homepage/index.html", name="Dashboard", users=users, documents=documents, news=news)

@app.route("/assets/<assettype>/<filename>")
def assets(assettype, filename):
	openModes = {
		"img": "rb",
		"js": "r",
		"css": "r",
	}
	
	mimeTypes = {
		"css" : "text/css",
		"js" : "text/javascript",
		"png" : "image/png",
		"jpg" : "image/jpeg",
	}
	
	path = os.path.join(assetsFolder,assettype,filename)
	
	try:
		with open(path, openModes[assettype]) as asset:
			assetContents = asset.read()
	except Exception as e:
		print e
		return abort(404);
	
	return Response( assetContents, mimetype=mimeTypes.get(filename.split(".")[-1], "text/plain") )

@app.route("/documents/")
def documentsIndex():
	documents = Document().matchObjects(
		{},
		limit=25)
	return render_template("documents/index.html", name="Documents overview", documents=documents)

@app.route("/documents/<id>")
def documentViewer(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		document = None
	return render_template("documents/viewer.html", name="Document", document=document)