from __future__ import division

import os, re, base64, urllib2, json, time, random, scrypt, collections, math, pprint, random
import multiprocessing, traceback, sys, feedparser

import cPickle as pickle
from functools import wraps, lru_c
from collections import defaultdict

from bson.objectid import ObjectId

from flask import Flask,render_template,abort, Response, request, session, redirect, g, url_for
from flask.ext import login

from Yuras.common.TemplateTools import TemplateTools
from Yuras.common.Pandoc import Pandoc
from Yuras.common.Config import Config

from Yuras.webapp.models.PublicDocument import PublicDocument as Document
from Yuras.webapp.models.Annotation import Annotation
from Yuras.webapp.models.User import User
from Yuras.webapp.models.Category import Category
from Yuras.webapp.models.Case import Case

from sklearn.feature_extraction.text import TfidfVectorizer

from Crypto import Random

from u2flib_server.jsapi import DeviceRegistration
from u2flib_server.u2f import start_register, complete_register, start_authenticate, verify_authenticate

templatesFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./templates")
assetsFolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"./public/assets")
app = Flask(__name__, template_folder=templatesFolder)
app.secret_key = Random.new().read(32)

# AUTH #
login_manager = login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "do_login"

@login_manager.user_loader
def load_user(userid):
	try:
		print "Getting user", userid
		return User().getObjectsByKey("_id", userid)[0]
	except Exception as e:
		print e
		return None

@app.route("/login", methods=["GET", "POST"])
def do_login():
	if login.current_user.is_authenticated():
		return redirect(request.args.get('next') or url_for('index'))

	if request.method == "POST":
		try:
			user = User().getObjectsByKey("username", unicode(request.form.get("username")).lower(),limit=1)[0]
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			user = None
			print "User not found"
			time.sleep(1 + random.random()) # Wait for some time to make sure we don't reveal that the username is not known

		if user is not None and user.checkPassword( urllib2.unquote( request.form.get("password").encode('utf-8') ) ):
			print "Username and password correct"
			login.login_user(user)
			return redirect(request.args.get('next') or url_for('index'))

		print "Password incorrect"

		return render_template("/users/login.html", name="Log in", error="This username/password combination does not exist.")
	else:
		return render_template("/users/login.html", name="Log in")

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
		givenToken = urllib2.unquote( request.form.get('_csrf_token',False) )
		if not token or token != givenToken:
			print "Incorrect CSRF", token, givenToken
			abort(403)

def generate_csrf_token():
	if '_csrf_token' not in session:
		try:
			session['_csrf_token'] = base64.b64encode(Random.new().read(32))
		except AssertionError:
			Random.atfork()
			session['_csrf_token'] = base64.b64encode(Random.new().read(32))
	return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# REQUEST TIME #
@app.before_request
def startRequestTimer():
	g.start_time = time.time()

@app.after_request
def stopRequestTime(response):
	try:
		print "Request took %s ms." % ((time.time() - g.start_time)*1000), request.endpoint, request.view_args
	except:
		pass
	return response

# ADD USER TO G #
@app.before_request
def addCurrentUser():
	g.current_user = login.current_user

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


# ROUTES #
@app.route("/")
def rootRedirect():
	return redirect(url_for('index'))

@app.route("/dashboard")
@login.login_required
def index():
	users = User().matchObjects({}, limit=5)
	documents = Document().matchObjects(
		{},
		limit=10,
		fields={"title":True, "author":True, "secure":True})
	
	# Parse blog feed
	blogRssUrl = "http://blog.yuras.nl/rss/"
	blogFeed = feedparser.parse(blogRssUrl)
	
	news = {}
	for entry in blogFeed.entries:
		news[entry.link] = entry.title
	
	return render_template("homepage/index.html", name="Dashboard", users=users, documents=documents, news=news, active="dashboard")

@app.route("/assets/<assettype>/<path:filename>")
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
		"svg": "image/svg+xml"
	}
	
	path = os.path.join(assetsFolder,assettype,filename)
	print path
	try:
		with open(path, openModes[assettype]) as asset:
			assetContents = asset.read()
	except Exception as e:
		print e
		return abort(404);

	return Response( assetContents, mimetype=mimeTypes.get(filename.split(".")[-1], "text/plain") )

