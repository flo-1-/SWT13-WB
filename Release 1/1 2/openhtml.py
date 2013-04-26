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


def main(argv):
	htmlList = loadHTMLList()						#loads the url list	
#	for i in range(2):							#loop for testing purposes
	for i in range(len(htmlList)):						#loop through the urls
		htmlText = getTextOfHTML(htmlList[i])				#get text of i-th htm file
		htmlText = convertHTMLChars(htmlText)				#convert speacial htm characters to unicode
		text = htmlList[i][26:31] + "\n"				#add the file number to the new text 
		text += parser(htmlText)					#delete certain htm tags
		text = deleteCSS(text)						#delete CSS code and some whitespaces
		save(text, os.getcwd()+"/Temp", "person_"+str(i),".txt")	#save the new text in a subfolder

if __name__ == "__main__":
	main(sys.argv[1:])
	