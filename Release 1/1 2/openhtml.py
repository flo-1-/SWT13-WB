#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import re

from HTMLParser import HTMLParser

from drwHelper import openPickle
from drwHelper import save
from drwHelper import saveCurDict
from drwHelper import convertHTMLChars
from drwHelper import printWhatItIs

def loadHTMLList():
	"""
	@return a list[] of all html urls
	"""
	htmlList = openPickle(os.getcwd(), "listOfAllHTMLSites.pickle")
	
	return htmlList

def getTextOfHTML(url):
	"""
	opens an url and returns its content as a string
	@return The Content of the URL as a string
	"""
	oneHTML = urllib.urlopen(url)
	hTMLText = oneHTML.read()
	
	return hTMLText

# create a subclass and override the handler methods
class DrwHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.myText = u''
		self.currentTag = "" 
		self.currentAttrs = ""
	def handle_starttag(self, tag, attrs):
#        print "Encountered a start tag:", tag
#        print "With attributes:", attrs
		self.currentTag = tag
		self.currentAttrs = attrs
#		print attrs
	def handle_endtag(self, tag):
		self.currentTag = "x"		
	def handle_data(self, data):
#        print "Encountered some data  :", data
		if data.strip() != "":
			if self.currentTag == "b":
				self.myText += "<b>"
				self.myText += data
				self.myText += "</b>"	
			elif self.currentTag == "i":
				self.myText += "<i>"
				self.myText += data
				self.myText += "</i>"
			elif self.currentTag == "a":
				link = ""
				for attr in self.currentAttrs:
					if attr[0] == "href":
						link = attr[1]
						foundInternLink = re.search("\d{5}\.html", link)
						if foundInternLink:
							personNumber = re.search("\d{5}", link).group()				
							self.myText += "#internNameLink#" + personNumber + "#endNameNr#"
							self.myText += data + "#/internNameLink#"		
						else:
							self.myText += " " + link + " "
							self.myText = self.myText.replace("  "," ")
			elif self.currentTag == "x":
				self.myText += data
			else:
				self.myText += "\n" + data
		self.myText = self.myText.replace("\n\n","\n")

def parser(feed):
	"""
	@return parsed String
	"""
	parser = DrwHTMLParser()
	parser.feed(feed)
	
	return parser.myText

def deleteCSS(text):
	"""
	@return cleaned text as a string
	"""
	zeilen = text.splitlines(True)
	startZeile = 1
	endZeile = -1
	
	for i in range(len(zeilen)):
		if ("personendatenbank.html" in zeilen[i]):
			endZeile = i+1
			break
	
	for i in range(startZeile, endZeile):
		zeilen[i] = ""
		
	for i in range(len(zeilen)):
		if zeilen[i].strip() == "":
			zeilen[i] = ""
	
	text = "".join(zeilen[:])
	
	return text

def getKat(zeilen, ergebnis, kat):
	start = ende = -1
	n = o = 0
	
	for n in range(len(zeilen)):
		if (zeilen[n] == kat + "\n") and (ende == -1):
			start = n+1
		elif ((zeilen[n][1:] == "\n") or (zeilen[n][2:] == "\n") or (zeilen[n][3:] == "\n") or (n+1 == len(zeilen)) ) and (n > start) and (start != -1):
			ende = n
			break
	if (start != -1) and (ende != -1):
		for o in range(start, ende):
			ergebnis += zeilen[o]
		ergebnis = ergebnis[:-1]
		
	return ergebnis

def getMut(zeilen, ergebnis):
	start = ende = wlba = fund = -1
	n = o = p = 0
	ergebnis = ""
	
	for p in range(len(zeilen)):
		if (zeilen[p] == "M\n"):
			fund += 1	#M Counter
		if ((zeilen[p] == "WL\n") or (zeilen[p] == "B\n") or (zeilen[p] == "A\n")) and (fund == 0):
			wlba = 1	#Mutter present
		if (fund == 1):
			wlba = 2	#Mutter and Mitglied present
			break
	
	#only Mutter present or Mutter and Mitglied present
	if ((fund == 0) and (wlba == 1)) or (fund == 1):
		for n in range(len(zeilen)):
			if (zeilen[n] == "M\n") and (ende == -1):
				start = n+1
			elif ((zeilen[n][1:] == "\n") or (zeilen[n][2:] == "\n") or (zeilen[n][3:] == "\n") or (n+1 == len(zeilen)) ) and (n > start) and (start != -1):
				ende = n
				break
		if (start != -1) and (ende != -1):
			for o in range(start, ende):
				ergebnis += zeilen[o]
			ergebnis = ergebnis[:-1]
		
	return ergebnis

