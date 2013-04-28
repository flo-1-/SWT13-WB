#!/usr/bin/python
# -*- coding: latin-1 -*-
import codecs
import sys
import os
import re
import pickle
import cgi #Fuer die HTML Entities


"""Umgang mit Dateien"""

#-------------------------------------------------------

def textEinlesen(pfad,dateiname):
	"""
	read text from file (UTF 8 coded)
	@param pfad: path to read from
	@param dateiname: file to read
	@type pfad: String
	@type dateiname: String
	"""
	datei = pfad+"/"+dateiname
	text = "Fehler"
	try:
		in_file = codecs.open(datei,encoding='utf-8')
		text = in_file.read()
		in_file.close()
	except IOError:
		print("UUUuuups. Datei gibt es nicht in diesem Ordner.")
	
	return text


def openPickle(pfad, dateiname):
	"""
	read data from pickle file
	@param pfad: path to open from
	@param dateiname: file to open
	@type pfad: String
	@type dateiname: String
	"""
	datei = pfad+"/"+dateiname
#	print(datei)
	newPickle = dict()
	try:
		in_file = codecs.open(datei)
		text = in_file.read()
#		print(text)
		newPickle = pickle.loads(text)
		in_file.close()
	except IOError:
		print("UUUuuups. Datei gibt es nicht in diesem Ordner.")

	return newPickle


def save(Text, pfad, dateiname, ending):
	"""
	save file
	@param pfad: saving path
	@param dateiname: file to save
	@param Text: content to save
	@param ending: file format
	@type pfad: String
	@type dateiname: String
	@param Text: String
	@param ending: String
	"""
	dateiname = dateiname.partition(".")[0] + ending
	datei = pfad+"/"+dateiname
	try:
		out_file = codecs.open(datei, mode="w",encoding='utf-8')
		out_file.write(Text)
		out_file.close()
	except IOError:
		print("UUUuuups. Datei gibt es nicht in diesem Ordner."+ str(IOError))


def saveHTML(htmlText, pfad, dateiname):
	"""
	save as html
	@param htmlText: htm to save
	@param pfad: saving path
	@param dateiname: filename
	@type htmlText: String
	@type pfad: String
	@type dateiname: String
	"""
	save(htmlText, pfad, dateiname,".html")


def saveTTL(htmlText, pfad, dateiname):
	"""
	save as turtle
	@param htmlText: htm to save
	@param pfad: saving path
	@param dateiname: filename
	@type htmlText: String
	@type pfad: String
	@type dateiname: String
	"""
	save(htmlText, pfad, dateiname,".ttl")

	
def saveCurDict(curDict, pfad, dateiname):
	"""
	save dict as pickle
	@param curDict: dict to save
	@param pfad: saving path
	@param dateiname: filename
	@type curDict: Dictionary
	@type pfad: String
	@type dateiname: String
	"""
	dateiname = dateiname.partition(".")[0] + ".pickle"
	datei = pfad+"/"+dateiname
	try:
		out_file = open(datei, mode="w")
		pickle.dump(curDict, out_file)
		out_file.close()
	except IOError:
		print("UUUuuups. Datei gibt es nicht in diesem Ordner."+ str(IOError))


def printWhatItIs(structure, level=0):
	"""
	print dictionaries for testing
	@param structure: data structure
	@param level: depth of structure to print
	@type structure: Dictionary
	@type level: Integer
	"""
	def levelTabPrint(text):
		for step in range(level):
			text += u' '
		return text
	text = u''
	if isinstance(structure,type(u'')) or isinstance(structure,type("")):
		text = levelTabPrint(text)
		text += structure
	elif isinstance(structure,type({})):
		text += u'{\n'
		level += 1
		for entry in structure:
			text = levelTabPrint(text)
			text += "'" + str(entry) + "'" + ': \n'
			text += printWhatItIs(structure[entry], level+1)
		level -= 1
		text += u'}'
	else:
		print("ARRG: Type nicht erkannt: " + str(type(structure)))
	text += u'\n'
	return text


#Schrift konvertieren

def convertHTMLChars(text):
	"""
	Converts an text with htmlEntities to utf-8
	@return an utf 8 String
	@exception raises Exception, if an HTMLEntity is not converted because
	its not in the EntityList 
	You have to append it manual, please.
	"""
	text = text.decode('unicode-escape') # Umwandlung von string in unicode
	pattern = '&#\d{2,4};' #Patten fuer Re \d sind nur Zahlen {2,4} Anzahl der Zahlen (2 bis 4)
	while re.search(pattern,text):
		nextHTMLEntity = re.search(pattern,text).group()
		nextHTMLEntityInt = int(nextHTMLEntity[2:-1])
		letterUnicode = unichr(nextHTMLEntityInt)
#		print nextHTMLEntity
#		print letterUnicode
		text = unicode(text.replace(nextHTMLEntity, letterUnicode))
	pattern = '&#\w*;' #\w sind Zeichen ohne Leerzeichen
	while re.search(pattern,text):
		nextHTMLEntity = re.search(pattern,text).group()
#		print nextHTMLEntity
		nextHTMLEntityInt = int("0"+nextHTMLEntity[2:-1],0)
		letterUnicode = unichr(nextHTMLEntityInt)
		text = text.replace(nextHTMLEntity, letterUnicode)
	#EntityList
	text = text.replace(u'&auml;', u'\u00e4')
	text = text.replace(u'&Auml;', u'\u00c4')
	text = text.replace(u'&ouml;', u'\u00f6')
	text = text.replace(u'&Ouml;', u'\u00d6')
	text = text.replace(u'&uuml;', u'\u00fc')
	text = text.replace(u'&Uuml;', u'\u00dc')
	text = text.replace(u'&szlig;', u'\u00df')	
	text = text.replace(u'&nbsp;', u'\u00a0')	
	text = text.replace(u'&bull;', unichr(8226))
	text = text.replace(u'&Oslash;', u'\u00D8')
	text = text.replace(u'&otilde;', u'\u00F5')
	text = text.replace(u'&Euml;', u'\u00CB')
	text = text.replace(u'&eacute;', u'\u00E9')
	text = text.replace(u'&ccedil;', u'\u00E7')
	text = text.replace(u'&oacute;', u'\u00F3')
	text = text.replace(u'&agrave;', u'\u00E0')
	text = text.replace(u'&aacute;', u'\u00E9')
	text = text.replace(u'&iuml;', u'\u00EF')
	text = text.replace(u'&rsquo;', u'\u2019')
	text = text.replace(u'&euml;', u'\u00EB')
	text = text.replace(u'&acirc;', u'\u00E2')
	text = text.replace(u'&icirc;', u'\u00EE')
	text = text.replace(u'&ocirc;', u'\u00F4')
	pattern = '&\w*;'
	if re.search(pattern,text):
		errText =  "Achtung. Hier ist eine htmlEntity, die noch nicht konvertiert wurde: "
		errText += re.search(pattern,text).group()
		raise Exception(errText)
	
	return text

def main(argv):
	pass
		

if __name__ == "__main__":
	main(sys.argv[1:])
	