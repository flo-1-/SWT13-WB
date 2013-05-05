#!/usr/bin/python
# coding: utf8

from dictHelper import convertHTMLChars #convert html code into unicode
from dictHelper import saveCurDict #save Dictionary as .pickle
from dictHelper import openPickle #open pickle file
from HTMLParser import HTMLParser #parse html
from urllib import urlopen #open url
from pprint import pprint #for testing

import os #path operations
import re #for split

class PersonDataParser(HTMLParser):
	'''
	Parser for parsing all necessary information from the html pages to build the
	data for the database.
	'''
	def __init__(self):
		'''
		Constructor, sets a list of all Paragraphs an some helper variables
		'''
		HTMLParser.__init__(self)
		self.paragraphs = ['V', 'M', 'E', 'A', 'B', 'WL', 'W', 'SL', 'P', 'GPV', 'Q']
		self.foundParagraphs = []
		self.t100gFound = False
		self.t100sFound = False
		self.t100nFound = False
		self.h3EndFound = False
		self.nameLinkFound = False
		self.isParagraph = False
		self.getData = False
		self.text = ''
		
	def handle_starttag(self, tag, attrs):
		'''
		Handles the starttags, causes actions, if specific starttags were found.
		Can start the collection of data.
		'''
		if (tag == 'td' and self.isParagraph == True):
			self.getData = True
			self.isParagraph = False
			
		if (tag == 'td'):
			for attr, value in attrs:
				if (attr == 'class'):
					if (value == 't5s'):
						self.isParagraph = True
					if (value == 't100g'):
						self.t100gFound = True
					if (value == 't100s'):
						self.t100sFound = True
						self.getData = True
						self.text += '.:._.:.Name russisch.:._.:.'
						self.foundParagraphs.append('Name russisch')
					if (value == 't100n'):
						self.t100nFound = True
		
		if (tag == 'h3' and self.t100gFound == True):
			self.text += '.:._.:.Name.:._.:.'
			self.foundParagraphs.append('Name')
			self.getData = True
		
		if (self.t100gFound == True and self.h3EndFound == True):
			self.foundParagraphs.append('Quelle')
			self.text += '.:._.:.Quelle.:._.:.'
			self.getData = True
		
		if (tag == 'img'):
			for name, value in attrs:
				if (name == 'src'):
					try:
						testValue = int(value[0]) #exclude pfeil.jpg
						self.text += '.:._.:.Portrait.:._.:.http://drw.saw-leipzig.de/' + value
						self.foundParagraphs.append('Portrait')
					except:
						pass
						
				if (name == 'title' and value != u'zurück'):
					self.text += '.:._.:.Portraittext.:._.:.' + value
					self.foundParagraphs.append('Portraittext')
		
		if (tag == 'a'):
			for attr, value in attrs:
				if (attr == 'href'):
					if(not('personendatenbank' in value)):
						if (re.match("\d{5}\.html", value)):
							self.text += '#internNameLink#' + value.replace('.html', '') + '#EndNameNr#'
							self.nameLinkFound = True
						else:
							self.text += value + ' '
							
						self.getData = True
						
		if (self.getData == True and self.isParagraph == False):
			if (tag == 'i'):
				self.text += '<i>'
				
			if (tag == 'b'):
				self.text += '<b>'
	
	def handle_data(self, data):
		'''
		Handles the data, causes actions, if specific data were found or adds data
		to the datacollection.
		'''
		if (self.getData == True and self.isParagraph == False):
			self.text += data
		
		if (self.getData == False and self.isParagraph == True):
			if (data == 'M' and ('M' in self.foundParagraphs or ('A' in self.foundParagraphs or 'B' in self.foundParagraphs))):
						self.foundParagraphs.append('MG')
						self.text += '.:._.:.MG.:._.:.'
						self.getData = True
			else:
				if (data in self.paragraphs):
					self.foundParagraphs.append(data)
					self.paragraph = data
					self.text += '.:._.:.' + data +'.:._.:.'
					self.getData = True
				else:
					self.isParagraph = False
		
		if (self.getData == False and self.t100nFound == True):
			if (data[0] == '*'):
				self.foundParagraphs.append('Geburtsdaten')
				self.text += '.:._.:.Geburtsdaten.:._.:.'
				self.text += data
				self.t100nFound = False
			else:
				if (data[0] == u'\u2020'):
					self.foundParagraphs.append('Sterbedaten')
					self.text += '.:._.:.Sterbedaten.:._.:.'
					self.text += data
					self.t100nFound = False
				else:
					if ('Namensvariationen' in data):
						self.foundParagraphs.append('Namensvariationen')
						self.text += '.:._.:.Namensvariationen.:._.:.'
						self.text += data.replace('Namensvariationen:', '').strip()
						self.t100nFound = False
					else:
						self.foundParagraphs.append('Berufe')
						self.text += '.:._.:.Berufe.:._.:.'
						self.text += data.strip()
						self.t100nFound = False
		
		if (self.getData == True and self.nameLinkFound == True):
			self.text += data

	def handle_endtag(self, tag):
		'''
		Handles the endtags, causes actions if specific endtags were found.
		Can stop the collection of data.
		'''
		if (tag == 'td' and self.isParagraph == False):
			self.getData = False
			self.t100gFound = False
			
		if (tag == 'h3' and self.getData == True):
			self.getData = False
			self.h3EndFound = True
		
		if (tag == 'td' and self.t100sFound == True):
			self.getData = False
			self.t100sFound = False
		
		if (tag == 'a' and self.nameLinkFound == True):
			self.text += '#/internNameLink#'
			self.getData = False
			self.nameLinkFound = False
		
		if (self.getData == True and self.isParagraph == False):
			if (tag == 'i'):
				self.text += '</i>'
				
			if (tag == 'b'):
				self.text += '</b>'

	def getText(self):
		'''
		Method that returns the collected data.
		@return self.text: collected data
		'''
		return self.text
		