# DOCUMENTS #
@app.route("/documents/")
@login.login_required
def documentsIndex():
	documents = Document().matchObjects(
		{},
		limit=18,
		fields={"title":True, "_created":True, "author":True, "secure":True, "_id":True}
		)

	categories = Category().matchObjects({})
	return render_template("documents/index.html", name="Documents overview", documents=documents, categories=categories, active="documents")

@app.route("/documents/json/<amount>/<page>")
@login.login_required
def documentsJSON(amount,page):
	fields = {"title":True, "_created":True, "author":True, "secure":True, "_id":True}
	documents = Document().matchObjects(
		{},
		limit=int(amount),
		skip=int(page)*int(amount),
		fields=fields
		)
	return json.dumps([dict([ (f,str(getattr(d,f,None))) for f in fields if fields[f]]) for d in  documents])

@app.route("/documents/table/<amount>/<page>")
@login.login_required
def documentsTable(amount,page):
	fields = {"title":True, "_created":True, "author":True, "secure":True, "_id":True}
	documents = Document().matchObjects(
		{},
		limit=int(amount),
		skip=int(page)*int(amount),
		fields=fields
		)
	return render_template("documents/table.html", documents=documents)

@app.route("/documents/new")
@login.login_required
def documentNew():
	doc = Document()
	doc.author = login.current_user.username
	doc.save()
	_id = doc._id
	return redirect("/documents/%s" % _id)

@app.route("/documents/<id>")
@login.login_required
def documentViewer(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except Exception as e:
		print e
		return abort(404)

	annotations = Annotation().getObjectsByKey("document", id)
	cases = Case().matchObjects({})
	
	categories = Category().matchObjects({})
	annotations.sort(key=lambda a: a.location[0])
	document.contents = Pandoc().convert("markdown_github", "html", document.contents)

	return render_template("documents/viewer.html", name="Document", document=document, cases=cases, annotations=annotations, categories=categories)

@app.route("/documents/<id>/save",methods=["POST"])
@login.login_required
def documentSave(id):	
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		document = None

	title = request.form.get("title","").encode('utf-8')
	contents = request.form.get("contents","").encode('utf-8')
	category = request.form.get("category","").encode('utf-8')
	annotations = request.form.get("annotations","").encode('utf-8')
	
	document.author = login.current_user.username
	
	if document.save(title,contents,category,annotations):
		return json.dumps( {"success":"true","new_csrf":generate_csrf_token() } );
	
	return abort(500)

@app.route("/documents/<id>/delete",methods=["POST"])
@login.login_required
def documentDelete(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)

	document.remove()

	return json.dumps( {
			"success":"true",
			"new_csrf":generate_csrf_token()
		} );

	return abort(403)

@app.route("/documents/<id>/download/<filetype>")
@login.login_required
def documentDownload(id, filetype):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)

	return document.download(filetype, login.current_user)

@app.route("/documents/<id>/related")
#@login.login_required
def documentRelated(id):
	try:
		document = Document().matchObjects({"_id": id}, fields={"_id":True, "contents":True, "tags":True})[0]
	except Exception as e:
		print e
		return abort(404)
	
	return document.getRelatedDocumentsByTags()
		
@app.route("/documents/<id>/tfidf")
@login.login_required
def documentTFIDF(id):
	try:
		document = Document().matchObjects({"_id": id}, fields={"_id":True,"title":True, "category":True, "contents":True, "tags":True, "wordcount":True})[0]
	except Exception as e:
		traceback.print_exc(file=sys.stdout)
		return abort(404)

	return document.documentAnalysis()

@app.route("/documents/<id>/articles")
@login.login_required
def documentArticles(id):
	try:
		document = Document().matchObjects({"_id": id}, fields={"_id":True,"title":True, "category":True, "contents":True, "tags":True, "wordcount":True})[0]
	except Exception as e:
		traceback.print_exc(file=sys.stdout)
		return abort(404)

	return json.dumps( document.getArticlesFromContent() )