def getMit(zeilen, ergebnis):
	start = ende = wlba = fund = -1
	n = o = p = q = r = c = 0
	ergebnis = ""
	
	for p in range(len(zeilen)):
		if (zeilen[p] == "M\n"):
			fund += 1
		elif ((zeilen[p] == "WL\n") or (zeilen[p] == "B\n") or (zeilen[p] == "A\n")) and (fund == -1):
			wlba = 0	#Mutter not present
		elif ((zeilen[p] == "WL\n") or (zeilen[p] == "B\n") or (zeilen[p] == "A\n")) and (fund == 0):
			wlba = 1	#Mutter present
		elif (fund == 1):
			break		#Mutter and Mitglied present

	#only Mitglied present
	if ((fund == 0) and (wlba == 0)):
		for n in range(len(zeilen)):
			if (zeilen[n] == "M\n") and (ende == -1):
				start = n+1
			elif ((zeilen[n][1:] == "\n") or (zeilen[n][2:] == "\n") or (zeilen[n][3:] == "\n") or (n+1 == len(zeilen)) ) and (n > start) and (start != -1):
				ende = n
				break
		if (start != -1) and (ende != -1):
			for o in range(start, ende):
				ergebnis += zeilen[o]
			ergebnis = ergebnis[:-1]
			return ergebnis
	#Mutter and Mitglied present
	elif (fund == 1):
		for q in range(len(zeilen)):
			if (zeilen[q] == "M\n") and (ende == -1) and (c == 0):
				c = 1
			elif (zeilen[q] == "M\n") and (ende == -1) and (c != 0):
				start = q+1
			elif ((zeilen[q][1:] == "\n") or (zeilen[q][2:] == "\n") or (zeilen[q][3:] == "\n") or (q+1 == len(zeilen)) ) and (q > start) and (start != -1):
				ende = q
				break
		if (start != -1) and (ende != -1) and (c != 0):
			for r in range(start, ende):
				ergebnis += zeilen[r]
			ergebnis = ergebnis[:-1]
			return ergebnis

