#!/usr/bin/python
# -*- coding: latin-1 -*-
import codecs
import sys
import os
import pickle
import cgi #Fuer die HTML Entities

"""Umgang mit Dateien"""

#-------------------------------------------------------

def textEinlesen(pfad,dateiname):
	"""	Umgang mit Datein
		text aus Datei Lesen ( UTF 8 codiert)"""
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
	"""	Daten aus einer pickle Datei lesen"""
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
	"""text in Datei schreiben"""
	dateiname = dateiname.partition(".")[0] + ending
	datei = pfad+"/"+dateiname
	try:
		out_file = codecs.open(datei, mode="w",encoding='utf-8')
		out_file.write(Text)
		out_file.close()
	except IOError:
		print("UUUuuups. Datei gibt es nicht in diesem Ordner."+ str(IOError))


def saveHTML(htmlText, pfad, dateiname):
	save(htmlText, pfad, dateiname,".html")


def saveTTL(htmlText, pfad, dateiname):
	"""Save als .ttl"""
	save(htmlText, pfad, dateiname,".ttl")

	
def saveCurDict(curDict, pfad, dateiname):
	"""Daten in eine Datei schreiben (mit pickle)"""
	dateiname = dateiname.partition(".")[0] + ".pickle"
	datei = pfad+"/"+dateiname
	try:
		out_file = open(datei, mode="w")
		pickle.dump(curDict, out_file)
		out_file.close()
	except IOError:
		print("UUUuuups. Datei gibt es nicht in diesem Ordner."+ str(IOError))


def printWhatItIs(structure, level=0):
	"""Printfunktion fuer verschachtelte Dictionarys"""
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
			text += print_what_it_is(structure[entry], level+1)
		level -= 1
		text += u'}'
	else:
		print("ARRG: Type nicht erkannt: " + str(type(structure)))
	text += u'\n'
	return text