@app.route("/documents/add-jurisprudence")
@login.login_required
def addJurisprudenceDocuments():
	Document.generateJurisprudenceDocuments( Document )
	
	return json.dumps({"success":"true"})

@app.route("/documents/full-articles")
@login.login_required
def fullArticlesRun():	
	print "Performing total articles run."
	allDocuments = Document().matchObjects(
		{},
		fields={"_id":True,"title":True, "category":True, "contents":True, "tags":True, "wordcount":True}
	)
	
	for d in allDocuments:
		print "Articles for", d.title,
		d.getArticlesFromContent()
		print len(d.articles),"results"
	
	return json.dumps({"success":"true"})

@app.route("/documents/full-tfidf")
@login.login_required
def fullTFIDFRun():	
	print "Performing total TFIDF run."
	allDocuments = Document().matchObjects(
		{},
		fields={"_id":True,"title":True, "category":True, "contents":True, "wordcount":True, "articles":True}
	)
	
	for d in allDocuments:
		print "TFIDF for", d.title,
		d.tfidf(allDocuments=allDocuments)
		print len(d.tags),"results"
	
	return json.dumps({"success":"true"})


@app.route("/documents/qsearch")
@login.login_required
def documentQuickSearch():
	keywords = request.args.get("keywords", "").split(" ")
	return Document().quickSearch(keywords)

@app.route("/documents/search")
#@login.login_required
def documentSearch():
	query = request.args.get("keywords", "")
	if isinstance(query, list):
		query = query[0]
	category = request.args.get("category", None)
	
	results, extendedQuery = Document.search(query)

	categories = Category().matchObjects({})
	return render_template("documents/search.html",
						   name="Document search results",
						   category=category,
						   categories=categories,
						   documents=results,
						   keywords=query,
						   extendedQuery=extendedQuery,
						   active="documents")

@app.route("/documents/search/table/<amount>/<page>")
@login.login_required
def documentSearchTable(amount, page):
	keywords = request.args.get("keywords", "")
	category = request.args.get("category", None)
	results = do_documentSearch(keywords,
								category=category if len(category)>0 else None,
								skip=int(amount)*int(page),
								limit=int(amount))

	return render_template("documents/search-table.html", documents=results)


def returnUploadError(error, categories):
	return render_template("documents/upload.html", active="documents", categories=categories, name="Upload document", error=error)

@app.route("/documents/upload", methods=["GET","POST"])
@login.login_required
def documentsUpload():
	categories = Category().matchObjects({})
	error = None

	if request.method == "GET":
		return render_template("documents/upload.html", active="documents", categories=categories, name="Upload document", error=None)
	else:
		data = dict(request.form)
		title = data["title"][0]
		author = login.current_user.username
		category = data["category"][0]
		
		document,error = Document.upload(title, author, category, request.files["file"], documentClass=Document)

		if error is None:
			return redirect("/documents/"+str(document._id))
		else:
			return returnUploadError(error,categories)
	
	return returnUploadError(error,categories)
	
def returnUploadReferenceError(error):
	return render_template("users/profile.html", active="profile", name="Profile", passwordError=None, referenceError=error)
	
@app.route("/documents/upload-reference", methods=["POST"])
@login.login_required
def documentsReferenceUpload():
	filetypes = {
		"docx":"docx"
	}
	
	error = None
	f = request.files["reference"]
	data = dict(request.form)
	filename = f.filename
	extension = filename.split(".")[-1]
	if extension not in filetypes.keys():
		error = "Not an allowed format."
		return returnUploadReferenceError(error)
	
	user = login.current_user	
	user.referenceDocument = f.stream.read()
	user.save()

	if error is None:
		return redirect("/users/profile")
	else:
		return returnUploadReferenceError(error)
	
# CASES #
@app.route("/cases/")
@login.login_required
def caseIndex():
	cases = Case().matchObjects(
		{},
		limit=25
	)

	return render_template("cases/index.html", name="Cases overview", cases=cases, active="cases")

