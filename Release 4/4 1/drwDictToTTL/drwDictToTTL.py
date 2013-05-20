#!/usr/bin/python
# -*- coding: latin-1 -*-

import os
import sys
from drwHelper import saveTTL
from drwHelper import openPickle
from drwHelper import printWhatItIs


#Das ist der Kopf der zu erstellenden .ttl Datei
ttlHeader = """
@base <http://drw-catalog.saw-leipzig.de/> .
@prefix drw-model: <http://drw-model.saw-leipzig.de/> .
@prefix drw-catalog: <http://drw-catalog.saw-leipzig.de/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<> a owl:Ontology ;
   rdfs:label "DRW-Katalog" ;
   owl:imports <http://drw-model.saw-leipzig.de/> .

"""
def main(argv):
	""" Oeffnet die pickle Datei, fuerhrt die Umwandlung durch, speichert das
	Ergebnis"""
	dictList = openPickle(os.getcwd(),"personDict.pickle")	
#	print print_what_it_is(dictList)
	ttltext = createTTL(dictList)
	saveTTL(ttltext, os.getcwd(), "ttlExportOverview")



def createTTL(dicts):
	"""	Geht das Dictionary, dass aus der .pickle Datei geladen wurde, durch,
	erstellt neue Eintraege fuer Ressourcennamen und erstellt dann einen ttl 
	Text
	@param dictionary aller Personen mit den Dazugehoerigen Daten
	@return ttl als text
	"""
	ttl = ttlHeader
	for eachDict in dicts:
#		print dicts[eachDict]
		ttlDict = prepPersonDict(dicts[eachDict])
		print dicts[eachDict]["nameRes"]
#	print printWhatItIs(dicts)
		ttl += prepTTLForPerson(ttlDict)
	
	return ttl

def prepPersonDict(personDict):
	"""	Stellt einzelne Werte als neue Werte oder Bearbeitete Werte zusammen"""
	for entry in personDict:		
		personDict[entry] = personDict[entry].replace("<br>", " ")
		isErrorInText(personDict[entry]) 
#	Erstellt Namen, die als Ressourcen verwendet werden koennen
	personDict["sterbeortRes"] = cleanTextForResName(personDict["sterbeort"])
	personDict["sterbeortRes"] = delSpecialChar(personDict["sterbeortRes"])
	personDict["sterbejahrRes"] = cleanTextForResName(personDict["sterbejahr"])
	personDict["sterbejahrRes"] = delSpecialChar(personDict["sterbejahrRes"])
	personDict["geburtsortRes"] = cleanTextForResName(personDict["geburtsort"])
	personDict["geburtsortRes"] = delSpecialChar(personDict["geburtsortRes"])
	personDict["geburtsjahrRes"] = cleanTextForResName(personDict["geburtsjahr"])
	personDict["geburtsjahrRes"] = delSpecialChar(personDict["geburtsjahrRes"]) 
	nameConcat = personDict["name"] + "_" + personDict["vornamen"]
	personDict["nameRes"] = cleanTextForResName(nameConcat)
	personDict["nameRes"] = delSpecialChar(personDict["nameRes"])
#	print (personDict["nameRes"])
	
	return personDict


