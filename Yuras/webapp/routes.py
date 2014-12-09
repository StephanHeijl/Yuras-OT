import os, re, base64, urllib, json
from flask import Flask,render_template,abort, Response, request, session, redirect
from Yuras.common.TemplateTools import TemplateTools
from Yuras.common.Pandoc import Pandoc

from Yuras.webapp.models.Document import Document

from Crypto import Random

templatesFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./templates")
assetsFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./public/assets")
app = Flask(__name__, template_folder=templatesFolder)
app.secret_key = "tVblvH7yuM6P5tBT8D9DFI6bvHX3xu5U"

# LOAD TEMPLATE TOOLS #
tools = TemplateTools()
for attribute in dir(tools):
	if not attribute.startswith("__") and hasattr(getattr(tools, attribute), "__call__"):
		app.jinja_env.globals[attribute] = getattr(tools, attribute)

# CSRF PROTECTION #
@app.before_request
def csrf_protect(*args, **kwargs):
   	if request.method == "POST":
		token = session.pop('_csrf_token', None)
		givenToken = urllib.unquote( request.form.get('_csrf_token') )
		if not token or token != givenToken:
			abort(403)
			
def generate_csrf_token():
	if '_csrf_token' not in session:
		session['_csrf_token'] = base64.b64encode(Random.new().read(32))
	return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token
		
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
		"jpg" : "image/jpeg"
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

@app.route("/documents/new")
def documentNew():
	doc = Document()
	doc.save()
	_id = doc._id
	return redirect("/documents/%s" % _id)

@app.route("/documents/<id>")
def documentViewer(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
		document.contents = Pandoc().convert("markdown", "html", document.contents.replace("\"", r"\""))
	except:
		return abort(404)
		
	return render_template("documents/viewer.html", name="Document", document=document)

@app.route("/documents/<id>/save",methods=["POST"])
def documentSave(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		document = None
	
	if request.method != "POST":
		return abort(405)
	
	contents = urllib.unquote( request.form.get("contents",None) )
	contents_escaped = contents.replace("\"", r"\"").strip(" \n\t")
	contents_md = Pandoc().convert("html","markdown",contents_escaped)
	
	print contents
	print contents_md
	
	if contents is not None:
		document.contents = contents_md
		document.save()
		return json.dumps( { 
			"success":"true",
			"new_csrf":generate_csrf_token()
		} );
	return abort(403)