@app.route("/cases/new")
@login.login_required
def caseCreate():
	case = Case()
	case.save()
	_id = case._id;
	return redirect("/cases/%s/edit" % _id)

@app.route("/cases/<id>/edit")
@login.login_required
def caseEdit(id):
	try:
		case = Case().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	print dir(case)
	print case.documents
	
	documents = case.getDocuments()
	tags = defaultdict(int)
	for d in documents:
		for tag in d.tags.values():
			if len(tag) > 3:
				tags[tag]+=1
		
	suggested = case.getFullCaseRecommendations()
	return render_template("cases/edit.html", name="Edit case", case=case, suggested=suggested, tags=dict(tags), active="cases")

@app.route("/cases/<id>/delete",methods=["POST"])
@login.login_required
def caseDelete(id):
	try:
		case = Case().getObjectsByKey("_id", id)[0]
	except:
		return abort(404)

	if request.method != "POST":
		return abort(405)

	case.remove()

	return json.dumps( {
			"success":"true",
			"new_csrf":generate_csrf_token()
		} );

	return abort(403)

@app.route("/cases/<id>/add",methods=["POST"])
@login.login_required
def caseAddDocument(id):
	try:
		case = Case().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	return json.dumps( { "success":case.insertDocument( request.form.get("document_id", None ) ),
					   	 "new_csrf":generate_csrf_token() } )


@app.route("/cases/<id>/remove",methods=["POST"])
@login.login_required
def caseRemoveDocument(id):
	try:
		case = Case().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	return json.dumps( { "success":case.removeDocument( request.form.get("document_id", None ) ),
					   	 "new_csrf":generate_csrf_token() } )

@app.route("/cases/<id>/set-title",methods=["POST"])
@login.login_required
def caseSetTitle(id):
	try:
		case = Case().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	title = request.form.get("document_title", None )
	case.title = title
	case.save()
	
	return json.dumps( { "success":True,
					   	 "new_csrf":generate_csrf_token() } )


# ANNOTATIONS #

@app.route("/annotations/")
@login.login_required
def annotationsIndex():
	annotations = Annotation().matchObjects(
		{},
		limit=25
	)

	return render_template("annotations/index.html", name="Annotations overview", annotations=annotations, active="annotations")

@app.route("/annotations/<id>/delete",methods=["POST"])
@login.login_required
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
@login.login_required
def usersIndex():
	users = User().matchObjects(
		{},
		limit=25)

	return render_template("users/index.html", name="Users overview", users=users, active="users")

@app.route("/users/new")
@login.login_required
def userCreate():
	user = User()
	user.save()
	_id = user._id;
	return redirect("/users/%s/edit" % _id)

@app.route("/users/<id>/edit")
@login.login_required
def userEdit(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)

	try:
		user.public_key = base64.b64decode(user.public_key)
	except:
		pass # Skip over new users
	return render_template("users/edit.html", name="Edit user", user=user, active="users")

@app.route("/users/profile")
@login.login_required
def userProfile():
	error = request.args.get("error",None)
	passwordError = None
	passwordErrors = {
		"password-toocommon": "The password you tried to use was is too common.",
		"password-incorrect": "The old password you provided was incorrect",
		"password-nomatch": "The new passwords you sent don't match up.",
		"password-tooshort": "The password you're trying too use is too short."
	}
	if error is not None:
		passwordError = passwordErrors.get(error,None)
	
	documents = Document().getObjectsByKey("author", login.current_user.username, limit=10)
	return render_template("users/profile.html",
						   name="Your profile page",
						   user=login.current_user,
						   documents=documents,
						   passwordError=passwordError,
						   success=request.args.get("success",None),
						   active="profile")

@app.route("/users/<id>")
@login.login_required
def userView(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)

	try:
		user.public_key = base64.b64decode(user.public_key)
	except:
		pass # Skip over new users

	return render_template("users/view.html", name="View user", user=user, active="users")

