import os, re, base64, urllib2, json, time, random, chardet
from flask import Flask,render_template,abort, Response, request, session, redirect, g
from Yuras.common.TemplateTools import TemplateTools
from Yuras.common.Pandoc import Pandoc

from Yuras.webapp.models.Document import Document
from Yuras.webapp.models.Annotation import Annotation
from Yuras.webapp.models.User import User

from Crypto import Random

templatesFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./templates")
assetsFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./public/assets")
app = Flask(__name__, template_folder=templatesFolder)
app.secret_key = Random.new().read(32)

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
		print token
		
		givenToken = urllib2.unquote( request.form.get('_csrf_token',False) )
		print givenToken
		if not token or token != givenToken:
			abort(403)
			
def generate_csrf_token():
	if '_csrf_token' not in session:
		session['_csrf_token'] = base64.b64encode(Random.new().read(32))
	return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token


# REQUEST TIME #
@app.before_request
def startRequestTimer():
	g.start_time = time.time()
	
@app.after_request
def stopRequestTime(response):
	#print "Request took %s ms." % ((time.time() - g.start_time)*1000), request.endpoint, request.view_args
	return response
		
# ROUTES #

# ERROR PAGES #

@app.errorhandler(403)
def page_not_found(e):
    return render_template('errors/403.html',name="403 - Forbidden"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html',name="404 - Not found"), 404

@app.errorhandler(405)
def page_not_found(e):
    return render_template('errors/405.html',name="405 - Method not allowed"), 405

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html',name="500 - Server error"), 500


# AUTHENTICATION #
@app.route("/login")
def login():
	return render_template("users/login.html", name="Login", active=None)

# AFTER AUTH #

@app.route("/dashboard")
def index():
	users = ["Jan", "Piet", "Klaas", "Yuri"]
	documents = Document().matchObjects(
		{},
		limit=10)
	news = ["First mockup released"]
	return render_template("homepage/index.html", name="Dashboard", users=users, documents=documents, news=news, active="dashboard")

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

# DOCUMENTS #

@app.route("/documents/")
def documentsIndex():
	documents = Document().matchObjects(
		{},
		limit=25)
	return render_template("documents/index.html", name="Documents overview", documents=documents, active="documents")

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
	except Exception as e:
		return abort(404)
	
	annotations = Annotation().getObjectsByKey("document", id)
	
	markedContainer = ("<samp type='marked'>","</samp>")
	#markedContainer = ("[[[[","]]]]")
	#markedContainer = ("","")
	markedContainerLength = sum([len(mC) for mC in markedContainer])
	
	annotations.sort(key=lambda a: a.location[0])
	
	for a,annotation in enumerate(annotations):
		start, length = annotation.location
		start += markedContainerLength*a
		
		before_string = document.contents[:start]
		after_string = document.contents[start+length:]
		
		document.contents = "".join([before_string, markedContainer[0], document.contents[start:start+length], markedContainer[1],after_string ])
		
	document.contents = Pandoc().convert("markdown_github", "html", document.contents.encode("utf-8"))
	document.contents = document.contents.replace(markedContainer[0], "<span class='marked'>").replace(markedContainer[1], "</span>")
	
	return render_template("documents/viewer.html", name="Document", document=document, annotations=annotations, active="documents")

@app.route("/documents/<id>/save",methods=["POST"])
def documentSave(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		document = None
	
	if request.method != "POST":
		return abort(405)
	
	contents = urllib2.unquote( request.form.get("contents","").encode('utf-8') )
	contents_escaped = contents
	contents_md = unicode(Pandoc().convert("html","markdown_github",contents_escaped))
	title = urllib2.unquote( request.form.get("title","").encode('utf-8') )
	
	if contents is not "":
		document.contents = contents_md.encode('utf-8')
		document.title = title
		document.save()
	
	annotations = urllib2.unquote( request.form.get("annotations","").encode('utf-8') )
	
	if annotations is not "":
		annotations = json.loads(annotations)
		
		for anno_id, annotation in annotations.items():
			try:
				a = Annotation().getObjectsByKey("_id", anno_id)[0]
			except:
				a = Annotation()
				
			a.contents = annotation["text"].encode('utf-8')
			a.location = [int(i) for i in annotation["location"].split(",")]
			a.document = id
			a.document_title = document.title
			a.selected_text = annotation["selected_text"].encode('utf-8')
			
			# Correct location parameter
			print contents_md[a.location[0]:a.location[0]+a.location[1]], a.selected_text
			if contents_md[a.location[0]:a.location[0]+a.location[1]] != a.selected_text:
				
				i = contents_md.index(annotation["selected_text"],0)
				d = -1

				while i >= 0:
					delta = abs(i-a.location[0])
					print i,d,delta
					if d >= 0 and d < delta:
						break
					
					if d > delta or d < 0:
						d = delta
					
					try:
						ni = contents_md.index(annotation["selected_text"],i+1)
						print ni
					except Exception as e:
						print e
						break
						
					if i == ni:
						break
					else:
						i = ni
						
				print contents_md[i:i+a.location[1]]
				a.location[0] = int(i)
			
			a.save()
	
	if contents is not "":
		return json.dumps( { 
				"success":"true",
				"new_csrf":generate_csrf_token()
			} );
	
	return abort(403)

@app.route("/documents/<id>/delete",methods=["POST"])
def documentDelete(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)
	
	if request.method != "POST":
		return abort(405)
	
	document.remove()
	
	return json.dumps( { 
			"success":"true",
			"new_csrf":generate_csrf_token()
		} );
	
	return abort(403)

@app.route("/documents/<id>/download/<filetype>")
def documentDownload(id, filetype):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)
	
	filetypes = {
		"docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		"pdf":"application/pdf",
		"txt":"text/plain",
	}
	
	if filetype in filetypes:
		responseContents = Pandoc().convert("markdown_github", filetype, document.contents.encode("utf-8"))
		response = Response(responseContents, mimetype=filetypes[filetype])
		
		filename = document.title + "." + filetype
		
		response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
		return response
	else:
		return abort(405)
	
# ANNOTATIONS #

@app.route("/annotations/")
def annotationsIndex():
	annotations = Annotation().matchObjects(
		{},
		limit=25)
	
	return render_template("annotations/index.html", name="Annotations overview", annotations=annotations, active="annotations")
	
@app.route("/annotations/<id>/delete",methods=["POST"])
def annotationDelete(id):
	try:
		annotation = Annotation().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)
	
	if request.method != "POST":
		return abort(405)
	
	annotation.remove()
	
	return json.dumps( { 
			"success":"true",
			"new_csrf":generate_csrf_token()
		} );
	
	return abort(403)

