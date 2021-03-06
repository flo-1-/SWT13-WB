#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib	#to open URLs
import re	#regular expressions

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
	@param url: A URL to get the text from
	@type url: String
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
	@param feed: Text to parse
	@type feed: String
	@return parsed String
	"""
	parser = DrwHTMLParser()
	parser.feed(feed)
	
	return parser.myText

def deleteCSS(text):
	"""
	deletes the css classes of a html file
	@param text: Raw HTM file without the tags
	@type text: String
	@return cleaned text as a string
	"""
	zeilen = text.splitlines(True)					#split text into a list of lines
	startZeile = 1
	endZeile = -1
	
	for i in range(len(zeilen)):					#scan through all lines
		if ("personendatenbank.html" in zeilen[i]):		#if a line has a specific content
			endZeile = i+1					#take the next index as endpoint
			break
	
	for i in range(startZeile, endZeile):				#from the first line to the endpoint
		zeilen[i] = ""						#delete the lines
		
	for i in range(len(zeilen)):					#scan through all lines
		if zeilen[i].strip() == "":				#if lines have whitespaces or linebreaks
			zeilen[i] = ""					#delete these unnessessary lines
	
	text = "".join(zeilen[:])					#glue the splitted lines together
	
	return text

def getKat(zeilen, ergebnis, kat):
	"""
	returns a string with the content of the desired category
	@param zeilen: lines of a text
	@param ergebnis: content of category
	@param kat: short name for category
	@type zeilen: L{lines}
	@type ergebnis: String
	@type kat: String
	"""
	start = ende = -1
	n = o = 0
	
	for n in range(len(zeilen)):					#scan through all lines
		if (zeilen[n] == kat + "\n") and (ende == -1):		#if the desired short name is found
			start = n+1					#take the next line as starting point
		#if a starting point is found and another short name for a category is found or the end of the document is reached
		elif ((zeilen[n][1:] == "\n") or (zeilen[n][2:] == "\n") or (zeilen[n][3:] == "\n") or (n+1 == len(zeilen)) ) and (n > start) and (start != -1):
			if (n+1 == len(zeilen)):			#if end of document is reached
				ende = n+1				#take the last line as endpoint
				zeilen[n] = zeilen[n] + "X"		#add a character (because it will be deleted later)
				break
			else:						#if next category is found
				ende = n				#take that line as endpoint
				break
	if (start != -1) and (ende != -1):				#if start and endpoint are found
		for o in range(start, ende):				#add the lines between them to the result
			ergebnis += zeilen[o]
		ergebnis = ergebnis[:-1]				#delete the last character (linebreak if endpoint is ...
									#...a category or 'X' if endpoint is the end of the document)
		
	return ergebnis

def getMut(zeilen, ergebnis):
	"""
	see getKat(), but specified for Mutter
	@param zeilen: lines of a text
	@param ergebnis: content of category
	@type zeilen: L{lines}
	@type ergebnis: String
	"""
	start = ende = wlba = fund = -1
	n = o = p = 0
	ergebnis = ""
	
	for p in range(len(zeilen)):					#scan through all lines
		if (zeilen[p] == "M\n"):				#if category M is found
			fund += 1					#inrement counter
		#if categor WL, B or A is found and one category M was found before
		if ((zeilen[p] == "WL\n") or (zeilen[p] == "B\n") or (zeilen[p] == "A\n")) and (fund == 0):
			wlba = 1					#first category M is Mutter
		if (fund == 1):						#if two categories M are found
			wlba = 2					#Mutter and Mitglied are present
			break
	
	#only Mutter present or Mutter and Mitglied present
	if ((fund == 0) and (wlba == 1)) or (fund == 1):		#if one M is found before WL, B or A or two M were found
		for n in range(len(zeilen)):				#see doc for getKat(), it is the same from here
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
	"""
	see getKat(), but specified for Mitglied
	@param zeilen: lines of a text
	@param ergebnis: content of category
	@type zeilen: L{lines}
	@type ergebnis: String
	"""
	start = ende = wlba = fund = -1
	n = o = p = q = r = c = 0
	ergebnis = ""
	
	for p in range(len(zeilen)):					#see getMut() for this loop
		if (zeilen[p] == "M\n"):
			fund += 1
		elif ((zeilen[p] == "WL\n") or (zeilen[p] == "B\n") or (zeilen[p] == "A\n")) and (fund == -1):
			wlba = 0					#Mutter not present
		elif ((zeilen[p] == "WL\n") or (zeilen[p] == "B\n") or (zeilen[p] == "A\n")) and (fund == 0):
			wlba = 1					#Mutter present
		elif (fund == 1):
			break						#Mutter and Mitglied present

	#only Mitglied present
	if ((fund == 0) and (wlba == 0)):				#see getMut() for this condition
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
	elif (fund == 1):						#see getMut() for this condition
		for q in range(len(zeilen)):
			#c is a counter to skip the first M
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
	"""
	saves the contents of each category in a dictionary
	@param text: cleaned text without html text or css classes
	@param namenDict: dictionary to save the data in
	@type text: String
	@type namenDict: Dictionary
	"""
	zeilen = text.splitlines(True)					#split text into a list of lines
	kreuzZeile = -1							#line with a cross-shape character
	ID = zeilen[0][:-1].strip()					#take the first line without linebreak as ID
	nachName = zeilen[1][:(zeilen[1].find(","))].strip()		#take the second line before the comma as nachName
	vorName = zeilen[1][(zeilen[1].find(",")+1):].strip()		#take the second line after the comma as vorName
	#set the contents to empty string so the can be overwritten properly
	nameKyr = namensVar = geburtsDaten = sterbeDaten = beruf = vater = ehegatte = mutter = mitglied = ausbildung = lebensstationen = ""
	leistungen = werke = sekundLit = publikVerz = quellen = portraits = geschwister = nachkommen = ""
	
	#Kyrillischer Name
	for i in range(2,5):						#scan through lines 2, 3 and 4
		#if a line starts with a '*' or 'Namen'
		if (zeilen[i][:2].strip() == "*" or zeilen[i][:5].strip() == "Namen") or (zeilen[i][:5].strip() == "Name"):
			break
		else:
			if (zeilen[i][-1:] == "\n"):			#if the line ends with a linebreak
				nameKyr += zeilen[i][:-1]		#save nameKyr without it
			else:
				nameKyr += zeilen[i]			#save line in nameKyr
	
	#Namensvariationen
	for j in range(3,10):						#scan through lines 4 to 9
		#if line starts with 'Namen'
		if ((zeilen[j][:5].strip() == "Namen") or (zeilen[j][:5].strip() == "Name")):
			if (zeilen[j][-1:] == "\n"):			#if line ends with a linebreak
				namensVar += zeilen[j][19:-1].strip()	#save the text after string 'Namensvariatonen: ' without it
			else:
				namensVar += zeilen[j][19:].strip()	#save the text after string 'Namensvariationen: '
	
	#Geburtsdatum und Ort
	for k in range(3,10):						#scan through lines 4 to 9
		if ((zeilen[k][:2].strip() == "*")):			#if a line starts with a '*'
			geburtsDaten = zeilen[k][2:-1].strip()		#save that line without linebreaks
			break
	
	#Sterbedaten
	for l in range(20):						#scan through lines 1 to 19
		if ((zeilen[l][:2].strip() == u'†')):			#if a line starts with a cross-shaped character
			kreuzZeile = l					#save that linenumber in kreuzZeile
			sterbeDaten = zeilen[l][2:-1].strip()		#save the content of the line without linebreak and first character
			break
	
	#Beruf
	for m in range(kreuzZeile+1, 20):				#scan from the line after the cross to line 19
		if not (zeilen[m][1:] == "\n"):				#if a lines second character is not a linebreak
			beruf += zeilen[m][:-1]				#save that line as beruf
		else:
			break
	
	vater = getKat(zeilen, vater, "V")				#Vater
	ehegatte = getKat(zeilen, ehegatte, "E")			#Ehegatten
	ausbildung = getKat(zeilen, ausbildung, "A")			#Ausbildung
	lebensstationen = getKat(zeilen, lebensstationen, "B")		#Lebensstationen
	leistungen = getKat(zeilen, leistungen, "WL")			#Leistungen
	werke = getKat(zeilen, werke, "W")				#Werke
	sekundLit = getKat(zeilen, sekundLit, "SL")			#Sekundaerliteratur
	portraits = getKat(zeilen, portraits, "P")			#Portraits
	publikVerz = getKat(zeilen, publikVerz, "GPV")			#Publikationsverzeichnisse
	quellen = getKat(zeilen, quellen, "Q")				#Quellen
	geschwister = getKat(zeilen, geschwister, "G")			#Geschwister
	nachkommen = getKat(zeilen, nachkommen, "N")			#Nachkommen
	mutter = getMut(zeilen, mutter)					#Mutter
	mitglied = getMit(zeilen, mitglied)				#Mitgliedschaft

	#Dictionary fuellen
	namenDict["ID"] = ID
	namenDict["Name"] = {"Nachname": nachName, "Vorname": vorName}
	namenDict["Namen (kyrillisch)"] = nameKyr
	if namensVar != "":
		namenDict["Namensvariationen"] = namensVar
	if geburtsDaten != "":
		namenDict["Geburtsdaten"] = geburtsDaten
	if sterbeDaten != "":
		namenDict["Sterbedaten"] = sterbeDaten
	if beruf != "":
		namenDict["Berufe"] = beruf
	if vater != "":
		namenDict["V"] = vater
	if ehegatte != "":
		namenDict["E"] = ehegatte
	if (mutter != "") and not (mutter is None):
		namenDict["M"] = mutter
	if (mitglied != "") and not (mitglied is None):
		namenDict["MG"] = mitglied
	if ausbildung != "":
		namenDict["A"] = ausbildung
	if lebensstationen != "":
		namenDict["B"] = lebensstationen
	if leistungen != "":
		namenDict["WL"] = leistungen
	if werke != "":
		namenDict["W"] = werke
	if sekundLit != "":
		namenDict["SL"] = sekundLit
	if publikVerz != "":
		namenDict["GPV"] = publikVerz
	if portraits != "":
		namenDict["P"] = portraits
	if quellen != "":
		namenDict["Q"] = quellen
	if geschwister != "":
		namenDict["G"] = geschwister
	if nachkommen != "":
		namenDict["N"] = nachkommen

def main(argv):
	htmlList = loadHTMLList()							#loads the url list
	personenDict = {}								#dictionary for all persons
#	for i in range(5,6):								#loop for testing purposes
	for i in range(len(htmlList)):							#loop through the urls
		personenDict.clear()
		htmlText = getTextOfHTML(htmlList[i])					#get text of i-th htm file
		htmlText = convertHTMLChars(htmlText)					#convert speacial htm characters to unicode
		text = htmlList[i][26:31] + "\n"					#add the file number to the new text 
		text += parser(htmlText)						#delete certain htm tags
		text = deleteCSS(text)							#delete CSS code and some whitespaces
		save(text, os.getcwd()+"/Temp", "person_"+str(i),".txt")		#save the new text in a subfolder
		saveNamen(text, personenDict)						#save the content of each category in a dictionary "personenDict"
		saveCurDict(personenDict, os.getcwd()+"/Fertig", "person_"+str(i))	#save each dict to a pickle file
#		print printWhatItIs(personenDict)					#print the dictionary for testing purposes

if __name__ == "__main__":
	main(sys.argv[1:])
	