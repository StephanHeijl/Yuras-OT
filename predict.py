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
Het geding in eerste aanleg
In eerste aanleg is geprocedeerd en beslist zoals weergegeven in de vonnissen van 1 december 2010, 7 september 2011 en 7 maart 2012 van de rechtbank Assen.
2 Het geding in hoger beroep
2.1
Het verloop van de procedure is als volgt:
- de dagvaarding in hoger beroep d.d. 6 juni 2012;
- de memorie van grieven;
- de memorie van antwoord tevens van grieven in incidenteel hoger beroep (met producties);
- de memorie van antwoord in incidenteel hoger beroep.

2.2
Vervolgens heeft [appellant] de stukken voor het wijzen van arrest overgelegd en heeft het hof arrest bepaald.

2.3
De vordering van [appellant] luidt:
"bij arrest, bij voorraad uitvoerbaar, te vernietigen het vonnis dat de Rechtbank Assen op
7 maart 2012 onder rolnummer 81519 tussen partijen heeft gewezen, en, opnieuw rechtdoende:
Ad 1:	geïntimeerde te veroordelen om tegen behoorlijk bewijs van kwijting aan appellant
te betalen een bedrag van € 450,= ter zake van het omwisselen van de ps kisten, te
vermeerderen met de wettelijke rente over dit bedrag vanaf de dag van de inleidende
dagvaarding tot de dag der algehele voldoening;
Ad 2:	geïntimeerde te veroordelen om tegen behoorlijk bewijs van kwijting aan appellant
te betalen een bedrag van € 3.250,= ter zake van de post extra wapening, te
vermeerderen met de wettelijke rente over dit bedrag vanaf de dag van de inleidende
dagvaarding tot de dag der algehele voldoening;
Ad 3:	geïntimeerde te veroordelen om tegen behoorlijk bewijs van kwijting aan appellant
te betalen een bedrag van € 25.134,47 ter zake van de herstelkosten aan de berg- en
kapschuur, te vermeerderen met de wettelijk rente over dit bedrag vanaf de dag van
de inleidende dagvaarding tot de dag der algehele voldoening;
Ad 4: geïntimeerde te veroordelen om tegen behoorlijk bewijs van kwijting aan appellant
te betalen een bedrag van € 1.038,43 ter zake van herstelkosten aan het stookhutje,
te vermeerderen met de wettelijke rente over dit bedrag vanaf de dag van de
inleidende dagvaarding tot de dag der algehele voldoening;
Ad 5:	geïntimeerde te veroordelen om aan appellant te betalen een bedrag van € 2.008,13
ter zake van het rapport van de heer ing. [deskundige], te vermeerderen met de
wettelijke rente over dit bedrag vanaf de dag van het nemen van de onderhavige
memorie tot op de dag der algehele voldoening;
Ad 6: geïntimeerde te veroordelen om tegen behoorlijk bewijs van kwijting aan appellant
te betalen een bedrag van € 531,17 ter zake van de nota van de heer [betrokkene 1], te
vermeerderen met de wettelijke rente over dit bedrag vanaf de dag van het nemen
van onderhavige memorie tot de dag der algehele voldoening;
Ad 7:	geïntimeerde te veroordelen in de kosten van beide instanties."
2.4
In incidenteel appel heeft [geïntimeerde] gevorderd:
"bij arrest, voor zover mogelijk uitvoerbaar bij voorraad:
In appel
1.	De vorderingen van [appellant] af te wijzen, dan wel hem deze te ontzeggen, dan wel
te bepalen dat op het bedrag dat aan [appellant] wordt toegewezen het reeds betaald
bedrag van € 7020,90 (vermeerder met rente vanaf 15 mei 2012 tot de datum der
voldoening) in mindering wordt gebracht
In zelfstandig appel
2. Te verklaren voor recht dat [appellant] een vordering heeft op [appellant] Vastgoed
BV, tot een bedrag van € 7020,90 (vermeerderd met rente vanaf 15 mei 2012 tot de
datum der voldoening), dan wel tot een zodanig bedrag dat in deze juist wordt
geacht en daarbij te bepalen dat deze vordering rechtsgeldig is overgedragen en
verrekend met de schuld van [geïntimeerde] aan [appellant], waardoor deze vordering is
teniet gegaan tot het bedrag van € 7020,90.
subsidiair
[appellant] te veroordelen tot betaling aan [geïntimeerde] tot een bedrag van € 7020,90,
dan wel tot betaling van een zodanig bedrag dat in deze juist wordt geacht, te
vermeerderen met rente van 15 mei 2012 tot de datum der algehele voldoening.
In appel en zelfstandig appel
3.	[appellant] te veroordelen in de kosten van de procedure in eerste aanleg en appel."
3 De ontvankelijkheid
In de appeldagvaarding wordt hoger beroep ingesteld tegen alle door de rechtbank gewezen vonnissen. Tegen het vonnis van 1 december 2010 zijn echter geen grieven geformuleerd zodat [appellant] in zoverre niet-ontvankelijk is zijn hoger beroep.
4 De feiten
4.1
De rechtbank heeft in haar vonnis van 7 september 2011 onder 2 (2.1 tot en met 2.3) feiten vastgesteld waartegen geen grieven zijn gericht en ook is niet anderszins van bezwaren is gebleken. Samen met hetgeen is komen vast te staan gaat het, voor zover in hoger beroep van belang, om het volgende.

