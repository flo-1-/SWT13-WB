#!/usr/bin/python
# coding: utf8

from urllib import urlopen

import codecs
import os
import re
import pickle
import cgi #Fuer die HTML Entities

def openPickle(path, fileName):
	"""
	Reads data from a pickle file.
	@param path: path to open from
	@param fileName: file to open
	@type path: String
	@type fileName: String
	@return pickleData: Data from pickle file
	"""
	pickleFile = path + "/" + fileName
	
	newPickle = dict()
	
	try:
		in_file = codecs.open(pickleFile)
		data = in_file.read()
		in_file.close()
		
		pickleData = pickle.loads(data)	
	except IOError:
		print("File not found.")

	return pickleData

def saveCurDict(curDict, path, fileName):
	"""
	Saves a dictionary as apickle file 
	@param curDict: dict to save
	@param path: saving path
	@param fileName: filename
	@type curDict: Dictionary
	@type path: String
	@type fileName: String
	"""
	fileName = fileName.partition(".")[0] + ".pickle"
	
	if (not (os.path.isdir(path))):
			os.mkdir("/" + path)
			
	pickleFile = path + "/" + fileName
	
	try:
		out_file = open(pickleFile, mode="w")
		pickle.dump(curDict, out_file)
		out_file.close()
	except IOError:
		print("File not Found. " + str(IOError))
		
def saveImage(url):
	'''
	Downloads the portraits and saves them to the path ./portraits.
	@param url the url where the portrait is located
	'''
	try:
		data = (urlopen(url)).read()
	except:
		print("Error opening image url.")
	
	fileName = (url.split('/')).pop()
	
	if (not (os.path.isdir(os.getcwd() + "/portraits"))):
		os.mkdir(os.getcwd() + "/portraits")
	
	try:
		savefile = open(os.getcwd() + "/portraits/" + fileName, 'wb')
		savefile.write(data)
		savefile.close()
	except IOError:
		print("Error creating file. " + str(IOError))

def convertHTMLChars(text):
	"""
	Converts an text with htmlEntities to utf-8
	@param text text to convert
	@return an utf 8 String
	@exception raises Exception, if an HTMLEntity is not converted because its
	not in the EntityList, you have to append it manual.
	"""
	text = text.decode('unicode-escape') # Umwandlung von string in unicode
	pattern = '&#\d{2,4};' #Patten fuer Re \d sind nur Zahlen {2,4} Anzahl der Zahlen (2 bis 4)
	
	while re.search(pattern,text):
		nextHTMLEntity = re.search(pattern,text).group()
		nextHTMLEntityInt = int(nextHTMLEntity[2:-1])
		letterUnicode = unichr(nextHTMLEntityInt)
		text = unicode(text.replace(nextHTMLEntity, letterUnicode))
	pattern = '&#\w*;' #\w sind Zeichen ohne Leerzeichen
	
	while re.search(pattern,text):
		nextHTMLEntity = re.search(pattern,text).group()
		nextHTMLEntityInt = int("0"+nextHTMLEntity[2:-1],0)
		letterUnicode = unichr(nextHTMLEntityInt)
		text = text.replace(nextHTMLEntity, letterUnicode)
		
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