def saveNamen(text, namenDict):
	zeilen = text.splitlines(True)
	kreuzZeile = -1
	ID = zeilen[0][:-1].strip()
	nachName = zeilen[1][:(zeilen[1].find(","))].strip()
	vorName = zeilen[1][(zeilen[1].find(",")+1):].strip()
	nameKyr = namensVar = geburtsDaten = sterbeDaten = beruf = vater = ehegatte = mutter = mitglied = ausbildung = lebensstationen = ""
	leistungen = werke = sekundLit = publikVerz = quellen = portraits = geschwister = nachkommen = ""
	
	#Kyrillischer Name
	for i in range(2,5):
		if (zeilen[i][:2].strip() == "*" or zeilen[i][:5].strip() == "Namen") or (zeilen[i][:5].strip() == "Name"):
			break
		else:
			if (zeilen[i][-1:] == "\n"):
				nameKyr += zeilen[i][:-1]
			else:
				nameKyr += zeilen[i]
	
	#Namensvariationen
	for j in range(3,10):
		if ((zeilen[j][:5].strip() == "Namen") or (zeilen[j][:5].strip() == "Name")):
			if (zeilen[j][-1:] == "\n"):
				namensVar += zeilen[j][19:-1].strip()
			else:
				namensVar += zeilen[j][19:].strip()
	
	#Geburtsdatum und Ort
	for k in range(3,10):
		if ((zeilen[k][:2].strip() == "*")):
			geburtsDaten = zeilen[k][2:-1].strip()
			break
	
	#Sterbedaten
	for l in range(20):
		if ((zeilen[l][:2].strip() == u'†')):
			kreuzZeile = l
			sterbeDaten = zeilen[l][2:-1].strip()
			break
	
	#Beruf
	for m in range(kreuzZeile+1, 20):
		if not (zeilen[m][1:] == "\n"):
			beruf += zeilen[m][:-1]
		else:
			break
	
	vater = getKat(zeilen, vater, "V")			#Vater
	ehegatte = getKat(zeilen, ehegatte, "E")		#Ehegatten
	ausbildung = getKat(zeilen, ausbildung, "A")		#Ausbildung
	lebensstationen = getKat(zeilen, lebensstationen, "B")	#Lebensstationen
	leistungen = getKat(zeilen, leistungen, "WL")		#Leistungen
	werke = getKat(zeilen, werke, "W")			#Werke
	sekundLit = getKat(zeilen, sekundLit, "SL")		#Sekundaerliteratur
	portraits = getKat(zeilen, portraits, "P")		#Portraits
	publikVerz = getKat(zeilen, publikVerz, "GPV")		#Publikationsverzeichnisse
	quellen = getKat(zeilen, quellen, "Q")			#Quellen
	geschwister = getKat(zeilen, geschwister, "G")		#Geschwister
	nachkommen = getKat(zeilen, nachkommen, "N")		#Nachkommen
	mutter = getMut(zeilen, mutter)				#Mutter
	mitglied = getMit(zeilen, mitglied)			#Mitgliedschaft
	
	#Dictionary fuellen
	namenDict["ID"] = ID
	namenDict["Name"] = {"Nachname": nachName, "Vorname": vorName}
	namenDict["Kyrillische Namen"] = nameKyr
	if namensVar != "":
		namenDict["Namensvariationen"] = namensVar
	if geburtsDaten != "":
		namenDict["Geburtsdaten"] = geburtsDaten
	if sterbeDaten != "":
		namenDict["Sterbedaten"] = sterbeDaten
	if beruf != "":
		namenDict["Beruf"] = beruf
	if vater != "":
		namenDict["Vater"] = vater
	if ehegatte != "":
		namenDict["Ehegatten"] = ehegatte
	if (mutter != "") and not (mutter is None):
		namenDict["Mutter"] = mutter
	if (mitglied != "") and not (mitglied is None):
		namenDict["Mitgliedschaft"] = mitglied
	if ausbildung != "":
		namenDict["Ausbildung"] = ausbildung
	if lebensstationen != "":
		namenDict["Lebensstationen"] = lebensstationen
	if leistungen != "":
		namenDict["Leistungen"] = leistungen
	if werke != "":
		namenDict["Werke"] = werke
	if sekundLit != "":
		namenDict["Sekundaerliteratur"] = sekundLit
	if publikVerz != "":
		namenDict["Publikationsverzeichnisse"] = publikVerz
	if portraits != "":
		namenDict["Portraits"] = portraits
	if quellen != "":
		namenDict["Quellen"] = quellen
	if geschwister != "":
		namenDict["Geschwister"] = geschwister
	if nachkommen != "":
		namenDict["Nachkommen"] = nachkommen

def main(argv):
	htmlList = loadHTMLList()						#loads the url list
	personenDict = {}							#dictionary for all persons
#	for i in range(5,6):							#loop for testing purposes
	for i in range(len(htmlList)):						#loop through the urls
		personenDict.clear()
		htmlText = getTextOfHTML(htmlList[i])				#get text of i-th htm file
		htmlText = convertHTMLChars(htmlText)				#convert speacial htm characters to unicode
		text = htmlList[i][26:31] + "\n"				#add the file number to the new text 
		text += parser(htmlText)					#delete certain htm tags
		text = deleteCSS(text)						#delete CSS code and some whitespaces
		save(text, os.getcwd()+"/Temp", "person_"+str(i),".txt")	#save the new text in a subfolder
		saveNamen(text, personenDict)					#save the content of each category in a dictionary "personenDict"
		saveCurDict(personenDict, os.getcwd()+"/Fertig", "person_"+str(i))
#		print printWhatItIs(personenDict)				#print the dictionary for testing purposes

if __name__ == "__main__":
	main(sys.argv[1:])
	