# USERS #
@app.route("/users/")
def usersIndex():
	users = User().matchObjects(
		{},
		limit=25)
	
	return render_template("users/index.html", name="Users overview", users=users, active="users")

@app.route("/users/new")
def userCreate():
	user = User()
	user.save()
	_id = user._id;
	return redirect("/users/%s/edit" % _id)

@app.route("/users/<id>/edit")
def userEdit(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
			
	return render_template("users/edit.html", name="Edit user", user=user, active="users")

@app.route("/users/<id>/delete",methods=["POST"])
def userDelete(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)
	
	if request.method != "POST":
		return abort(405)
	
	user.remove()
	
	return json.dumps( { 
			"success":"true",
			"new_csrf":generate_csrf_token()
		} );
	
	return abort(403)


# USERS - PASSWORD #
with open(os.path.join(assetsFolder, "words.txt")) as wordsFile:
	wordList = [ w.strip("\r ") for w in wordsFile.read().split("\n") if (len(w) > 4 and len(w) < 8) ]
	
@app.route("/users/get-random-words/<n>")
def getRandomWords(n):
	return json.dumps(random.sample(wordList,int(n)))	
	
@app.route("/users/<id>/password/edit")
def userPasswordEdit(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
			
	return render_template("users/password-edit.html", name="Respin password", user=user, active="users")


	
	
	