import requests, time, json

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

importioapi = "https://api.import.io/store/data/1e925fc7-26d7-4774-b5cb-66e4323c9580/_query?input/webpage/url={}&_user=25ce5931-7842-406c-8e24-5b3594f52ecc&_apikey=EFgA9V0bfcD4Eaj%2BOdFKaNzxAUk2spuzzLn%2BJwssq%2BQ6elaPDx3qsygYnd1swOl3bmsRmC9%2FGig%2B1A2QvpIE8w%3D%3D"
documenturl = "http://uitspraken.rechtspraak.nl/inziendocument?id="

uitspraken = 314216
n = 1
step = 100

starttime = time.time()
timen = 1

print "ID\tpage\tstep\tresult"
while n*step < uitspraken:
	resultsOutput = open("rechtspraak.nl-page-%s.json" % n, "w")
	
	r = requests.post(url, payload % (n, step), headers=headers)
	#print payload % (n, n*step)
	resultsDict = {}
	for r, result in enumerate(r.json()["Results"]):
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
		
		apiurl = importioapi.format(documenturl+_id)
		document = requests.get(apiurl)
		try:
			resultsDict[_id]["contents"] = document.json()
		except:
			print "Error on", _id
			time.sleep(30)
		
		
	json.dump(resultsDict,resultsOutput)
	resultsOutput.close()
	n+=1
	