class DataFormater():
	'''
	Formats the collected data and builds a Dictionary with that data.
	'''
	def __init__(self, text, dataID):
		'''
		Constructor, gets the data, the ID and creates an empty dictionary.
		@param text: collected data
		@param dataID: ID for the current data
		'''
		self.text = text.strip()
		self.personDict = {}
		self.dataID = dataID
	
	def makeDict(self):
		'''
		Builds the dictionary from the collected data, starts all Methods for
		formating each paragraph.
		'''
		textList = self.text.split('.:._.:.')
		if ('' in textList):
			textList.remove('')
		
		count = 0
		while (count < len(textList)):
			self.personDict.update({textList[count]: textList[count + 1]})
			count += 2
		
		self.addID()
		if ('Name' in self.personDict):
			self.formatName()
		if ('Geburtsdaten' in self.personDict):
			self.formatBorn()
		if ('Sterbedaten' in self.personDict):
			self.formatDeath()
		if ('Berufe' in self.personDict):
			self.formatProfessions()
		if ('Namensvariationen' in self.personDict):
			self.formatNameVariation()
		if ('Name russisch' in self.personDict):
			self.formatNameRus()
		if ('P' in self.personDict):
			self.formatParagraph('P')
		if ('Q' in self.personDict):
			self.formatParagraph('Q')
		if ('SL' in self.personDict):
			self.formatParagraph('SL')
		if ('W' in self.personDict):
			self.formatW()
	
	def addID(self):
		'''
		Adds the ID to the dictionary.
		'''
		idDict = {u'ID': self.dataID}
		
		self.personDict.update(idDict)
	
	def formatName(self):
		'''
		Formats and adds the Name to the dictionary.
		The shape is like:
		{'Name': {'Vorname': vorName, 'Nachname': nachName}
		'''
		name = self.personDict['Name'].split(',')
		name[1] = name[1].strip()
		
		if (' ' in name[0]):
			splittedName = re.split('( )', name[0])
		
			name[0] = ''
		
			for index, content in enumerate(splittedName):
				if (not (' ' in content)):
					splittedName[index] = splittedName[index][0] + splittedName[index][1:].lower()
					name[0] += splittedName[index]
				else:
					name[0] += splittedName[index]
				
			name[0] = name[0].strip()
		else:
			name[0] = name[0].title()
			
		
		nameDict = {'Name': {'Nachname': name[0]}}
		nameDict['Name']['Vorname'] = name[1]
		
		self.personDict.update(nameDict)
	
	def formatNameRus(self):
		'''
		Formats and adds the russian Name to the dictionary.
		The shape is like:
		{'Name russisch': {'name': name, 'countryCode': countryCode}
		
		countryCode can be 'de' or 'ru'
		'''
		nameRus = self.personDict['Name russisch'].split('/')
		nrDict = {'Name russisch': []}
		
		for index, content in enumerate(nameRus):
			if (re.search(u'[\u0400-\u04ff]', nameRus[index])):
				countryCode = 'ru'
			else:
				countryCode = 'de'
			
			nrDict['Name russisch'].append({'name': nameRus[index].strip(), 'countryCode': countryCode})
		
		self.personDict.update(nrDict)
	
	def formatNameVariation(self):
		'''
		Formats and adds the namevariations to the dictionary:
		The shape is like:
		{'Namensvariationen': {'name': name, 'countryCode': countryCode}
		
		countryCode can be 'de' or 'ru'
		'''
		nameVariation = self.personDict['Namensvariationen'].split(',')
		nvDict = {'Namensvariationen': []}
		
		for index, content in enumerate(nameVariation):
			if (re.search(u'[\u0400-\u04ff]', nameVariation[index])):
				countryCode = 'ru'
			else:
				countryCode = 'de'
			
			nvDict['Namensvariationen'].append({'name': nameVariation[index].strip(), 'countyCode': countryCode})
			
		self.personDict.update(nvDict)
		
	def formatBorn(self):
		'''
		Formats and adds the birthdates to the dictionary.
		The shape is like:
		{'Geburtsdaten': {'Geburtsdatum': datum, 'Geburtsort': geburtsort}
		'''
		born = self.personDict['Geburtsdaten']
		born = born.replace('*', '').strip().split(',')
		
		for index, content in enumerate(born):
			born[index] = born[index].strip()
		
		bornDict = {'Geburtsdaten': {'Geburtsdatum': born[0]}}
		if (len(born) == 2):
			bornDict['Geburtsdaten']['Geburtsort'] = born[1]
		if (len(born) > 2):
			for index, content in enumerate(born):
				if (index > 2):
					born[1] += ', ' + born[index]
			bornDict['Geburtsdaten']['Geburtsort'] = born[1]
		
		self.personDict.update(bornDict)
		
	def formatDeath(self):
		'''
		Formats and adds the deathdates to the dictionary.
		The form is like:
		{'Sterbedaten': {'Sterbedatum': datum, 'Sterbeort': ort, 'Grabstätte': grabstätte}
		'''
		death = self.personDict['Sterbedaten']
		deathDict = {'Sterbedaten': {}}
		
		if (u'Grabstätte:' in death):
			death = death.split(u'Grabstätte:')
			cemetery = death[1].strip()
			deathDict['Sterbedaten']['Grabstätte'] = cemetery
			death = death[0].split(',')
		else:
			death = death.split(',')
			
		dayOfDeath = death[0].replace(u'\u2020', '').strip()
		deathDict['Sterbedaten']['Sterbedatum'] = dayOfDeath
		if (len(death) == 2):
			placeOfDeath = death[1].strip()
			deathDict['Sterbedaten']['Sterbesort'] = placeOfDeath
		if (len(death) > 2):
			placeOfDeath = death[1].strip()
			for index, content in enumerate(death):
				if (index >= 2):
					death[1] += ', ' + death[index]
			deathDict['Sterbedaten']['Sterbesort'] = placeOfDeath
		
		self.personDict.update(deathDict)
		
	def formatProfessions(self):
		'''
		Formats and adds the professions to the dictionary.
		The form is like:
		{'Berufe': [beruf1, beruf2, beruf3]}
		'''
		professions = self.personDict['Berufe'].split(',')
		for index, data in enumerate(professions):
			professions[index] = professions[index].strip()
		
		proDict = {'Berufe': professions}
		
		self.personDict.update(proDict)
		
	def formatParagraph(self, paragraph):
		'''
		Formats paragraphs with dots at the beginning.
		Removes the dots and puts in a shape like:
		{'A': [line1, line 2, line3]}
		where 'A' can be replaced by the other paragraphs.
		@param paragraph: paragraph to format
		'''
		a = self.personDict[paragraph].replace(u'\u2022 ', '').split('\n')
		pDict = {paragraph: a}
		self.personDict.update(pDict)
	
	def formatW(self):
		'''
		Formats the 'W' paragraph. This paragraph can contain headlines and
		footnotes, which must be threated differently then the other paragraphs.
		It also removes the dots of line with those.
		It creates two dictionarys, wich look like:
		{'W': {'general': [line, line, line], headline: [line, line, line]}
		{footnodes: {1: footnote, 2: footnote}}
		'general' and 'footnote' are only present if they are in the data.
		'''
		dictKey = ''
		isHeadline = True
		general = []
		wDict = {'W': {}}
		footDict = {'footnotes': {}}
		w = self.personDict['W'].strip().split('\n')
		for index, content in enumerate(w):
			if ('' in w):
				w.remove('')
		
		count = 0
		for index, content in enumerate(w):
			if (not (w[index][0] == u'\u2022') and isHeadline == True):
				count = 0
				dictKey = content.strip()
				wDict['W'][dictKey] = []
				isHeadline = False
				count += 1
			else:
				if (not (w[index][0] == u'\u2022') and isHeadline == False):
					wDict['W'].pop(dictKey, None)
					dictKey += '#footnote' + str(count) + '#'
					wDict['W'][dictKey] = []
					footDict['footnotes'][count] = content.strip()
					count += 1
				else:
					if (w[index][0] == u'\u2022' and count == 0):
						general.append(content.replace(u'\u2022 ', '').strip())
						isHeadline = True
					if (w[index][0] == u'\u2022' and count > 0):
						wDict['W'][dictKey].append(content.replace(u'\u2022 ', '').strip())
						isHeadline = True
		
		if (general):
			wDict['W']['general'] = general
		if (footDict['footnotes']):
			self.personDict.update(footDict)
		
		self.personDict.update(wDict)
		
	def getPersonDict(self):
		'''
		Method that returns the complete dictionary:
		@return self.personDict: the complete dictionary
		'''
		return self.personDict