4.2
Tussen partijen is een aannemingsovereenkomst tot stand gekomen op grond waarvan [geïntimeerde] in opdracht en voor rekening van [appellant] diens boerderij zou verbouwen alsmede een berg- en kapschuur en een stookhut zou bouwen. Daartoe hebben zij een opdrachtbevestiging d.d. 8 oktober 2009 ondertekend. De werkzaamheden zouden in regie worden uitgevoerd tegen een tarief van € 35,- per uur exclusief btw. Voorts vermeldt de overeenkomst onder meer:



“De verbouwing gaat conform de tekening en de constructie berekening van de architect Dhr [architect]. Wijzigingen en/of meerwerk worden alleen uitgevoerd na overleg met Dhr. [appellant] of diens partner. Verder dienen wij zorg voor de uitvoering van de werkzaamheden en in overleg zorgen wij ook voor de onderaanneming van de installateur, dakdekker, kraanwerkzaamheden, metselwerken het inhuren van specialisten en werklui.”.

4.3
[geïntimeerde] is op 19 oktober 2009 met de werkzaamheden begonnen. Van 16 december 2009 tot het voorjaar van 2010 is [geïntimeerde] tijdelijk gestopt met het werk vanwege de weersomstandigheden.

4.4
Op 25 december 2009 is door barre weersomstandigheden het achterhuis van de boerderij ingestort. [appellant] heeft daarop van zijn verzekeraar een uitkering ontvangen van € 98.000,-.

4.5
Op 7 mei 2010 is [geïntimeerde] gestopt met zijn werkzaamheden. Hij heeft daarna de sleutels ingeleverd en het bouwdepot verrekend.

4.6
In opdracht van [appellant] is door Bouw- Adviesbureau Ing. [deskundige] een rapport geschreven, bestaande uit drie delen waarbij afzonderlijk de “voormalige woonboerderij met voorhuis”, de “schuur- en kapschuur” en de “stookhut” zijn beoordeeld. Als producties 2 t/m 4 bij de inleidende dagvaarding zijn de drie volgende delen overgelegd, die steeds gebaseerd zijn op een inspectie die is gehouden op 8 juni 2010. Alle drie de delen zijn op het voorblad aangeduid als “ Versie 3 juli 2010” .

4.7
Als productie 5 en 6 bij de inleidende dagvaarding zijn getallenoverzichten afkomstig van [deskundige] overgelegd met het opschrift “Calculatie van de herstelwerkzaamheden” .

4.8
Als productie 24 bij conclusie van repliek heeft [appellant] een tweede versie van een deel van het rapport [deskundige] overgelegd met het opschrift:

