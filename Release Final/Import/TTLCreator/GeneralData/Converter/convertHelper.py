#!/usr/bin/python
# -*- coding: UTF-8 -*-
import codecs
import sys
import os
import pickle
import cgi #Fuer die HTML Entities

# Daten aus einer pickle Datei lesen
def openPickle(pfad, dateiname):
	"""
	opens .pickle formated files
	@param pfad: path of the file
	@param dateiname: name of the file which should be opened
	@return: data structure which was contained in .pickle file   
	"""
	datei = pfad+"/"+dateiname
	newPickle = dict()
#	print datei
	try:
		in_file = codecs.open(datei)
		text = in_file.read()
#		print(text)
		newPickle = pickle.loads(text)
		in_file.close()
	except IOError:
		print("The file you want to open does not exist.")
		print IOError
		
	return newPickle

def save(text, pfad, dateiname, ending):
	"""
	method to save text as file
	@param text: text to store
	@param pfad: path where the file should be stored
	@param ending:	ending of the file name e.g. ".txt"  
 
	"""
	dateiname = dateiname.partition(".")[0] + ending
	datei = pfad+"/"+dateiname
	try:
		out_file = codecs.open(datei, mode="w",encoding='utf-8')
		out_file.write(text)
		out_file.close()
	except IOError:
		print("Could not store file."+ str(IOError))



def print_what_it_is(structure, printContent=False, level=0 ):
	"""
	generic function to print structered Data with list(), str, unicode, dict(), 
	tuple() objects. 
	
	@param structure: The object you want to print
	@param printContent: Boolean indicates if the str and unicode objects should
	be displayed (True) or not (False). In this case "unicode" and "string" will
	be displayed instead.
	@param level: Do not use. Only for recursive function of this method.
	@return: str with json like structure of the object
	"""
	def levelTabPrint(text):
		for step in range(level):
			text += u' '
		return text
	text = u''
	if isinstance(structure,type(u'')):
		text = levelTabPrint(text)
		if printContent:
			text += structure
		else:
			text += "<unicode>"
#		print(structure)
	elif isinstance(structure,type("")):
		text = levelTabPrint(text)
		if printContent:
			text += structure
		else:
			text += "<string>"
#		print(structure)
	elif isinstance(structure,type([])):
		text = levelTabPrint(text)
		text += u'[\n' 
		for entry in structure:
			text += print_what_it_is(entry, printContent, level+1)
		text = levelTabPrint(text)
		text += u']'
	elif isinstance(structure,type(())):
#		for entry in structure:
		text = levelTabPrint(text)
		text += u'("' + unicode(structure[0]) + u'", <inhalt>)'
	elif isinstance(structure,type({})):
		text += u'{\n'
		level += 1
#		text = levelTabPrint(text)
		for entry in structure:
			text = levelTabPrint(text)
			text += "'" + unicode(entry) + "'" + ': \n'
			text += print_what_it_is(structure[entry], printContent, level+1)
		level -= 1
#		text = levelTabPrint(text)
		text += u'}'
	else:
		print("ARRG: Type nicht erkannt: " + str(type(structure)))
	text += u'\n'
	return text


def createASCIIString(text):
	"""
	Method to generate ASCII string out of unicode String.
	You can be shure that there are only ASCII letters, all unknown not ASCII
	letters will be deleted.
	@param text: text which should be returned as ASCII
	@return str with only ASCII letters inside. 
	"""
	def delSpecialChar(unicodeString, htmlCode=True):
		"""	
		Deletes all non Unicode Strings.
		@param unicodeString: unicode string
		@param htmlCode: If htmlCode=False " <,>,\", &" will be deleted
		@return str with only ascii inside 
		"""
		if htmlCode == False:
			unicodeString = cgi.escape(unicodeString, quote=True)
		asciiString = unicodeString.encode('ascii', 'ignore')
		del(unicodeString)
		return asciiString
	
	def cleanTextForResName(text):
		"""
		Replaces some forbidden signs: ".,:;()'! -"
		@param text: text which should be cleaned
		@return: str with cleaned text  
		"""
		forbiddenTokens = ["[","]",",",":",";","(",")","'","!","\u2018","\u2019"] #sollen geloescht werden
		for token in forbiddenTokens:
			text = text.replace(token, "")
		text = text.strip()
		text = text.replace(".", "_")
		text = text.replace(" ", "_")
		text = text.replace("-", "_")
		text = text.replace("/", "_or_")
		text = text.replace("\n", "_")
		text = text.replace("__", "_")
		text = text.replace("\u2019", "_")
		return text
	
	text = delSpecialChar(text, htmlCode=True)
	text = cleanTextForResName(text)
	if len(text) >30:
		text = text[:30]
	
	return text




def transLitGerRu(string):
	"""
	Transliterates string from german transliteration to kyrillic letters.
	@param string: unicode in german transliteration
	@return: unicode in kyrillic letters 
	"""