class makePickleFromData():
	'''
	Starts the parsing of the data, starts formating of the data and saves
	everything to different pickle files.
	'''	
	def getData(self):
		'''
		Opens a list of all websites for parsing.
		Starts parsing and formating of the data.
		'''
		htmlList = openPickle(os.getcwd(), 'listOfAllHTMLSites.pickle')
		
		numberOfPages = len(htmlList)
		
		count = 1
		for index, content in enumerate(htmlList):
			try:
				page = urlopen(content)
			except Exception as e:
				print(e)
			
			fileName = content[content.rfind('/') + 1:]
			fileName.replace('.html', '').strip()
			
			dataParser = PersonDataParser()
			dataParser.feed(convertHTMLChars(page.read()))
			dataParser.close()
			
			data = dataParser.getText()
			
			dataFormater = DataFormater(data, fileName)
			dataFormater.makeDict()
			
			dataDict = dataFormater.getPersonDict()
			
			saveCurDict(dataDict, (os.getcwd() + '/pickle'), fileName)
			
			print(fileName + ' (' + str(count) + '/' + str(numberOfPages) + ')')
			count += 1
		

def main():
	'''
	Main Method.
	'''
	makePickle = makePickleFromData()
	makePickle.getData()

if __name__ == "__main__":
	main()