@app.route("/users/<id>/save",methods=["POST"])
@login.login_required
def userSave(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)

	data = dict(request.form)

	oldPassword = urllib2.unquote( data.get("old-password", [""])[0].decode("utf-8") )
	newPassword = urllib2.unquote( data.get("new-password", [""])[0].decode("utf-8") )
	newPasswordAgain = urllib2.unquote( data.get("new-password-again", [""])[0].decode("utf-8") )
	
	if len(newPassword) > 0:
		if not user.checkPassword(oldPassword):
			return redirect(request.args.get("back", "/users/%s/edit" % id)+"?error=password-incorrect")

		if newPassword != newPasswordAgain:
			return redirect(request.args.get("back", "/users/%s/edit" % id)+"?error=password-nomatch")

		if len(newPassword) < 8:
			return redirect(request.args.get("back", "/users/%s/edit" % id)+"?error=password-tooshort")

		if newPassword in User.getMostCommonPasswords():
			return redirect(request.args.get("back", "/users/%s/edit" % id)+"?error=password-toocommon")

		user.setPassword(newPassword)

	user.username = data["username"][0]
	user.firstname = data["firstname"][0]
	user.lastname = data["lastname"][0]
	user.email = data["email"][0]
	user.save()

	return redirect(request.args.get("back", "/users/%s/edit" % id)+"?success=true")

@app.route("/users/<id>/delete",methods=["POST"])
@login.login_required
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
@login.login_required
def userPasswordEdit(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)

	return render_template("users/password-edit.html", name="Respin password", user=user, active="users")

# USERS - U2F AUTHENTICATION #

@app.route("/users/<id>/u2f/enroll")
def userEnroll(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	try:
		devices = map(DeviceRegistration.wrap, user.u2f_devices)
	except:
		devices = []
	
	app_id = "http://127.0.0.1"
	print app_id
	enroll = start_register(app_id, devices)
	user.u2f_enroll = enroll.json
	return enroll.json

@app.route("/users/<id>/u2f/bind")
def userBind(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	data = request.data.get("data", None)
	enroll = user.u2f_enroll
	binding, cert = complete_register(enroll, data, [])
	
	try:
		devices = map(DeviceRegistration.wrap, user.u2f_devices)
	except:
		devices = []
		
	devices.append(binding)
	user.u2f_devices = [d.json for d in devices]
	
	print "U2F device enrolled. Username: %s" % user.username
	print "Attestation certificate:\n%s" % cert.as_text()
	
	return json.dumps(True)

@app.route("/users/<id>/u2f/sign")
def userSign(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	try:
		devices = map(DeviceRegistration.wrap, user.u2f_devices)
	except:
		devices = []
		
	challenge = start_authenticate(devices)
	user.u2f_challenge = challenge.json
	return challenge.json

@app.route("/users/<id>/u2f/verify")
def userVerify(id):
	try:
		user = User().getObjectsByKey("_id", id)[0]
	except Exception as e:
		return abort(404)
	
	try:
		devices = map(DeviceRegistration.wrap, user.u2f_devices)
	except:
		devices = []
		
	challenge = user.u2f_challenge
	c, t = verify_authenticate(devices, challenge, data)
	return json.dumps({
			'touch': t,
			'counter': c
		})
	

# INSTALLING
@app.route("/install/")
def installYuras():
	if len(User().matchObjects({})) > 0:
		return abort(500)

	return render_template("install/index.html", name="Install Yuras")

@app.route("/install/<page>", methods=["POST"])
def installYurasPage(page):
	return render_template("install/page_%s.html" % page, name="Install Yuras", data=dict(request.form))

@app.route("/install/final", methods=["GET", "POST"])
def installYurasFinal():
	#data = dict(request.form)
	
	data = {
		"username":["Stephan"],
		"email":["Stephan@yuras.nl"],
		"password":["get rekt son lol"],
	}
	
	user = User()

	username = unicode(data.get("username")[0].lower())
	password = unicode(data.get("password")[0].lower())
	email = unicode(data.get("email")[0].lower())

	user.setPassword(password)
	user.username = username
	user.email = email
	user.firstname = username

	user.save()
	
	return render_template("install/final.html", name="You are done installing Yuras!")
	