def prepTTLForPerson(personDict):
	"""	Erstellt aus einem preparierten Dict ein .ttl Text Fragment"""
	ttlText = ""
	if personDict["sterbeortRes"] != "":
		ttlText += """
<Place/%(sterbeortRes)s> 
		a drw-model:place;
		drw-model:deathPlaceOf <Person/%(nameRes)s> ;
		rdfs:label "%(sterbeort)s" .
		"""%personDict
	if personDict["sterbejahrRes"] != "":
		ttlText += """
<Year/%(sterbejahrRes)s> 
		a drw-model:year;
		drw-model:yearOfDeathOf <Person/%(nameRes)s> ;
		rdfs:label "%(sterbejahr)s" .
		"""%personDict
	if personDict["geburtsortRes"] != "":
		ttlText += """
<Place/%(geburtsortRes)s> 
		a drw-model:place;
		drw-model:birthPlaceOf <Person/%(nameRes)s> ; 
		rdfs:label "%(geburtsort)s" .
		"""%personDict
	if personDict["geburtsjahrRes"] != "":
		ttlText += """
<Year/%(geburtsjahrRes)s> 
		a drw-model:year;
		drw-model:yearOfBirthOf <Person/%(nameRes)s> ;
		rdfs:label "%(geburtsjahr)s" .
		"""%personDict
	ttlText += """
<Person/%(nameRes)s> 
	a drw-model:person ;
    drw-model:labor "%(beruf)s" ;
    drw-model:lastName "%(name)s";
	drw-model:firstName "%(vornamen)s" ;
	rdfs:label "%(name)s, %(vornamen)s" ;"""%personDict
	if personDict["sterbejahrRes"] != "":
		ttlText += u'\n\tdrw-model:yearOfDeathIs drw-catalog:Year/'
		ttlText += personDict["sterbejahrRes"] + ' ;'
	if personDict["sterbeortRes"] != "":
		ttlText += u'\n\tdrw-model:deathPlaceIs drw-catalog:Place/'
		ttlText += personDict["sterbeortRes"] +u' ;'
	if personDict["geburtsjahrRes"] != "":
		ttlText += u'\n\tdrw-model:yearOfBirthIs drw-catalog:Year/'
		ttlText += personDict["geburtsjahrRes"] + u' ;'
	if personDict["geburtsortRes"] != "":
		ttlText += u'\n\tdrw-model:birthPlaceIs drw-catalog:Place/'
		ttlText += personDict["geburtsortRes"] + ' ;'
	ttlText = ttlText[:-1]
	ttlText += u'.'

	return ttlText


def isErrorInText(text):
	""" checkt einen string auf Fehler (Es steckt noch ein <
	oder ein > drin. Das kann passieren, wenn die eingelesene html Fehlerhaft 
	war.
	Wenn ein Fehler enthalten ist wirft die MEthode eine Exception"""
	errorList = [u'<', u'>','*',u'\u2020 ']
	for error in errorList:
		if error in text:
			errortext = u'Das darf nicht enthalten sein: "' + error + '"\n'
			errortext +=  text
			raise Exception(errortext)

	return text


def cleanTextForResName(text):
	""" Sorgt dafuer, dass ein Text als Ressourcenname verwendet werden kann"""
	forbiddenTokens = ".,:;()'!" #sollen geloescht werden
	for token in forbiddenTokens:
		text = text.replace(token, "")
	text = text.strip()
	text = text.replace(" ", "_")
	
	return text


def deleteHTMLCode(text):
	""" Loescht "<br>" aus dem Text. Kann noch aus dem dict stammen."""
	text = text.replace("<br>", " ")

def printDict(dictToPrint):
	"""	Printfunktion fuer das Dict (Zum anschauen)"""
	printText = u''
	if isinstance(dictToPrint, type({})):
		for entry in dictToPrint:
			printText += entry + "\n" 
			printText += printDict(dictToPrint[entry]) + "\n"
	else:
		printText += dictToPrint
	return printText	

def delSpecialChar(unicodeString, htmlCode=True):
    """    Konvertiert einen unicode String in einen ASCII String mit HTML 
        Entitaeten
        Wenn htmlCode=False angegeben wird, dann werden auch <,>,\", & 
        uebertragen. Das funktioniert natuerlich nicht mit htmlCode.Der ist ja 
        dann nicht mehr lesbar"""
    if htmlCode == False:
        unicodeString = cgi.escape(unicodeString, quote=True)
    asciiString = unicodeString.encode('ascii', 'ignore')
    del(unicodeString)
    
    return asciiString
				

if __name__ == "__main__":
	main(sys.argv[1:])
