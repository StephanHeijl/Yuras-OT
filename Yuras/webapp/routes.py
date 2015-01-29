from __future__ import division

import os, re, base64, urllib2, json, time, random, chardet, scrypt, collections, math, pprint
import multiprocessing
from functools import wraps
from collections import defaultdict

from bson.objectid import ObjectId

from flask import Flask,render_template,abort, Response, request, session, redirect, g, url_for
from flask.ext import login

from Yuras.common.TemplateTools import TemplateTools
from Yuras.common.Pandoc import Pandoc
from Yuras.common.Config import Config

from Yuras.webapp.models.Document import Document
from Yuras.webapp.models.Annotation import Annotation
from Yuras.webapp.models.User import User
from Yuras.webapp.models.Category import Category

from Crypto import Random

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
			user = User().getObjectsByKey("username", unicode(request.form.get("username")),limit=1)[0]
		except Exception as e:
			print e
			user = None
			print "User not found"
				
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
		fields={"title":True, "created":True, "author":True, "secure":True})
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
@login.login_required
def documentsIndex():
	documents = Document().matchObjects(
		{},
		limit=10,
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
	categories = Category().matchObjects({},limit=25)
	
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
		
	document.contents = Pandoc().convert("markdown_github", "html", document.contents)
	document.contents = document.contents.replace(markedContainer[0], "<span class='marked'>").replace(markedContainer[1], "</span>")

	return render_template("documents/viewer.html", name="Document", document=document, annotations=annotations, categories=categories)

@app.route("/documents/<id>/save",methods=["POST"])
@login.login_required
def documentSave(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except:
		document = None
	
	if request.method != "POST":
		return abort(405)
	
	contents_escaped = urllib2.unquote( request.form.get("contents","").encode('utf-8') )
	contents_md = unicode(Pandoc().convert("html","markdown_github",contents_escaped))
	title = urllib2.unquote( request.form.get("title","").encode('utf-8') )
	
	document.contents = contents_md.encode('utf-8')
	document.title = title
	category = urllib2.unquote( request.form.get("category","").encode('utf-8') )
	if len(Category().getObjectsByKey("name", category)) == 0:
		c = Category()
		c.name = category
		c.save()

	document.category = category
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
			a.linked_to = int(annotation["linked-to"])				
			
			# Correct location parameter
			print contents_md[a.location[0]:a.location[0]+a.location[1]], a.selected_text
			if contents_md[a.location[0]:a.location[0]+a.location[1]] != a.selected_text:
				try:
					i = contents_md.index(annotation["selected_text"],0)
				except:
					continue
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
	
	# Counting words
	words = re.findall("[a-z]{2,}", contents_md.lower()) + re.findall("[a-z]{2,}", title.lower())
	wordCount = collections.defaultdict(int)
	for word in words:
		wordCount[word] += 1
		
	hashedWordCount = collections.defaultdict(int)
	for word, count in wordCount.items():
		key = base64.b64encode(scrypt.hash(str(word), str(Config().database), N=1<<9))
		hashedWordCount[key] = count
	
	print wordCount
	
	document.wordcount = dict(hashedWordCount)
	document.save()
	
	if contents_escaped is not "":
		return json.dumps( {
				"success":"true",
				"new_csrf":generate_csrf_token()
			} );
	
	return abort(403)

@app.route("/documents/<id>/delete",methods=["POST"])
@login.login_required
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
@login.login_required
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
		responseContents = Pandoc().convert("markdown_github", filetype, document.contents)
		response = Response(responseContents, mimetype=filetypes[filetype])
		
		filename = document.title + "." + filetype
		
		response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
		return response
	else:
		return abort(405)

def loopTermFrequencies( termFrequencies, tfidf, documentCount, wordCountsByKey ):
	# This function is paralellezied due to the large amount of words and long CPU times.
	for word, (count, tf) in termFrequencies:
		key = base64.b64encode(scrypt.hash(str(word), str(Config().database), N=1<<9))
		idf = math.log(documentCount / (1+wordCountsByKey[key]))
		tfidf[word] = (idf*tf, key)		
		

@app.route("/documents/<id>/tfidf")
@login.login_required
def documentTFIDF(id):
	try:
		document = Document().getObjectsByKey("_id", id)[0]
	except Exception as e:
		print e
		return abort(404)

	startTime = time.time()
	
	# initialize manager for multiprocessing
	manager = multiprocessing.Manager()
	
	# Cound words in this document
	words = re.findall("[a-z]{2,}", document.contents.lower()) + re.findall("[a-z]{2,}", document.title.lower())
	wordCount = collections.defaultdict(int)
	for word in words:
		wordCount[word] += 1
		
	print time.time()-startTime
		
	termFrequencies = {}
	for word in words:
		termFrequencies[word] = (wordCount[word], wordCount[word]/len(words))
		
	print time.time()-startTime
		
	allDocuments = Document().matchObjects(
		{"category":document.category},
		fields={"wordcount":True}
	)
	
	print time.time()-startTime
	
	documentCount = len(allDocuments)
	
	print time.time()-startTime
	
	allWordCounts = []
	for d in allDocuments:
		allWordCounts += d.wordcount.keys()
		
	print time.time()-startTime
		
	wordCountsByKey = defaultdict(int)
	for k in allWordCounts:
		wordCountsByKey[k] += 1
		
	print time.time()-startTime
	
	tfidf = manager.dict()
	managerWordCountsByKey = manager.dict(wordCountsByKey)
		
	cores = multiprocessing.cpu_count()
	#cores = 1
	chunkSize = len(termFrequencies)/cores
	
	pool = []
	for core in range(cores):
		print core, int(chunkSize*core),int(chunkSize*(core+1))
		p = multiprocessing.Process(target=loopTermFrequencies, args=(termFrequencies.items()[int(chunkSize*core):int(chunkSize*(core+1))], tfidf, documentCount, managerWordCountsByKey))
		p.start()
		print "Starting", p
		pool.append( p )

	for p in pool:
		print "Joining", p
		p.join()
		
	print time.time()-startTime
		
	results = {}
	
	for word,(score,key) in tfidf.items():
		if score >= 0.015:
			related = Document().matchObjects(
				{"$and": [
						{"wordcount."+key : { "$exists": True }}, 
						{"_id": {"$ne": ObjectId(id)}} # A conversion to ObjectId is needed for Mongo/Toku
					]},
				limit = 3,
				fields = {"title":True, "_id":True}
			)
			relatedResults = []
			for r in related:
				relatedResults.append( 
					{
						"title":r.title,
						"_id":str(r._id)
					}
				)
				
			results[word] = relatedResults
		
	print time.time()-startTime
		
	return json.dumps(results)
	
	
def flatten(d, parent_key='', sep='_'):
	items = []
	for k, v in d.items():
		new_key = parent_key + sep + k if parent_key else k
		if isinstance(v, collections.MutableMapping):
			items.extend(flatten(v, new_key, sep=sep).items())
		else:
			items.append((new_key, v))
	return dict(items)
	
@app.route("/documents/add-jurisprudence")
@login.login_required
def addJurisprudenceDocuments():
	
	def generateJurisprudenceDocuments():
		jurisprudence = json.load( open(os.path.join( Config().WebAppDirectory, "..", "..", "jurisprudence.json"), "r") )		
		
		categorized = {}
		wiki = jurisprudence["Yuras"]["wiki"]
		flatWiki = flatten(wiki)
		dCounter = 1
		dTotal = len(flatWiki)
		for key, document in flatWiki.items():
			title = key.split("_")[-1].strip(".html").split("/")[-1].replace("-"," ")
			title = title[0].upper() + title[1:]
			key = key.split("_")[0]

			if key not in categorized:
				categorized[key] = []
				if len(Category().getObjectsByKey("name", key)) == 0:
					c = Category()
					c.name = key
					c.save()

			if len(Document().getObjectsByKey("title", title)) == 0:
				d = Document()
				d.title = title
				d.category = key
				d.contents = document
				d.author = "Yuras"

				# Counting words
				words = re.findall("[a-z]{2,}", document.lower()) + re.findall("[a-z]{2,}", title.lower())
				wordCount = collections.defaultdict(int)
				for word in words:
					wordCount[word] += 1

				hashedWordCount = collections.defaultdict(int)
				for word, count in wordCount.items():
					k = base64.b64encode(scrypt.hash(str(word), str(Config().database), N=1<<9))
					hashedWordCount[k] = count

				d.wordcount = dict(hashedWordCount)
				d.save()
			
			categorized[key].append(document)
			print title, "saved", dCounter, "/", dTotal
			dCounter += 1
			yield title + "\n"
			
	return Response(generateJurisprudenceDocuments(), mimetype='text/plain')

def do_documentSearch(keywords, category=None, skip=0, limit=10):
	wordCountList = []
	keys = []
	for word in keywords:
		if len(word) == 0:
			continue
		key = base64.b64encode(scrypt.hash(str(word), str(Config().database), N=1<<9))
		keys.append(key)
		wordCountList.append( {"wordcount."+key : { "$exists": True }} )
	
	if len(wordCountList) > 0:
		matchArray = {"$or":wordCountList}
	
		if category is not None:
			orValues = matchArray["$or"]
			del matchArray["$or"]
			matchArray["$and"] = [{"category":category}, {"$or":orValues}]
			
	else:
		if category is not None:
			matchArray = {"category":category}
	
	results = Document().matchObjects(
		matchArray,
		limit=limit,
		skip=skip
	)
	
	#results.sort(key=lambda r:r.wordcount.get(keys[0],0))
	return results
	
@app.route("/documents/search")
@login.login_required
def documentSearch():
	keywords = request.args.get("keywords", "").split(" ")
	category = request.args.get("category", None)
	results = do_documentSearch(keywords,category=category if len(category)>0 else None)
	
	categories = Category().matchObjects({})
	return render_template("documents/search.html", 
						   name="Document search results", 
						   category=category,
						   categories=categories,
						   documents=results,
						   keywords=" ".join(keywords),
						   active="documents")

@app.route("/documents/search/table/<amount>/<page>")
@login.login_required
def documentSearchTable(amount, page):
	keywords = request.args.get("keywords", "").split(" ")
	category = request.args.get("category", None)
	results = do_documentSearch(keywords,
								category=category if len(category)>0 else None,
								skip=int(amount)*int(page),
								limit=int(amount))
	
	return render_template("documents/search-table.html", documents=results)
	
	
@app.route("/documents/upload")
@login.login_required
def documentsUpload():
	render_template("documents/upload.html", active="documents", name="Upload document")
	
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
	
	rawPassword = urllib2.unquote( data["password"][0].decode("utf-8") )
	
	user.setPassword(rawPassword)
		
	user.username = data["username"][0]
	user.firstname = data["firstname"][0]
	user.lastname = data["lastname"][0]
	user.email = data["email"][0]
	user.save()
	
	return redirect("/users/%s/edit" % id)
	
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
@login.login_required
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

# INSTALLING
@app.route("/install")
def installYuras():
	if len(User().matchObjects({})) > 0:
		return abort(500)
	
	user = User()
	user.save()
	
	username = u"accountone"
	password = unicode(" ".join(random.sample(wordList,4)))
	
	user.setPassword(password)
	user.username = username	
	
	user.save()		
	
	return json.dumps([username, password])
	