“ Bouwkundige inspectie van de voormalige boerderij met voorhuis
Verkorte versie 7 maart 2011, geënt op de regelgeving en bouwkundige normen.”

Deze versie wijkt inhoudelijk af van de hiervoor genoemde versie 3 juli 2010 van het rapport [deskundige] (zie 4.6). Zo wordt in de eerste versie over een gebrek van de panlatten geen melding gemaakt en in de tweede versie wel.
5 De vordering in eerste aanleg
5.1
[appellant] vordert, verkort weergegeven, na twee vermeerderingen en een vermindering van eis:
a. ontbinding van de tussen partijen gesloten overeenkomst;
b. vergoeding door [geïntimeerde] van € 49.240,07 aan herstelkosten te vermeerderen met rente;
c. betaling door [geïntimeerde] van € 4.298,34 (ter zake van herstel van kozijnen);
d. betaling door [geïntimeerde] van € 2.665,60 (ter zake van een factuur van Adviesbureau [adviesbureau] B.V.);
e. betaling door [geïntimeerde] van € 1.258,- (ter zkae van een factuur van [bouwbedrijf] Bouwbedrijf B.V.

5.2
[appellant] stelt daartoe dat [geïntimeerde] de hem opgedragen werkzaamheden niet goed heeft uitgevoerd. De gevorderde herstelkosten van € 29.270,07 betreffen de voormalige boerderij met woonhuis voor € 24.105,60 en de bergschuur en kapschuur.

5.3
De rechtbank heeft in haar eindvonnis van 7 maart 2012 [geïntimeerde] veroordeeld tot betaling van € 5.594,63 vermeerderd met wettelijke rente over dat bedrag met ingang van
5 augustus 2010.

6 De grieven
6.1
In het principaal appel zijn zes grieven geformuleerd. De grieven 1 en 2 betreffen de fundering van de woonboerderij en grief 3 betreft de berg- en kapschuur alsmede het stookhutje. In grief 4 verzet [appellant] zich tegen de afwijzing door de rechtbank van een door [appellant] gewenste eisvermeerdering. Grief 5 betreft de proceskostenveroordeling en grief 6 is een veeggrief die zelfstandige betekenis mist. Het incidenteel appel omvat een ongenummerde grief gericht tegen de toewijzing door de rechtbank van een vergoeding ter zake van de panlatten, de kozijnen en de fundering.

6.2
Inleidende overwegingen

6.2.1
Centraal staat in deze zaak de vraag of [geïntimeerde] zijn werkzaamheden ondeugdelijk heeft uitgevoerd.

6.2.2
Over de volgende posten bestaat in hoger beroep discussie:

de woonboerderij met voorhuis:
a. de panlatten (incidenteel appel);
b. de kozijnstijlen (incidenteel appel);
c. de fundering (de grieven 1 en 2 principaal appel/incidenteel appel);
de berg- en kapschuur:

d. de muren (grief 3 principaal appel);
e. de kapconstructie (punt 161 e.v. en punt 167 memorie van grieven);
f. de hoofddraagconstructie van de kapschuur (punt 169 memorie van grieven);
g. de deuren van de garage (punt 173 memorie van grieven);
h. boeiboorden en waterkering van de kapschuur (punt 174 memorie van grieven);
i. lood onder de ramen van de kapschuur (punt 175 memorie van grieven);
afwerking dakpannen en dakgoten kapschuur (punt 176 memorie van grieven).
de stookhut:

j. boeiboorden, afdekkers, plaatmateriaal onder de hoek (grief 3 principaal appel);
k. onder de afdekkers geen waterkering (grief 3 principaal appel).
6.2.3
Het hof zal de grieven thematisch behandelen.

6.3
De fundering (de grieven 1 en 2 in het principaal appel en het incidenteel appel)

6.3.1
De rechtbank heeft in haar vonnis van 7 maart 2012 ten aanzien van de fundering overwogen:

“Ten aanzien van de foutief bestelde kisten en de wijze van aanbrengen van de wapening had de rechtbank reeds overwogen dat gedaagde ondeugdelijk werk heeft verricht en de daaruit voortvloeiende schade voor eiser aan hem dient te vergoeden.”

[geïntimeerde] heeft weliswaar gesteld dat hij met betrekking tot de fundering fouten heeft gemaakt maar hij heeft niet weersproken dat door hem onjuiste kisten voor de fundering zijn besteld.
6.3.2
Het gaat in hoger beroep dus uitsluitend nog om de omvang van de vordering.
[appellant] vordert een bedrag van € 6.365,60 dat als volgt is gespecificeerd:

- de factuur van [adviesbureau]	€ 2.665,60
- het omwisselen van de ps-kisten	€  450,-
- extra fundering € 3.250,-

6.3.3
De rechtbank heeft de vordering voor wat betreft de factuur van [adviesbureau] toegewezen (daartegen is het incidenteel appel gericht) en heeft van de gevorderde omwisselingskosten alleen de door [geïntimeerde] erkende transportkosten van € 160,- toegewezen (daartegen is grief 1 in het principaal appel en het incidenteel appel gericht). De kosten voor extra fundering € 3.250,- heeft de rechtbank afgewezen (daartegen is grief 2 in het principaal appel gericht).

6.3.4
Ter onderbouwing van zijn vordering verwijst [appellant] herhaalde malen naar het rapport [deskundige]. In de aan het hof overgelegde versies van dit rapport zijn echter geen berekeningen of andere verklaringen van de genoemde bedragen gegeven. Als productie 5 bij de inleidende dagvaarding wordt weliswaar een opsomming van de bedragen met betrekking tot de woonboerderij gegeven, echter zonder onderbouwing. Ten aanzien van de kosten voor extra fundering heeft [appellant] (proces-verbaal tweede comparitie) verklaard: “Naast het bedrag van € 618,54 dat ik betaald heb, heb ik ook de extra gewerkte uren moeten betalen. Daar heb ik geen specificatie van.” De rechtbank heeft, in hoger beroep onbestreden, vastgesteld dat dit een contante betaling betrof. [appellant] heeft de factuur van [adviesbureau] overgelegd, evenals een factuur afkomstig van [geïntimeerde] waarin een bedrag van € 618,54 voor extra staal staat vermeld.

6.3.5
In incidenteel appel (memorie van antwoord/incidenteel appel, randnummers 33 t/m 37) betoogt [geïntimeerde] dat hij niet is gehouden de factuur van 8 mei 2010 van [adviesbureau] te vergoeden. Vóór 8 mei 2010 had [appellant] geen klachten over het funderingswerk. Volgens [geïntimeerde] hebben de werkzaamheden van [adviesbureau] geen betrekking op het herstel van door [geïntimeerde] gemaakte fouten. Bovendien heeft [appellant], aldus [geïntimeerde], van zijn verzekeraar € 6.000,- ontvangen voor de fundering, zodat zijn schade met dat bedrag dient te worden verminderd.

6.3.6
In zijn memorie van antwoord in incidenteel appel heeft [appellant] niet gereageerd op dit gemotiveerde verweer door [geïntimeerde]. Het hof overweegt het volgende.

6.3.7
De fout door [geïntimeerde] bestaat er volgens [appellant] in dat te lage funderingskisten zijn gebruikt. Dat daardoor meer materiaal nodig was, is ook zonder nadere toelichting begrijpelijk. Zonder nadere toelichting, die ontbreekt, is echter niet zonder meer begrijpelijk dat daardoor nieuwe sterkteberekeningen zijn vereist. De enkele opmerking in de factuur dat sprake is geweest van “herberekening van de wapening van alle funderingsbalken omdat de hoogte van de wapeningskorven sterk afweek van wat op de tekening was aangegeven”, is daartoe onvoldoende. Niet alleen was het pand van [appellant] recent buiten schuld van [geïntimeerde] ingestort maar bovendien is uit de geciteerde passage in de factuur niet te herleiden dat de te lage bekisting een herberekening nodig maakte. Dit alles geldt te meer daar gezien de datum van de factuur (8 mei 2010) de genoemde berekeningen en tekeningen kennelijk zijn gemaakt op een moment dat [geïntimeerde] nog aan het werk was. Het incidenteel appel slaagt voor wat betreft de funderingskosten, zodat de vergoeding van de factuur van [adviesbureau] alsnog zal worden afgewezen.

6.3.8
Voor het bedrag van € 450,- wegens omwisselen van de kisten ontbreekt ook in hoger beroep iedere onderbouwing, zodat deze vordering voor het niet erkende deel van € 290,- terecht is afgewezen. Grief 1 in het principaal appel faalt.

6.3.9
Voor wat betreft het bedrag van € 3.250,- wegens extra fundering geldt eveneens dat een deugdelijke onderbouwing ontbreekt. Zelfs een eenvoudige berekening van de gebruikte hoeveelheid extra beton en ander materiaal gerelateerd aan daarvoor normaliter gekoppelde prijzen is niet gegeven. Ook in de rapportages van [deskundige] (waarnaar herhaald wordt verwezen), ontbreekt een berekening die sluit op het door [appellant] gevorderde bedrag. Het ligt op de weg van [appellant] feiten en omstandigheden te stellen waaruit zijn vordering volgt. Zelfs de voor een schatting als bedoeld in artikel 6:97 BW vereiste feitelijke aanknopingspunten ontbreken. Grief 2 in het principaal appel faalt.

6.3.10
Het verweer van [geïntimeerde] dat op het toe te wijzen bedrag de verzekeringsuitkering in mindering dient te komen, gaat het hof voorbij nu dit verweer niet of onvoldoende is onderbouwd. Op zich staat vast dat sprake is van een verzekeringsuitkering, maar dat deze ook dient om de transportkosten van € 160,- voor het omwisselen van de kisten te dekken volgt niet uit hetgeen is gesteld of gebleken.

6.4
De kosten van herstel aan de berg- en kapschuur en het stookhutje

6.4.1
Voorop staat dat de opsomming door de rechtbank van de gebreken aan de berg- en kapschuur en het stookhutje (hierna: de schuren en het hutje) onder 2.17 niet meer of minder is dan een weergave van de door [appellant] gestelde gebreken zonder dat de rechtbank die gebreken daarmee als vaststaand beschouwt. [appellant] kent daaraan in zijn grief ten onrechte een verderstrekkende betekenis toe.

6.4.2
Ook hier geldt dat het aan [appellant] is feiten en omstandigheden te stellen en zo nodig te bewijzen waaruit volgt dat de door [deskundige] in zijn rapport opgesomde feiten het gevolg zijn van door [geïntimeerde] gemaakte fouten en wat die fouten zijn. Uit de thans door [appellant] gekozen onderbouwing volgt niet meer dan dat sprake is van schuren en een hutje waaraan gebreken zijn vastgesteld. Een omschrijving, bijvoorbeeld van de werkzaamheden aan de schuren en het hutje door [geïntimeerde] zijn uitgevoerd en in hoeverre gebruik is gemaakt van bestaande bouw ontbreekt. Duidelijkheid volgt evenmin uit de overgelegde overeenkomst van 8 oktober 2009. Het rapport van [deskundige] schetst weliswaar een beeld van schuren en een hut in een slechte bouwkundige staat maar tot welke fouten door [geïntimeerde] de bouwkundige problemen zijn te herleiden, is niet toereikend onderbouwd.

6.4.3
Anderzijds zijn partijen het er over eens dat [geïntimeerde] een dak op de schuren heeft aangebracht waarvan [deskundige] concludeert dat dit veel te zwaar is voor de muren, waardoor er (kort gezegd) instortingsgevaar bestaat. [geïntimeerde] heeft echter gesteld dat hij handelde op uitdrukkelijk instructie van [appellant]. Dat [geïntimeerde] een waarschuwingsplicht heeft geschonden is door [appellant] niet aan zijn vordering ten grondslag gelegd.

6.4.4
Daarmee is de vraag of hetgeen reeds door [appellant] is aangevoerd voldoende ruimte biedt voor nadere verdieping van die feitelijke grondslag om aan te tonen dat [geïntimeerde] toerekenbaar te kort is geschoten. Het hof acht het zinvol dat partijen dienaangaande op een comparitie hun standpunten toelichten. Alvorens verder aangaande grief 3 te beslissen zal het hof daarom eerst een comparitie van partijen gelasten.

6.5
In grief 4. verzet [geïntimeerde] zicht tegen de afwijzing door de rechtbank van de vermeerdering van eis. In dit deel van zijn hoger beroep kan [geïntimeerde] echter niet worden ontvangen nu artikel 130 lid 2 Rv een hogere voorziening tegen een dergelijke beslissing uitsluit.
6.5.1
De beslissingen aangaande de grieven 5 en 6 houdt het hof aan.

6.6
De panlatten (incidenteel appel)

6.6.1
In het incidenteel appel betoogt [geïntimeerde] dat er geen noodzaak was de door hem aangebrachte panlatten te vervangen door nieuwe. Het hof overweegt dienaangaande het volgende.

6.6.2
Bij conclusie van repliek (randnummer 78 en 79) concretiseert [appellant] voor het eerst welke gebreken vervanging van de door [geïntimeerde] aangebrachte panlatten nodig maakte:


“78. (…) Wat [appellant] in dit opzicht aan [geïntimeerde] verwijt is dat hij onder elke panlat een klein latje heeft geschroefd, met als gevolg dat elke panlat een scharnier was, waardoor de pannen zijn gaan bewegen.
79. Daarnaast was de onderlinge verdeling van de pannen niet goed. Met als gevolg dat de pannen er niet op pasten. [appellant] had dus geen andere keuze dan firma [bouwbedrijf] te vragen alle panlatten en tengellatten te verwijderen en opnieuw aan te brengen. Daarop ziet een gedeelte van de tweede vermeerdering van eis.”
6.6.3
In het rapport [deskundige] van 7 maart 2011 is het volgende vermeld:


“Gangbaar is dat de panlatten op de tengellatten liggen. De panlatten liggen horizontaal en de tengellatten lopen van de nok naar de voet van het dak, dus verticaal. De aannemer heeft onder elke panlat een klein latje geschroefd. Elke panlat was toen een scharnier de pannen gaan dan bewegen.
Ook de onderlinge verdeling was niet goed, de pannen pasten er niet op. Bouwbedrijf [bouwbedrijf] uit Tynaarlo heeft alle panlatten en tegellatten weer verwijderd.”
6.6.4
Het vorenstaande is een herhaling van de discussie die in eerste aanleg al is gevoerd. De rechtbank heeft ten aanzien van dit deel van de vordering onder 5.22. t/m 5.24 overwogen dat [geïntimeerde] onvoldoende heeft weersproken dat hij werkzaamheden aan het dak van het voorhuis heeft verricht en dat hij in dat licht bezien duidelijker had moeten weerleggen dat de door hem uitgevoerde werkzaamheden onjuist zijn verricht.

6.6.5
In hoger beroep betoogt [geïntimeerde] niet langer dat hij geen werkzaamheden aan het dak van het voorhuis heeft verricht. Hij stelt echter dat de wijze waarop hij de panlatten heeft bevestigd niet onjuist was. De door [appellant] gestelde onjuiste verdeling van de panlatten op het dak, waardoor de pannen niet pasten, laat [geïntimeerde] onweersproken. Daarmee kan aan de discussie aangaande de bevestigingswijze van de panlatten voorbij worden gegaan. Immers ook als de panlatten op de juiste wijze, maar op de verkeerde plaats zijn aangebracht zodat de pannen daarop niet passen, dienden zij te worden verwijderd en opnieuw te worden bevestigd. De omvang van dit deel van de vordering is door [geïntimeerde] niet bestreden. Uit het vorenstaande volgt dat de incidentele grief faalt voor wat betreft dit deel van de vordering.

6.7
De kozijnen

6.7.1
Voor wat betreft de kozijnen concretiseert [appellant] zijn vordering voor het eerst in zijn conclusie van repliek (randnummers 47 t/m 50 en 76). [appellant] stelt daar dat [geïntimeerde] is uitgegaan van het oude bouwbesluit dat een hoogte van 2011 mm voorschreef, terwijl dat op grond van het geldende bouwbesluit 2300 mm had moeten zijn. Bij deze wat cryptische omschrijving verwijst [appellant] naar het rapport [deskundige] (kennelijk doelend op versie 2), waar onder meer is vermeld:


“Binnendeur kozijnen
Volgens het bouwbesluit is de deurhoogte nu 2300 mm Dhr. [geïntimeerde] is uitgegaan van de voorgaande eis van 2011 mm. Daarom zijn alle stijlen te kort afgezaagd. Als oplossing werden er neuten ondergezet om p de juiste hoogte te komen. De is niet met de opdrachtgever besproken. Ook de deuren wilden niet goed open en dicht omdat de neuten de draairichting belemmerden.”
6.7.2
[geïntimeerde] heeft bij dupliek aangevoerd dat de kozijnen minimaal 2190 mm dienen te zijn en de neuten 150 mm en dat dit in overeenstemming is met het bouwbesluit. [appellant] heeft daarop gereageerd met het betoog dat [geïntimeerde] het tegenover hem deed voorkomen dat de neuten geplaatst werden om esthetische redenen. Volgens [deskundige] is dat, aldus [appellant], niet het geval. [geïntimeerde] voert daarop weer aan dat [appellant] bij het uitzoeken van de kozijnen en neuten aanwezig was en zijn toestemming heeft gegeven (naar het hof aanneemt voor het toepassen van neuten). [geïntimeerde] verwijst hierbij naar de ter comparitie van 14 februari 2011 overgelegde verklaring van [betrokkene 2]. De vordering is, aldus [geïntimeerde], onvoldoende onderbouwd.

6.7.3
De rechtbank overweegt in haar tussenvonnis van 7 september 2011 onder 5.27 dat [geïntimeerde] niet ingaat op de kritiek die [appellant] heeft op de verklaring van [betrokkene 2], op welke kritiek de rechtbank daarbij doelt wordt het hof niet duidelijk. De rechtbank gaat daarom uit van de juistheid van dit weerwoord. De rechtbank overweegt vervolgens dat aanwezigheid van [appellant] bij het uitzoeken van de neuten en de daarvoor gegeven toestemming, de stellingen van eiser op dit punt dan ook onverlet laat. [geïntimeerde] is, aldus de rechtbank, niet ingegaan op de stelling van [appellant] dat [geïntimeerde] de kozijnen te kort had afgezaagd waardoor het gebruik van neuten noodzakelijk werd. Het verweer van [geïntimeerde] wordt als onvoldoende gemotiveerd gepasseerd. De rechtbank overweegt dat [geïntimeerde] terzake ondeugdelijk werk heeft verricht en dat hij aansprakelijk is voor de daardoor geleden schade, die de rechtbank begroot op € 1.936.34.

6.7.4
[appellant] heeft tegen de hoogte van de door de rechtbank vastgestelde schade geen grief opgeworpen. Het incidenteel appel is uitsluitend gericht tegen de overweging van de rechtbank dat [geïntimeerde] ondeugdelijk werk heeft geleverd. Het hof overweegt dienaangaande het volgende.

6.7.5
Voor de grondslag van zijn vordering lijkt [appellant] enerzijds te steunen op strijd met het bouwbesluit, anderzijds op esthetische argumenten en dan weer op functionele problemen als gevolg van de gebruikte neuten.

6.7.6
Voor wat betreft de esthetische bezwaren geldt dat het hof deze als onvoldoende onderbouwd ter zijde laat. [appellant] stelt niet meer dan dat [deskundige] de neuten esthetisch niet vindt voldoen. Voor wat betreft het niet goed functioneren van de deuren geldt dat een deugdelijke onderbouwing ontbreekt, ook het rapport van [deskundige] biedt daartoe onvoldoende aanknopingspunten.

6.7.7
Wat overblijft is het betoog dat de kozijnen in strijd zijn met het bouwbesluit. De vraag is wat [appellant] met dit standpunt beoogt. Door het gebruik van neuten wordt, naar het hof uit de stellingen van partijen begrijpt, wel voldaan aan het bouwbesluit voor wat betreft de hoogte van de kozijnstijlen. Dat de kozijnen zonder gebruik van neuten te kort zijn, is alleen dan een tekortkoming door [geïntimeerde] als gebruik van neuten in de overeenkomst niet was toegestaan. Dat dit gebruik juist wel was toegestaan, lijkt echter te volgen uit de door [appellant] gegeven toestemming daarvoor.

6.7.8
Mocht [appellant] bedoelen dat hij op grond van een onjuiste voorstelling van zaken aangaande het gebruik van neuten heeft gedwaald (achteraf niet esthetisch), dan zou dit onder omstandigheden kunnen leiden tot vernietiging van de vordering. Een vordering in die zin ontbreekt echter. De incidentele grief slaagt, de vordering voor wat betreft de kozijnen zal alsnog worden afgewezen.

7 Slotsom
Alvorens verder te beslissen aangaande de grieven, zal het hof eerst een comparitie van partijen gelasten om hen de mogelijkheid te geven zich nader uit te laten aangaande hetgeen het hof heeft overwogen ten aanzien van schuren en het hutje (hiervoor onder 6.4.). Alle overige beslissingen worden aangehouden.



8. De beslissing
Het gerechtshof:
bepaalt dat partijen in persoon, samen met hun advocaten zullen verschijnen voor het hierbij tot raadsheer-commissaris benoemde lid van het hof mr. G. van Rijssen , die daartoe zitting zal houden in het paleis van justitie aan het Wilhelminaplein 1 te Leeuwarden op een nader door deze te bepalen dag en tijdstip, om inlichtingen te geven als onder 7 vermeld en opdat kan worden onderzocht of partijen het op een of meer punten met elkaar eens kunnen worden;
bepaalt dat partijen de verhinderdagen van partijen en hun advocaten in de maanden oktober tot en met december 2013 zullen opgeven op de roldatum van dinsdag 24 september 2013 , waarna dag en uur van de comparitie (ook indien voormelde opgave van een of meer van partijen ontbreekt) door de raadsheer-commissaris zullen worden vastgesteld;
bepaalt dat indien een partij ter comparitie nog een proceshandeling wenst te verrichten en/of producties in het geding wil brengen, zij ervoor dient te zorgen dat aan het hof en de wederpartij schriftelijk wordt meegedeeld wat de inhoud is van de ter comparitie te verrichten proceshandeling (voorzien van stukken) en indien een partij ter comparitie nog producties in het geding wenst te brengen dat zij daarvan goed leesbare afschriften aan het hof en de wederpartij dient over te leggen, in beide gevallen uiterlijk veertien dagen voorafgaand aan de zitting;
verstaat dat de advocaat van [appellant] uiterlijk twee weken voor de verschijning zal plaatsvinden een kopie van het volledige procesdossier ter griffie van het hof doet bezorgen, bij gebreke waarvan de advocaat van [geïntimeerde] alsnog de gelegenheid heeft uiterlijk één week voor de vastgestelde datum een kopie van de processtukken over te leggen.
Dit arrest is gewezen door mr. M.W. Zandbergen, mr. G. van Rijssen en mr. B.J.H. Hofstee en is door de rolraadsheer in tegenwoordigheid van de griffier in het openbaar uitgesproken op dinsdag 27 augustus 2013.

""".decode(errors="ignore")

#print model.decision_function(parseText(text))
print model.predict(parseText(text))