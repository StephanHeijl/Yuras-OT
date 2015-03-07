import requests, time, json
from xml.dom.minidom import parse, parseString

url = "http://uitspraken.rechtspraak.nl/api/zoek"
payload = """{"PageIndex":%s,"PageSize":%s,"ShouldReturnHighlights":true,"ShouldCountFacets":true,"SortOrder":"Relevance","SearchTerms":[],"Contentsoorten":[{"NodeType":7,"Identifier":"uitspraak","level":1}],"Rechtsgebieden":[],"Instanties":[],"DatumPublicatie":[],"DatumUitspraak":[],"Advanced":{"PublicatieStatus":"AlleenGepubliceerd"},"CorrelationId":"704cf0dbc2f84f91a159151af2979c1a"}"""
headers = { "Host":" uitspraken.rechtspraak.nl",
"Connection":" keep-alive",
"Content-Length":" 375",
"Pragma":" no-cache",
"Cache-Control":" no-cache",
"Accept":" application/json, text/javascript, */*; q=0.01",
"Origin":" http://uitspraken.rechtspraak.nl",
"X-Requested-With":" XMLHttpRequest",
"User-Agent":" Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36",
"Content-Type":" application/json",
"Referer":" http://uitspraken.rechtspraak.nl/",
"Accept-Encoding":" gzip, deflate",
"Accept-Language":" nl-NL,nl;q=0.8,en-US;q=0.6,en;q=0.4",
"Cookie":" WT_FPC=id=92.110.83.17-3079728544.30424086:lv=1425485400003:ss=1425484112277" }

documenturl = "http://data.rechtspraak.nl/uitspraken/content?id="

uitspraken = 314216
n = 1735
step = 100

starttime = time.time()
timen = 1

print "ID\tpage\tstep\tresult"
while n*step < uitspraken:
	resultsOutput = open("rechtspraak.nl-page-%s.json" % n, "w")
	results = []
	resultsDict = {}
	while len(results) == 0:
		r = requests.post(url, payload % (n, step), headers=headers)
		print url
		try:
			results = r.json()["Results"]
		except:
			time.sleep(30)
			
		
	for r, result in enumerate(results):
		_id = result["TitelEmphasis"]
		
		totalelapsed = time.time() - starttime
		avgtime = totalelapsed/timen
		expected = (uitspraken-(n*step)-r)*avgtime
		
		days = int(expected/3600/24)
		expected-= days*3600*24
		hours = int(expected/3600)
		expected -= hours*3600
		minutes = int(expected/60)
		
		percentage = str(float(int((float((n*step)+r)/uitspraken)*10000))/100) + "%"
		
		print _id, n, step, r+1, "%s:%s:%s" % ( str(days),str(hours).rjust(2,"0"),str(minutes).rjust(2,"0")), percentage
		timen+=1
		resultsDict[_id] = result
		
		apiurl = documenturl+_id
		document = requests.get(apiurl)
		
		parsedDocument = {}
		
		xml = parseString(document.content)
		try:
			uitspraak = xml.getElementsByTagName("uitspraak")[0]
		except:
			continue

		parsedDocument["uitspraak"] = []
		for para in uitspraak.getElementsByTagName("para"):
			try:
				parsedDocument["uitspraak"].append(para.firstChild.nodeValue)
			except:
				pass
			
		parsedDocument["id"] = _id
		
		try:
			parsedDocument["datum_uitspraak"] = xml.getElementsByTagName("dcterms:date")[0].firstChild.nodeValue
		except:
			pass		
		try:
			parsedDocument["datum_publicatie"] = xml.getElementsByTagName("dcterms:issued")[0].firstChild.nodeValue
		except:
			pass
		try:
			parsedDocument["zaaknummer"] = xml.getElementsByTagName("psi:zaaknummer")[0].firstChild.nodeValue
		except:
			pass
		try:
			parsedDocument["bijzondere_kenmerken"] = xml.getElementsByTagName("dcterms:subject")[0].firstChild.nodeValue
		except:
			pass
		
		try:
			parsedDocument["inhoudsindicatie"] = xml.getElementsByTagName("inhoudsindicatie")[0].firstChild.firstChild.nodeValue
		except:
			pass
		
		
		resultsDict[_id]["contents"] = {}
		resultsDict[_id]["contents"]["results"] = parsedDocument
		
		
		try:
			pass
		except:
			print "Error on", _id
			time.sleep(30)
		
	
	json.dump(resultsDict,resultsOutput)
	resultsOutput.close()
	n+=1
