 #!/usr/bin/python
 # -*- coding: latin-1 -*-

from sklearn.externals import joblib
import sys, re

model = joblib.load(sys.argv[1])
counter = joblib.load(sys.argv[2])
transformer = joblib.load(sys.argv[3])

specialCharacters = re.compile("[^ a-z\-]")
stopWords = ['deze', 'en', 'haar', 'is', 'in', 'niet', 'zijn', 'door', 'het', 'heeft', 'van', 'rechtbank', 'te', 'zij', 'bij', 'de', 'dat', 'met', 'worden', 'die', 'voor', 'een', 'op', 'ze', 'of', 'aan']

def parseText(text):
	contents = text.lower()
	contents = specialCharacters.sub("", contents)
	contents = " ".join(filter(lambda w: len(w) > 0 and w not in stopWords, contents.split(" ")))
	
	X_train_counts = counter.transform([contents])
	X_train_tfidf  = transformer.transform(X_train_counts)
	
	
	return X_train_tfidf

text = """
Onderzoek van de zaak
Dit vonnis is gewezen naar aanleiding van het onderzoek op de terechtzitting van 

13 augustus 2013.
De tenlastelegging
Aan verdachte is ten laste gelegd dat:
1.
zij op een of meerdere tijdstip(pen) in of omstreeks de periode van 01
februari 2012 tot en met 03 maart 2012 te Putten en/of een of meerdere andere
plaats(en) in Nederland, in elk geval in Nederland,
(telkens) ter uitvoering van het voornemen en het misdrijf om, tezamen en in
vereniging met een ander of anderen, althans alleen, met het oogmerk om zich
of een ander wederrechtelijk te bevoordelen, door bedreiging met smaad,
smaadschrift of openbaring van een geheim, een of meerdere perso(o)n(en) ([benadeelde 1]
[benadeelde 1] en/of [benadeelde 2] en/of [benadeelde 3] en/of [benadeelde 4]) te dwingen tot
de afgifte van een geldbedrag (varierend tussen de 500 en 2.000 Euro), in elk
geval enig geldbedrag, dat geheel of ten dele toebehoort aan die [benadeelde 1]
en/of [benadeelde 2] en/of [benadeelde 3] en/of [benadeelde 4], in elk geval aan een
ander of anderen dan aan verdachte en/of haar mededader(s),
welke bedreiging met smaad, smaadschrift of openbaring van een geheim hieruit
bestond dat verdachte en/of haar mededader(s) (telkens) voornoemde [benadeelde 1]
en/of [benadeelde 2] en/of [benadeelde 3] en/of die [benadeelde 4] (telkens) een of
meerdere sms-bericht(en) e-mail(s) heeft/hebben gestuurd en/of een of meerdere
telefoongesprekken met die [benadeelde 1] en/of die [benadeelde 2] en/of die [benadeelde 3] en/of
die [benadeelde 4] heeft gevoerd, waarin gedreigd werd de (pedo)seksuele geaardheid
en/of een of meerdere door die [benadeelde 1] en/of [benadeelde 2] en/of [benadeelde 3] en/of die
[benadeelde 4] gepleegde strafbare feiten en/of een of meerdere door/van hen gemaakte
videobeelden openbaar te maken,
terwijl de uitvoering van dit voorgenomen misdrijf niet is voltooid;
art 45 lid 1 Wetboek van Strafrecht
art 47 ahf/ond 1 Wetboek van Strafrecht
art 318 lid 1 Wetboek van Strafrecht
2.
zij op een of meerdere tijdstip(pen) in of omstreeks de periode van 01
februari tot en met 03 maart 2012, te Rotterdam en/of een of meerdere andere
plaats(en) in Nederland, in elk geval in Nederland,
tezamen en in vereniging met een andere of anderen, althans alleen,
een voorwerp(en), te weten een of meerdere geldbedrag(en) van (in totaal)
ongeveer 2.500 Euro, heeft verworven, voorhanden heeft gehad, heeft
overgedragen en/of omgezet, althans van die/dat geldbedrag(en), gebruik heeft
gemaakt,
terwijl verdachte en/of haar mededader(s) wist(en) dat bovenomschreven
voorwerp(en) - onmiddellijk of middellijk - afkomstig was uit enig misdrijf;
art 47 ahf/sub 1 Wetboek van Strafrecht
art 420bis lid 1 ahf/ond b Wetboek van Strafrecht
3.
zij op een of meerdere tijdstip(pen) in of omstreeks de periode van 01
februari 2012 tot en met 03 maart 2012 te Rotterdam en/of een of meerdere
andere plaatsen in Nederland, in elk geval in Nederland,
(telkens) tezamen en in vereniging met een ander of anderen, althans alleen,
opzettelijk en wederrechtelijk gegevens (te weten: een of meerdere
e-mailberichten en/of foto's en/of videobeelden) die door middel van een
geautomatiseerd werk of door middel van een telecommunicatie waren opgeslagen
en/of werden verwerkt en/of overgedragen, heeft gewist en/of onbruikbaar
gemaakt en/of ontoegankelijk gemaakt, door (met voornoemd opzet) de/het
wachtenwoord(en) van de e-mailaccount(s),
- [e-mailaccount], en/of
- [e-mailaccount 2], en/of
- [e-mailaccount 3], en/of
- [e-mailaccount 4], en/of
- [e-mailaccount 5], en/of
- [e-mailaccount 6], en/of
- [e-mailaccount 7], en/of
- [e-mailaccount 8], en/of
- [e-mailaccount 9], en/of
- [e-mailaccount 10], en/of
- [e-mailaccount 11], en/of
- het e-mailadres van een persoon zich noemende [naam 1], en/of
- het e-mailadres van een persoon zich noemende [naam 2]
[naam 2], en/of
- het e-mailadres van een persoon zich noemende [naam 3], en/of
- het e-mailadres van een persoon zich noemende [naam 4], en/of
- het e-mailadres van een persoon zich noemende [naam 5], en/of
- het e-mailadres van een persoon zich noemende [naam 6], en/of
- het e-mailadres van een persoon zich noemende [naam 7], en/of
- het e-mailadres van een persoon zich noemende [naam 8], en/of
- het e-mailadres van een persoon zich noemende [naam 9], en/of
- het e-mailadres van een persoon zich noemende [naam 10], en/of
- het e-mailadres van een persoon zich noemende [naam 11]
[naam 11],
waarin die berichten en/of die foto's en/of die videobeelden werden
opgeslagen, te wijzigen;
art 350a lid 1 Wetboek van Strafrecht
4.
hij op een of meerdere tijdstip(pen) in of omstreeks de periode vam 01
februari 2012 tot en met 03 maart 2012 te Rotterdam en/of een of meerdere
andere plaats(en) in Nederland, in elk geval in Nederland,
tezamen met een ander of anderen, althans alleen, opzettelijk en
wederrechtelijk in een of meer geautomatiseerde werken, te weten een of
meerdere e-mailaccount(s), te weten:
- [e-mailaccount], en/of
- [e-mailaccount 2], en/of
- [e-mailaccount 3], en/of
- [e-mailaccount 4], en/of
- [e-mailaccount 5], en/of
- [e-mailaccount 6], en/of
- [e-mailaccount 7], en/of
- [e-mailaccount 8], en/of
- [e-mailaccount 9], en/of
- [e-mailaccount 10], en/of
- [e-mailaccount 11], en/of
- het e-mailadres van een persoon zich noemende [naam 1], en/of
- het e-mailadres van een persoon zich noemende [naam 2]
[naam 2], en/of
- het e-mailadres van een persoon zich noemende [naam 3], en/of
- het e-mailadres van een persoon zich noemende [naam 4], en/of
- het e-mailadres van een persoon zich noemende [naam 5], en/of
- het e-mailadres van een persoon zich noemende [naam 6], en/of
- het e-mailadres van een persoon zich noemende [naam 7], en/of
- het e-mailadres van een persoon zich noemende [naam 8], en/of
- het e-mailadres van een persoon zich noemende [naam 9], en/of
- het e-mailadres van een persoon zich noemende [naam 10], en/of
- het e-mailadres van een persoon zich noemende [naam 11]
[naam 11],
of in een deel daarvan, is binnengedrongen, waarna verdachte vervolgens
gegevens, die waren opgeslagen, werden verwerkt of werden overgedragen door
middel van dat/die geautomatiseerd(e) werk(en) waarin verdachte zich
wederrechtelijk bevond, voor zichzelf of een ander heeft overgenomen, afgetapt
of opgenomen;
art 47 lid 1 ahf/ond a Wetboek van Strafrecht
art 138ab lid 2 Wetboek van Strafrecht.
Aanhoudingsverzoek
aanhoudingsverzoek verdediging
Door de raadsvrouw is primair om aanhouding verzocht van de strafzaak, teneinde aangever [benadeelde 1] als getuige te horen ter beantwoording van de vraag in welke mate de telefoongesprekken / sms berichten vlak voorafgaand aan de aanhouding van verdachten zijn ingegeven c.q. gestuurd door de politie. Zij heeft daarbij gewezen op de omstandigheid dat er onder regie van de politie afspraken zijn gemaakt over de betaling (pag. 4 stamproces-verbaal) en de tapgesprekken waaronder testcalls (pag. 123 e.v.). De raadsvouw heeft daarbij gewezen op het arrest van de HR, LJN BK5593, en dat gelet op dat arrest in het onderhavige geval sprake kan zijn geweest van een pseudodienstverlening.
Standpunt van het openbaar ministerie
De officier heeft zich op het standpunt gesteld dat het horen van de getuige [benadeelde 1] niets toe of afdoet aan de rechtmatigheid van de aanhouding en de heldere verklaringen die verdachte zelf heeft afgelegd. Het arrest waaraan is gerefereerd – ziende op een pseudodienstverlening in verband met een drugsdealer - ziet op een geheel andere situatie dan de situatie in de onderhavige zaak. In de onderhavige zaak gaat het enkel om een wijziging van de al gemaakte afspraak over de betaling van het geld. Het verzoek om aanhouding dient daarom te worden afgewezen
Beoordeling door de rechtbank
De rechtbank is van oordeel dat van een situatie als bedoeld in artikel 126i en 126ij van het Wetboek van Strafvordering in deze zaak geen sprake is. In het onderhavige geval ging het om een al gemaakte afspraak omtrent een reeds door aangever [benadeelde 1] voorgenomen betaling van een geldbedrag om de veranderde wachtwoorden van zijn computer van verdachte te verkrijgen teneinde openbaarmaking van bestanden/een filmpje te voorkomen. Dit ziet op een geheel andere situatie dan die waar de wetgever met artikel 126i en 126ij het oog op heeft gehad. Het horen van deze getuige op de door de raadsvrouw aangegeven punten kan daarom in redelijkheid niet van belang zijn voor enige in de strafzaak te nemen beslissing in de zin van artikel 348 en 350 van het Wetboek van Strafvordering. Het verzoek om deze getuige in het kader van het verdedigingsbelang op de zitting te horen zal dan ook worden afgewezen.
Overwegingen ten aanzien van het bewijs 1
Aanleiding tot het onderzoek
Aanleiding voor het onderzoek was een aangifte door [benadeelde 1]. [benadeelde 1] was op 21 februari 2012 en 1 maart 2012 op zijn mobiele telefoon gebeld door een hem onbekende man die hem vertelde dat hij de hotmail account van [benadeelde 1] had en dat hij de hotmail account had doorgespit.
De man vertelde hem dat hij een mooi filmpje had gevonden dat op internet gezet zou gaan worden en dat [benadeelde 1] dit kon voorkomen als hij 1000 euro zou betalen. [benadeelde 1] vermoedde dat het zou gaan om een filmpje waarop te zien was dat hij seksuele handelingen verrichtte.
Na telefonisch contact tussen [benadeelde 1] en medeverdachte [medeverdachte] is onder regie van het onderzoeksteam een afspraak gemaakt om te betalen bij de McDonald’s bij strand Horst te Ermelo. Tijdens de overdracht van die betaling zijn [medeverdachte] en [verdachte] als verdachten aangehouden.
Standpunt van het openbaar ministerie
De officier van justitie heeft geconcludeerd tot bewezenverklaring van het onder 1, 2, 3 en 4 tenlastegelegde. Ter zitting heeft de officier van justitie de bewijsmiddelen opgesomd en toegelicht.
Standpunt van de verdachte / de verdediging
De raadsvrouw heeft zich met betrekking tot de inhoudelijke beoordeling van de ten laste gelegde feiten gerefereerd aan het oordeel van de rechtbank met betrekking tot de onder 1 en 2 aan verdachte ten laste gelegde feiten. Met betrekking tot de onder 3 en 4 aan verdachte ten laste gelegde feiten heeft de raadsvrouw zich op het standpunt gesteld dat verdachte dient te worden vrijgesproken bij gebrek aan voldoende wettig en overtuigend bewijs, aangezien uit de bevindingen van de digitale recherche onvoldoende kan worden afgeleid of er gegevens in de computers van de betrokken personen zijn gewist, onbruikbaar gemaakt of ontoegankelijk zijn gemaakt, terwijl evenmin sprake is geweest van hacken.
Ter terechtzitting heeft de raadsvrouw het standpunt van de verdediging toegelicht.
Beoordeling door de rechtbank
De rechtbank gaat bij de beoordeling van de ten laste gelegde feiten uit van de volgende feiten en omstandigheden.
Aangezien verdachte zowel bij de politie 2 als ter terechtzitting 3 duidelijk en ondubbelzinnig een bekennende verklaring heeft afgelegd, zal worden volstaan met een opgave van de bewijsmiddelen als bedoeld in artikel 359, derde lid, van het Wetboek van Strafvordering.
Naast deze verklaring van verdachte is voor het bewijs voorhanden de aangiften van 
[benadeelde 1] 4 , [benadeelde 2] 5 , [benadeelde 3] 6 , [benadeelde 4] 7 , de bij de aangifte van [benadeelde 4] gevoegde mailberichten 8 , de verklaringen van de medeverdachte [medeverdachte] 9 , en de bevindingen van het digitaal onderzoek 10 .
De rechtbank acht op grond daarvan bewezen dat verdachte zich heeft schuldig gemaakt aan de aan haar verweten gedragingen zoals hierna in de bewezenverklaring wordt opgenomen.
Het betoog van de raadsvrouw met betrekking tot feit 2 dat geen sprake is geweest van verhulling, volgt de rechtbank niet. Verdachte heeft verklaard een deel van het met de afpersing verkregen geld te hebben aangewend voor het kopen van verschillende goederen ten behoeve van gezamenlijk gebruik en een bedrag van € 500 te hebben gestort op haar bankrekening. Zij heeft verklaard tegen haar moeder te hebben verteld dat medeverdachte [medeverdachte] geld had gewonnen in het casino. In zoverre is sprake geweest van gedragingen die meer omvatten dan het enkele voorhanden hebben van de betreffende geldbedragen en hebben die gedragingen een op het daadwerkelijk verbergen of verhullen van de criminele herkomst van dat door eigen misdrijf verkregen voorwerp ingericht karakter. De rechtbank komt ter zake van dit feit dan ook tot een bewezenverklaring.
De verdediging heeft voorts gesteld dat geen sprake is geweest van “computervredebreuk” in de zin van artikel 138ab van het Wetboek van Strafrecht, aangezien verdachte en haar medeverdachte geen beveiligingen hebben doorbroken en zij zich op reglementaire wijze, met behulp van een door de slachtoffers vrijwillig gegeven wachtwoord, de toegang hebben verschaft tot de computers van de slachtoffers. Ook dit betoogt slaagt niet. Van binnendringen in vorenbedoelde zin is ook sprake indien men zich de toegang tot een geautomatiseerd werk of een deel daarvan verschaft door met behulp van valse signalen of een valse sleutel dan wel het aannemen van een valse hoedanigheid. Dat laatste is in dit geval zeker van toepassing, aangezien verdachte en haar medeverdachte een autorisatie door de ‘eigenaar’ hebben voorgewend. Ook op dit punt komt de rechtbank tot een bewezenverklaring.
Bewezenverklaring
Naar het oordeel van de rechtbank is wettig en overtuigend bewezen dat de verdachte het onder 1, 2, 3 en 4 ten laste gelegde heeft begaan, te weten dat:
1.
zij op tijdstippen in de periode van 01 februari 2012 tot en met 03 maart 2012 te Putten en/of een of meerdere andere plaats(en) in Nederland, telkens ter uitvoering van het voornemen en het misdrijf om, tezamen en in vereniging met een ander, met het oogmerk om zichof een ander wederrechtelijk te bevoordelen, door bedreiging met smaad, smaadschrift of openbaring van een geheim, meerdere personen ([benadeelde 1] en [benadeelde 2] en [benadeelde 3] en [benadeelde 4]) te dwingen tot de afgifte van een geldbedrag (variërend tussen de 500 en 2.000 Euro), dat geheel of ten dele toebehoort aan die [benadeelde 1] en/of [benadeelde 2] en/of [benadeelde 3] en/of [benadeelde 4], welke bedreiging met smaad, smaadschrift of openbaring van een geheim hieruit bestond dat verdachte en haar mededader telkens voornoemde [benadeelde 1] en [benadeelde 2] en [benadeelde 3] en die [benadeelde 4] (telkens) een of meerdere sms-bericht(en) e-mail(s) hebben gestuurd en/of een of meerdere telefoongesprekken met die [benadeelde 1] en/of die [benadeelde 2] en/of die [benadeelde 3] en/of die [benadeelde 4] hebben gevoerd, waarin gedreigd werd de (pedo)seksuele geaardheid en/of een of meerdere door die [benadeelde 1] en/of [benadeelde 2] en/of [benadeelde 3] en/of die [benadeelde 4] gepleegde strafbare feiten en/of een of meerdere door/van hen gemaakte
videobeelden openbaar te maken, terwijl de uitvoering van dit voorgenomen misdrijf niet is voltooid;
2.
zij op tijdstippen in of omstreeks de periode van 01 februari tot en met 03 maart 2012, te Rotterdam tezamen en in vereniging met een ander voorwerpen, te weten geldbedragen heeft verworven, voorhanden heeft gehad, heeft overgedragen en/of omgezet, althans van die/dat geldbedrag(en), gebruik heeft gemaakt, terwijl verdachte en haar mededader wisten dat bovenomschreven voorwerpen - onmiddellijk of middellijk - afkomstig wa s ren uit enig misdrijf;
3.
zij op tijdstippen in of omstreeks de periode van 01 februari 2012 tot en met 03 maart 2012 te Rotterdam (telkens) tezamen en in vereniging met een ander opzettelijk en wederrechtelijk gegevens (te weten: een of meerdere e-mailberichten en/of foto's en/of videobeelden) die door middel van een geautomatiseerd werk of door middel van een telecommunicatie waren opgeslagen en/of werden verwerkt en/of overgedragen, heeft gewist en/of ontoegankelijk gemaakt, door met voornoemd opzet de wachtenwoorden van de e-mailaccounts,
- [e-mailaccount 2], en
- [e-mailaccount 3], en
- [e-mailaccount 4], en
- [e-mailaccount 6], en
- het e-mailadres van een persoon zich noemende [naam 1], en
- het e-mailadres van een persoon zich noemende [naam 2]
[naam 2], en
- het e-mailadres van een persoon zich noemende [naam 3], en
- het e-mailadres van een persoon zich noemende [naam 5], en
- het e-mailadres van een persoon zich noemende [naam 9], en
- het e-mailadres van een persoon zich noemende [naam 11]
[naam 11],
waarin die berichten en/of die foto's en/of die videobeelden werden
opgeslagen, te wijzigen;
4.
zij op tijdstippen in of omstreeks de periode van 01 februari 2012 tot en met 03 maart 2012 te Rotterdam tezamen met een ander opzettelijk en wederrechtelijk in geautomatiseerde werken, te weten e-mailaccount(s), te weten:
- [e-mailaccount 2], en
- [e-mailaccount 3], en
- [e-mailaccount 4], en
- [e-mailaccount 6], en
- het e-mailadres van een persoon zich noemende [naam 1], en
- het e-mailadres van een persoon zich noemende [naam 2]
[naam 2], en
- het e-mailadres van een persoon zich noemende [naam 3], en
- het e-mailadres van een persoon zich noemende [naam 5], en
- het e-mailadres van een persoon zich noemende [naam 9], en
- het e-mailadres van een persoon zich noemende [naam 11]
[naam 11],
of in een deel daarvan, is binnengedrongen, waarna verdachte vervolgens
gegevens, die waren opgeslagen, werden verwerkt of werden overgedragen door
middel van die geautomatiseerde werken waarin verdachte zich wederrechtelijk bevond, voor zichzelf of een ander heeft overgenomen, afgetapt of opgenomen.
Voor zover in de tenlastelegging taal- en/of schrijffouten en/of kennelijke omissies voorkomen, zijn deze in de bewezenverklaring verbeterd. De verdachte is daardoor niet geschaad in de verdediging.
Strafbaarheid van het bewezenverklaarde
Het bewezene levert de navolgende strafbare feiten op:
feit 1: poging tot medeplegen van afdreiging, meermalen gepleegd;
feit 2: medeplegen van witwassen, meermalen gepleegd;
feit 3: medeplegen van opzettelijk en wederrechtelijk gegevens die door middel van een geautomatiseerd werk of door middel van telecommunicatie zijn opgeslagen, worden verwerkt of overgedragen, wissen, onbruikbaar of ontoegankelijk maken, meermalen gepleegd;
feit 4: medeplegen van computervredebreuk, meermalen gepleegd.
Strafbaarheid van de verdachte
Verdachte is strafbaar, nu geen omstandigheid is gebleken of aannemelijk geworden die de strafbaarheid van verdachte uitsluit.
Oplegging van straf en/of maatregel
De officier van justitie heeft gevorderd dat verdachte terzake van de door haar onder 1, 2, 3 en 4 bewezen geachte feiten zal worden veroordeeld tot een voorwaardelijke gevangenisstraf voor de duur van zes maanden met een proeftijd van twee jaar en een werkstraf van 240 uur, subsidiair 120 dagen vervangende hechtenis met aftrek van de dagen in verzekering doorgebracht. De officier heeft in de strafeis onder meer betrokken dat verdachte en haar medeverdachte inbreuk hebben gemaakt op de persoonlijke levenssfeer van hun slachtoffers en dat de bedreiging van de onder 1 genoemde slachtoffers weliswaar andersoortig is dan de bedreiging in de zin van artikel 317 van het Wetboek van Strafrecht, maar dat deze bedreigingen zeker niet minder ernstig zijn. Daarnaast heeft de officier rekening gehouden met de persoonlijke omstandigheden van verdachte, het feit dat verdachte een blanco straf blad heeft en haar leven inmiddels weer aardig op de rails heeft en dat de gepleegde feiten al weer enige tijd – anderhalf jaar – geleden hebben plaatsgevonden. Dit maakt dat de officier aanleiding heeft gezien om geen onvoorwaardelijke gevangenisstraf te vorderen.
De raadsvrouw heeft bepleit om in het geval van een veroordeling geen voorwaardelijke gevangenisstraf op te leggen. De raadsvrouw heeft onder meer aangevoerd dat de feiten anderhalf jaar geleden hebben plaatsgevonden en dat in november 2012 uit de relatie van verdachte met de medeverdachte [medeverdachte] een zoontje is geboren voor wie verdachte zorg draagt. De onderhavige strafzaak, de consequenties die de strafzaak reeds heeft gehad en daarnaast de extreme spanningen die de strafzaak met zich brengt, maken dat geen voorwaardelijke gevangenisstraf behoeft te worden opgelegd, aangezien de kans dat verdachte ooit weer met justitie in aanraking zal komen gering is en de onderhavige feiten als een eenmalige gebeurtenis moeten worden beschouwd.
De rechtbank acht na te melden beslissing in overeenstemming met de aard en de ernst van het bewezenverklaarde en de omstandigheden waaronder dit is begaan, mede gelet op de persoon van verdachte, zoals van een en ander tijdens het onderzoek ter terechtzitting is gebleken. De rechtbank heeft verder het volgende in aanmerking genomen.
Verdachte heeft samen met haar medeverdachte ernstige inbreuk gemaakt op de persoonlijke levenssfeer van een aantal door haar en haar medeverdachte geselecteerde slachtoffers. Verdachte en haar medeverdachte hebben aangevoerd daarmee vermeende (pedofiele) praktijken aan de kaak te willen stellen en hun slachtoffers onder druk te willen zetten daarmee op te houden. Verdachte en haar medeverdachte hebben dat motief echyter tevens aangewend om ten behoeve van eigen gewin geld te verkrijgen. Verdachte en haar medeverdachte zijn daarbij stelselmatig te werk gegaan. Verdachte heeft een blanco strafblad.
De reclassering heeft geen strafadvies uitgebracht. Contra-indicaties voor het opleggen van werkstraf zijn er niet. Het recidiverisico wordt als laag ingeschat.
Uit het rapport van de reclassering van 31 juli 2013 komt naar voren dat verdachte een enigszins starre en stereotype denktrant heeft, waardoor zij van mening was dat de slachtoffers het verdienden afgeperst te worden. Zij dacht dat zij goed bezig was, maar ziet nu in dat zij te ver is gegaan. Zij heeft een laag gemiddeld IQ en heeft hierdoor enige beperkingen in haar sociale en cognitieve vaardigheden. Zij kan enigszins impulsief zijn, waardoor zij niet goed nadenkt over de gevolgen van haar gedrag. Zij heeft een Wajong uitkering. Zij heeft samen met medeverdachte [medeverdachte] een baby van – inmiddels – negen maanden oud. Er zijn geen problematische schulden.

De rechtbank acht, gelet op het vorenstaande, een strafoplegging zoals door de officier van justitie gevorderd op zijn plaats, maar ziet in de persoonlijke omstandigheden van de verdachte aanleiding om de gevorderde werkstraf enigszins te matigen. De rechtbank acht een voorwaardelijke gevangenisstraf aangewezen, niet zo zeer vanwege het zoveel mogelijk beperken van de kans op recidive, maar veel meer om de ernst van de onderhavige feiten te benadrukken. Zij zal daarom geen reclasseringstoezicht opleggen.
Vorderingen tot schadevergoeding en/of schadevergoedingsmaatregel
De benadeelde partij [benadeelde 4] heeft zich met een vordering tot schadevergoeding ten bedrage van € 476,53 (immaterieel € 300,00, materieel € 176,53) ter zake de door hem geleden schade gevoegd in het strafproces ten aanzien van het tenlastegelegde.
De officier van justitie heeft zich op het standpunt gesteld dat de vordering van de benadeelde partij integraal kan worden toegewezen.
De raadsvrouw heeft zich op het standpunt gesteld dat de vordering ten aanzien van de immateriële schade dient te worden afgewezen dan wel dient te worden verminderd tot maximaal € 100, aangezien de onderhavige zaak de vergelijking met de uitspraak van de rechtbank Utrecht (LJN: BA5303) waarnaar de benadeelde partij heeft verwezen, niet kan doorstaan. In die uitspraak ging het om een forse afdreiging van iemand die prostituees bezocht, welke gedraging niet strafbaar was. Ten aanzien van de materiële schade dienen de opgenomen verlofuren buiten beschouwing te worden gelaten.
Naar het oordeel van de rechtbank is, op grond van de gebezigde bewijsmiddelen en wat verder ter terechtzitting met betrekking tot de vordering is gebleken, komen vast te staan dat de benadeelde partij als gevolg van het bewezen verklaarde handelen rechtstreeks schade heeft geleden, waarvoor verdachte naar burgerlijk recht aansprakelijk is.
De rechtbank begroot de immateriële schade, rekening houdende met alle omstandigheden, naar billijkheid op een bedrag van € 100,00. De materiële schade zal de rechtbank beperken tot een bedrag van € 135,17, aangezien zij de opgegeven hoeveelheid gederfde verlofuren bovenmatig acht en een matiging tot zes uren billijk acht. De vordering zal dan ook worden toegewezen tot een bedrag van € 235,17 en de benadeelde partij zal voor het overige 
niet-ontvankelijk worden verklaard in zijn vordering.
Gelet op het voorgaande ziet de rechtbank aanleiding om aan verdachte op basis van het bepaalde in artikel 36f van het Wetboek van Strafrecht de verplichting op te leggen tot betaling aan de Staat van na te melden bedrag ten behoeve van genoemd slachtoffer.
In beslag genomen voorwerpen
De officier van justitie heeft verbeurdverklaring gevorderd van de op de lijst van inbeslaggenomen voorwerpen onder de nummers 2, 3, 4 en 6 vermelde voorwerpen. De officier heeft verder de teruggave gevorderd van de op voormelde lijst onder 8 vermelde computer aan [medeverdachte].
De raadsvrouw heeft aangevoerd dat er redenen zijn – beperkte financiële draagkracht – om, hoewel er sprake is van medeplegen van een strafbaar feit, de laptop/notebook (nummer 3 van de lijst) te doen teruggeven aan verdachte.

De rechtbank is van oordeel dat de onder verdachte in beslag genomen laptop/notebook, volgens opgave van verdachte aan haar toebehorend, vatbaar is voor verbeurdverklaring, nu het een voorwerp is met behulp waarvan het bewezenverklaarde is begaan en voorbereid.
De rechtbank heeft hierbij rekening gehouden met de draagkracht van verdachte.
Ten aanzien van de overige voorwerpen zal de rechtbank de officier van justitie in deze strafzaak niet ontvankelijk verklaren in haar vordering, aangezien het ziet op goederen die onder de medeverdachte [medeverdachte] in beslag zijn genomen en waarvan de verdachte en de medeverdachte te kennen hebben gegeven dat deze voorwerpen aan hem toebehoren.
Toepasselijke wettelijke voorschriften
Deze strafoplegging is gegrond op de artikelen 10, 14a, 14b, 14c, 22c, 22d, 24c, 27, 33, 33a, 36f, 45, 47, 57, 138ab, 350a, 318 en 420bis van het Wetboek van Strafrecht. Beslissing
De rechtbank:
 wijst het verzoek tot schorsing van het onderzoek ter terechtzitting ten behoeve van het horen van aangever [benadeelde 1] als getuige af ;

 verklaart, zoals hiervoor overwogen, bewezen dat verdachte het onder 1, 2, 3 en 4 tenlastegelegde heeft begaan;

 verklaart niet bewezen hetgeen verdachte meer of anders is ten laste gelegd dan hierboven is bewezen verklaard en spreekt verdachte daarvan vrij;

 verklaart het bewezenverklaarde strafbaar, kwalificeert dit als:

de misdrijven:
feit 1: poging tot medeplegen van afdreiging, meermalen gepleegd;
feit 2: medeplegen van witwassen, meermalen gepleegd;
feit 3: medeplegen van opzettelijk en wederrechtelijk gegevens die door middel van een geautomatiseerd werk of door middel van telecommunicatie zijn opgeslagen, worden verwerkt of overgedragen, wissen, onbruikbaar of ontoegankelijk maken, meermalen gepleegd ;
feit 4: medeplegen van computervredebreuk, meermalen gepleegd
en verklaart verdachte hiervoor strafbaar;
-
veroordeelt verdachte tot een gevangenisstraf voor de duur van zes (6) maanden ;
-
bepaalt, dat de gevangenisstraf niet zal worden ten uitvoer gelegd , tenzij de rechter later anders mocht gelasten, op grond dat veroordeelde zich vóór het einde van een proeftijd van 2 jaren aan een strafbaar feit heeft schuldig gemaakt;
 veroordeelt de verdachte tot de navolgende taakstraf , te weten:
een werkstraf gedurende honderdtachtig (180) uren , met bevel dat indien deze straf niet naar behoren wordt verricht vervangende hechtenis zal worden toegepast voor de duur van 90 dagen;

 beveelt dat voor de tijd die door de veroordeelde vóór de tenuitvoerlegging van de taakstraf in verzekering is doorgebracht, bij de uitvoering van die straf uren in mindering worden gebracht volgens de maatstaf dat per dag in verzekering doorgebracht 2 uur in mindering wordt gebracht;

 verklaart verbeurd de op de lijst van inbeslaggenomen voorwerpen onder 3 vermelde HP notebook / laptop;

 verklaart de officier van justitie voor het overige niet-ontvankelijk in haar vordering tot verbeurdverklaring dan wel teruggave van in beslag genomen voorwerpen;

 veroordeelt verdachte ten aanzien van de feiten 1, 3 en 4 tot betaling van schadevergoeding aan de benadeelde partij [benadeelde 4] van een bedrag van
€ 235,17 vermeerderd met de wettelijke rente vanaf 3 maart 2012, met veroordeling van verdachte in de kosten van het geding en de tenuitvoerlegging door de benadeelde partij gemaakt, tot op heden begroot op nihil;

 verklaart de benadeelde partij voor het overige niet-ontvankelijk in zijn vordering;

 legt aan veroordeelde de verplichting op om aan de Staat , ten behoeve van het slachtoffer [benadeelde 4] voornoemd een bedrag te betalen van € 235,17 vermeerderd met de wettelijke rente vanaf 3 maart 2012, met bevel dat bij gebreke van betaling en verhaal vier dagen hechtenis zal kunnen worden toegepast zonder dat de betalingsverplichting vervalt;

 bepaalt dat, indien veroordeelde heeft voldaan aan de verplichting tot betaling aan de Staat daarmee de verplichting tot betaling aan de benadeelde partij in zoverre komt te vervallen en andersom dat, indien veroordeelde heeft voldaan aan de verplichting tot betaling aan de benadeelde partij daarmee de verplichting tot betaling aan de Staat in zoverre komt te vervallen;

 verstaat dat indien en voor zover door de medeveroordeelde het betreffende schadebedrag is betaald, veroordeelde daarvan zal zijn bevrijd;

 heft op het – geschorste – bevel tot voorlopige hechtenis.

Aldus gewezen door mr. Welbergen, voorzitter, mr. E.G. De Jong en mr. Kropman, rechters, in tegenwoordigheid van Van Bun, griffier, en uitgesproken op de openbare terechtzitting van 27 augustus 2013.
Mr. De Jong is buiten staat dit vonnis mede te ondertekenen.

""".decode(errors="ignore")

print model.decision_function(parseText(text))
print model.predict(parseText(text))