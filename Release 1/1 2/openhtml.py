#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import re

from HTMLParser import HTMLParser

from drwHelper import openPickle
from drwHelper import save
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

def saveNamen(text, namenDict):
	zeilen = text.splitlines(True)
	kreuzZeile = -1
	v_start = -1
	v_ende = -1
	m_start = -1
	m_ende = -1
	wl_b_a = -1
	mi_start = -1
	mi_ende = -1
	wl_b_a_2 = -1
	ID = zeilen[0][:-1].strip()
	nachName = zeilen[1][:(zeilen[1].find(","))].strip()
	vorName = zeilen[1][(zeilen[1].find(",")+1):].strip()
	nameKyr = ""
	namensVar = ""
	geburtsDaten = ""
	sterbeDaten = ""
	beruf = ""
	vater = ""
	ehegatte = ""
	mutter = ""
	mitglied = ""
	
	
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
			
			"""
			if "," in zeilen[k]:
				geburtsDatum += zeilen[k][2:(zeilen[k].find(","))].strip()
				geburtsOrt += zeilen[k][(zeilen[k].find(",")+1):-1].strip()
			elif "in" in zeilen[k]:
				if (not ("im" in zeilen[k][:zeilen[k].find("in")]) or ("auf" in zeilen[k][:zeilen[k].find("in")])):
					geburtsDatum += zeilen[k][2:(zeilen[k].find("in"))].strip()
					geburtsOrt += zeilen[k][(zeilen[k].find("in")+2):-1].strip()
				elif "im" in zeilen[k]:
					if (not ("in" in zeilen[k][:zeilen[k].find("im")]) or ("auf" in zeilen[k][:zeilen[k].find("im")])):
						geburtsDatum += zeilen[k][2:(zeilen[k].find("im"))].strip()
						geburtsOrt += zeilen[k][(zeilen[k].find("im")+2):-1].strip()
					elif "auf" in zeilen[k]:
						if (not ("in" in zeilen[k][:zeilen[k].find("auf")]) or ("im" in zeilen[k][:zeilen[k].find("auf")])):
							geburtsDatum += zeilen[k][2:(zeilen[k].find("auf"))].strip()
							geburtsOrt += zeilen[k][(zeilen[k].find("auf")+2):-1].strip()
			else:
				if "0" in zeilen[k] or "1" in zeilen[k]:
					geburtsDatum += zeilen[k][2:-1].strip()
				else:
					geburtsOrt += zeilen[k][2:-1].strip()
			"""
	
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
	
	#Vater
	for n in range(len(zeilen)):
		if zeilen[n] == "V\n":
			v_start = n+1
		if ((zeilen[n][1:] == "\n") or (zeilen[n][2:] == "\n") or (zeilen[n][3:] == "\n")) and (n > v_start):
			v_ende = n
			break
	for o in range(v_start, v_ende):
		vater += zeilen[o]
		
	vater = vater[:-1]
	
	#Ehegatte
	for p in range(len(zeilen)):
		if zeilen[p] == "E\n":
			v_start = p+1
		if ((zeilen[p][1:] == "\n") or (zeilen[p][2:] == "\n") or (zeilen[p][3:] == "\n")) and (p > v_start):
			v_ende = p
			break
	for q in range(v_start, v_ende):
		ehegatte += zeilen[q]
		
	ehegatte = ehegatte[:-1]
	
	"""
	#Mutter
	for r in range(len(zeilen)):
		if ((zeilen[r] == "WL\n") or (zeilen[r] == "B\n") or (zeilen[r] == "A\n")):
			wl_b_a = 1
		if (zeilen[r] == "M\n"):
			if (wl_b_a != 1):
				m_start = r+1
		if ((zeilen[r][1:] == "\n") or (zeilen[r][2:] == "\n") or (zeilen[r][3:] == "\n")) and (r > m_start) and (m_start != -1):
			m_ende = r
			break
	
	print str(m_start)
	print str(m_ende)
	
	if ((m_start != -1) and (m_ende != -1)):
		for t in range(m_start, m_ende):
			mutter += zeilen[t]
		mutter = mutter[:-1]
	
	#Mitgliedschaft
	for v in range(len(zeilen)):
		if ((zeilen[v] == "WL\n") or (zeilen[v] == "B\n") or (zeilen[v] == "A\n")):
			wl_b_a_2 = 1
		if (zeilen[v] == "M\n"):
			if (wl_b_a_2 == 1):
				mi_start = v+1
		if ((zeilen[v][1:] == "\n") or (zeilen[v][2:] == "\n") or (zeilen[v][3:] == "\n")) and (v > mi_start) and (mi_start != -1):
			mi_ende = v
			break
	
	if ((mi_start != -1) and (mi_ende != -1)):
		for w in range(mi_start, mi_ende):
			mitglied += zeilen[w]
		mitglied = mitglied[:-1]
	"""
	
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
	if mutter != "":
		namenDict["Mutter"] = mutter
	if mitglied != "":
		namenDict["Mitgliedschaft"] = mitglied
	

def main(argv):
	htmlList = loadHTMLList()						#loads the url list
	personenDict = {}							#dictionary for all persons
#	for i in range(4, 7):							#loop for testing purposes
	for i in range(len(htmlList)):						#loop through the urls
		htmlText = getTextOfHTML(htmlList[i])				#get text of i-th htm file
		htmlText = convertHTMLChars(htmlText)				#convert speacial htm characters to unicode
		text = htmlList[i][26:31] + "\n"				#add the file number to the new text 
		text += parser(htmlText)					#delete certain htm tags
		text = deleteCSS(text)						#delete CSS code and some whitespaces
		save(text, os.getcwd()+"/Temp", "person_"+str(i),".txt")	#save the new text in a subfolder
		saveNamen(text, personenDict)
		print printWhatItIs(personenDict)

if __name__ == "__main__":
	main(sys.argv[1:])
	