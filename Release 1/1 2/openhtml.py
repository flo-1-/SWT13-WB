#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Vorgehen
	* hmtlListe importieren
	* Oeffenen einer html 
	* Oeffenen aller html @TODO noch nicht gemacht. For-schleife
	* Einfacher Parser
	* speichern als textdatei mitbeliebiger Endung

"""

import os
import sys
import urllib
import re #Regulaere Ausdruecke

from HTMLParser import HTMLParser

from drwHelper import openPickle
from drwHelper import save
from drwHelper import convertHTMLChars
from drwHelper import testParser



def loadHTMLList():
	"""
	@return a list [] of all html urls
	"""
	htmlList = openPickle(os.getcwd(), "listOfAllHTMLSites.pickle")
#	for url in htmlList:
#		print url
	
	return htmlList


def getTextOfHTML(url):
	"""opens an url and returns as a string
	
	@return The Content of the URL as a string
	
	"""
	oneHTML = urllib.urlopen(url)
	hTMLText = oneHTML.read()
#	print oneHTML.info()
	
	return hTMLText



# create a subclass and override the handler methods
class DrwHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.myText = u''
	def handle_starttag(self, tag, attrs):
#        print "Encountered a start tag:", tag
#        print "With attributes:", attrs
		pass
	def handle_endtag(self, tag):
#        print "Encountered an end tag :", tag
		pass
	def handle_data(self, data):
#        print "Encountered some data  :", data
		if data.strip() != "":
#			print (data.strip())
			self.myText += data.strip()+"\n"
#		else:
#			print "\nZZZ",data.strip(), "ZZZ"



def parser(feed):								#Parser instanziieren und HTM übergeben
	parser = DrwHTMLParser()
	parser.feed(feed)
	return parser.myText


def main(argv):
	htmlList = loadHTMLList()					#Laedt die Liste
	
#	for i in range(3):							#Testlauf mit den ersten urls
	for i in range(len(htmlList)):				#durchlaufe alle URLs
#		htmlText = getTextOfHTML(htmlList[i])	#oeffnet die i-te url aus der Liste
#		htmlText = convertHTMLChars(htmlText)	#nimmt die htmlEntities raus
#		text = parser(htmlText)					#Versuchs Parser
#		save(text, os.getcwd()+"/Temp", "person_"+str(i),".txt")
		testParser(i)	


if __name__ == "__main__":
	main(sys.argv[1:])
	