# Die Buchstaben ju und ch (Ch, Ju) und sind zu lang. Deswegen wird erst  ch durch h und Ju durch Û ersetzt (Das entspricht der offiziellen Transkription) - Das gleiche gilt fuer šč, Šč, ŠČ, das wird erst in ŝ bzw. Ŝ uebersetzt 
#ACHTUNG Vielleicht noch probleme beim Haertezeichen
	gerRu = {}
	gerRu.update({u"'":u"ь", u"’":u"ь", u"A":u"А", u"B":u"Б", u"C":u"Ц", u"D":u"Д", u"E":u"Е"})
	gerRu.update({u"F":u"Ф", u"G":u"Г", u"H":u"Х", u"I":u"И", u"J":u"Й", u"K":u"К", u"L":u"Л"})
	gerRu.update({u"M":u"М", u"N":u"Н", u"O":u"О", u"P":u"П", u"R":u"Р", u"S":u"С", u"T":u"Т"})
	gerRu.update({u"U":u"У", u"V":u"В", u"Y":u"Ы", u"Z":u"З", u"a":u"а", u"b":u"б", u"c":u"ц"})
	gerRu.update({u"d":u"д", u"e":u"е", u"f":u"ф", u"g":u"г", u"h":u"х", u"i":u"и", u"j":u"й"})
	gerRu.update({u"k":u"к", u"l":u"л", u"m":u"м", u"n":u"н", u"o":u"о", u"p":u"п", u"r":u"р"})
	gerRu.update({u"s":u"с", u"t":u"т", u"u":u"у", u"v":u"в", u"y":u"ы", u"z":u"з", u"Â":u"Я"})
	gerRu.update({u"Ė":u"Э", u"Û":u"Ю", u"â":u"я", u"ė":u"э", u"û":u"ю", u"Č":u"Ч", u"č":u"ч"})
	gerRu.update({u"Ŝ":u"Щ", u"ŝ":u"щ", u"Š":u"Ш", u"š":u"ш", u"Ž":u"Ж", u"ž":u"ж", u"ʺ":u"ъ"})
	gerRu.update({u"ё":u"ё", u"Ё":u"Ё"})
	string = string.replace(u'ju',u'û')
	string = string.replace(u'Ju',u'Û')
	string = string.replace(u'JU',u'Û')
	string = string.replace(u'ja',u'â')
	string = string.replace(u'Ja',u'Â')
	string = string.replace(u'JA',u'Â')
	string = string.replace(u'ch',u'h')
	string = string.replace(u'Ch',u'H')
	string = string.replace(u'CH',u'H')
	string = string.replace(u'šč',u'ŝ')
	string = string.replace(u'Šč',u'Ŝ')
	string = string.replace(u'ŠČ',u'Ŝ')
	convertedString = u''
	for letter in string:
		if letter in gerRu:
			#print('erkannt')
			convertedString += gerRu[letter]
		else:
			#print('nicht erkannt')
			convertedString += letter
			
	return convertedString


 
def getListOfPickles():
	"""
	Creates a List of Pickle File in a folder
	@return: a list of the stored .pickle filenames
	"""
	pfadZuPickles = os.getcwd() + "/pickleFromDRW"
	allFilesInPickleErgebnisse = os.listdir(pfadZuPickles)
	allPickleFilesInList = []
	for file in allFilesInPickleErgebnisse:
		if ".pickle" in file:
			allPickleFilesInList.append(file)
	#Nach Name Sortieren
	newFileList = []
	for file in allPickleFilesInList:
		person = openPickle(pfadZuPickles, file)
		name = unicode(person["Name"]["Nachname"])
		ident = unicode(person["ID"]) 
#		print(name + ": " + ident)
		newFileList.append((name,ident))
	newFileList.sort()
	for numberOfName in range(len(newFileList)):
		newFileList[numberOfName] = newFileList[numberOfName][1] + u'.pickle'
#		print(newFileList[numberOfName])
 	
	return newFileList

			
# #TODO Ist aehnlich in curVitxmlToDict und soll da auch eigentlich hin
# #	hier nur weil ich zu faul bin alle Dicts nachzuberarbeiten. kommt aber noch!
# def getYearOfDate(dateText):
# 	"""
# 		Sucht nach 4stelligen Jahreszahlen und stellt diese, wenn sie unter-
# 		schiedlich sind hintereinander dar.
# 		Nicht besonders sicher.
# 		TODO Nachschauen, was fuer spyialfaelle es gibt: so wie: 1867/68
# 		Das wird bisher noch nicht erfasst.
# 		TODO oder:"1845(?)"
# 	"""
# 	whereIntsAre = ""
# 	yearsInText = u''
# 	yearsList = []
# 	
# 	for letter in dateText:
# 		if letter.isdecimal():
# 			whereIntsAre += u'1'
# 		else:
# 			whereIntsAre += u'0'
# 	howManyYears = whereIntsAre.count(u'1111')
# 	for year in range(howManyYears):
# 		lastYearPlace = whereIntsAre.rfind(u'1111')
# 		newYear = dateText[lastYearPlace:lastYearPlace+4]
# 		if newYear not in yearsList:
# 			yearsList.append(newYear)
# 		whereIntsAre = whereIntsAre[:whereIntsAre.rfind(u'1111')]
# 	yearsList.sort()
# 	for year in range(len(yearsList)):
# 		if year != 0:
# 			yearsInText += u'/'
# 		yearsInText += yearsList[year]
# #	print(dateText)
# #	print(whereIntsAre)
# #	print(yearsInText)
# 
# 	return yearsInText




