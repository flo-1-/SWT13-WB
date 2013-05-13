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
		self.paragraphs = ['V', 'M', 'E', 'A', 'B', 'WL', 'W', 'SL', 'P', 'GPV', 'Q', 'G', 'N']
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
		if (tag == 'td' and self.isParagraph == True): #every interesting data is between <td> and </td>
			self.getData = True
			self.isParagraph = False
			
		if (tag == 'td'):
			for attr, value in attrs:
				if (attr == 'class'): #search for classes which contain data or after them is interesting data
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
		
		if (tag == 'h3' and self.t100gFound == True): #the data for the name contains <h3> tag, so if <h3> tag is present, its the name
			self.text += '.:._.:.Name.:._.:.'
			self.foundParagraphs.append('Name')
			self.getData = True
		
		if (self.t100gFound == True and self.h3EndFound == True): #the source is also after the class t100g, so if an </h3> was found, it's the source
			self.foundParagraphs.append('Quelle')
			self.text += '.:._.:.Quelle.:._.:.'
			self.getData = True
		
		if (tag == 'img'): #looking for the portrait image, if there is one
			for name, value in attrs:
				if (name == 'src'):
					try:
						testValue = int(value[0]) #exclude pfeil.jpg
						self.text += '.:._.:.portraitURL.:._.:.' + value
						self.foundParagraphs.append('portraitURL')
					except:
						pass
						
				if (name == 'title' and value != u'zurück'): #find portrait text (exclude u'zurück', because it'S the back button
					self.text += '.:._.:.Portraittext.:._.:.' + value
					self.foundParagraphs.append('Portraittext')
		
		if (tag == 'a'):
			for attr, value in attrs:
				if (attr == 'href'):
					if(not('personendatenbank' in value)): #exclude link to the main page
						if (re.match("\d{5}\.html", value)): #if pattern matches 5 digits and .html (ex. 12345.html) it's a name link
							self.text += '#internNameLink#' + value.replace('.html', '') + '#endNameNr#'
							self.nameLinkFound = True
						else:
							self.text += value + ' ' #no name link, a link to an online resource
							
						self.getData = True
						
		if (self.getData == True and self.isParagraph == False):
			if (tag == 'i'): #bring back removed <i>
				self.text += '<i>'
				
			if (tag == 'b'): #bring back removed <b>
				self.text += '<b>'
	
	def handle_data(self, data):
		'''
		Handles the data, causes actions, if specific data were found or adds data
		to the datacollection.
		'''
		if (self.getData == True and self.isParagraph == False): #add current data if true
			self.text += data
		
		if (self.getData == False and self.isParagraph == True): #add MG instead of M, if M, A or B found before (because there are 2 M)
			if (data == 'M' and ('M' in self.foundParagraphs or ('A' in self.foundParagraphs or 'B' in self.foundParagraphs))):
						self.foundParagraphs.append('MG')
						self.text += '.:._.:.MG.:._.:.'
						self.getData = True
			else: #adds the paragraph description to the data (ex. A or B or WL or ...)
				if (data in self.paragraphs):
					self.foundParagraphs.append(data)
					self.paragraph = data
					self.text += '.:._.:.' + data +'.:._.:.'
					self.getData = True
				else:
					self.isParagraph = False
		
		if (self.getData == False and self.t100nFound == True):
			if (data[0] == '*'): #adds birth dates
				self.foundParagraphs.append('Geburtsdaten')
				self.text += '.:._.:.Geburtsdaten.:._.:.'
				self.text += data.strip()
				self.t100nFound = False
			elif (data[0] == u'\u2020'): #adds death dates
				self.foundParagraphs.append('Sterbedaten')
				self.text += '.:._.:.Sterbedaten.:._.:.'
				self.text += data.strip()
				self.t100nFound = False
			elif ('Namensvariationen' in data): #adds namevariations
				self.foundParagraphs.append('Namensvariationen')
				self.text += '.:._.:.Namensvariationen.:._.:.'
				self.text += data.replace('Namensvariationen:', '').strip()
				self.t100nFound = False
			else:
				data = data.strip().replace(u'\xa0', '')
				if (data != ''): # adds professions
					self.foundParagraphs.append('Berufe')
					self.text += '.:._.:.Berufe.:._.:.'
					self.text += data.strip()
					self.t100nFound = False

	def handle_endtag(self, tag):
		'''
		Handles the endtags, causes actions if specific endtags were found.
		Can stop the collection of data.
		'''
		if (tag == 'td' and self.isParagraph == False): #if </td> was found end adding data
			self.getData = False
			self.t100gFound = False
			
		if (tag == 'h3' and self.getData == True): #if </h3> was found
			self.getData = False
			self.h3EndFound = True
		
		if (tag == 'td' and self.t100sFound == True): #</td> was found and class=t100s before
			self.getData = False
			self.t100sFound = False
		
		if (tag == 'a' and self.nameLinkFound == True): #if namelink was found set end of the namelink text
			self.text += '#/internNameLink#'
			self.nameLinkFound = False
		
		if (self.getData == True and self.isParagraph == False):
			if (tag == 'i'): #bring back removed </i>
				self.text += '</i>'
				
			if (tag == 'b'): #bring back removed </b>
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
		textList = self.text.strip().split('.:._.:.') #split the text at .:._.:.
		textList = [item for item in textList if item.strip() != ''] #remove '' from the list
		
		count = 0
		while (count < len(textList)): #builds the unformated dictionary: {paragraph1: text1, paragraph2: text2, ...}
			self.personDict.update({textList[count]: textList[count + 1]})
			count += 2
		
		#start all Methods for formating the paragraphs
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
		{'Name': {'Vornamen': vorName, 'Nachname': nachName}
		'''
		name = self.personDict['Name'].split(',') #split at ',' beacause its lastname, firstnames
		name[1] = name[1].strip()
		
		if (' ' in name[0]):
			splittedName = re.split('( )', name[0]) #if firstname contains more then one name, split at ' ', including the ' '
		
			name[0] = ''
		
			for index, content in enumerate(splittedName):
				if (not (' ' in content)): #formts the lastname to lowercase after the first letter
					splittedName[index] = splittedName[index][0] + splittedName[index][1:].lower()
					name[0] += splittedName[index]
				else:
					name[0] += splittedName[index]
				
			name[0] = name[0].strip()
		else:
			name[0] = name[0].title()
			
		
		nameDict = {'Name': {'Nachname': name[0]}}
		nameDict['Name']['Vornamen'] = name[1]
		
		self.personDict.update(nameDict)
	
	def formatNameRus(self):
		'''
		Formats and adds the russian Name to the dictionary.
		The shape is like:
		{'Name russisch': {'name': name, 'countryCode': countryCode}
		countryCode can be 'de' or 'ru'
		'''
		nameRus = self.personDict['Name russisch'].split('/') #split at '/'
		nrDict = {'Name russisch': []}
		
		for index, content in enumerate(nameRus):
			if (re.search(u'[\u0400-\u04ff]', nameRus[index])):
				countryCode = 'ru' #if russian letters in the data
			else:
				countryCode = 'de' #if no russian letters in the data
			
			nrDict['Name russisch'].append({'name': nameRus[index].strip(), 'countryCode': countryCode})
		
		self.personDict.update(nrDict)
	
	def formatNameVariation(self):
		'''
		Formats and adds the namevariations to the dictionary:
		The shape is like:
		{'Namensvariationen': {'name': name, 'countryCode': countryCode}
		countryCode can be 'de' or 'ru'
		'''
		nameVariation = self.personDict['Namensvariationen'].split(',') #split at ','
		nvDict = {'Namensvariationen': []}
		
		for index, content in enumerate(nameVariation):
			if (re.search(u'[\u0400-\u04ff]', nameVariation[index])):
				countryCode = 'ru' #if russian letters in the data
			else:
				countryCode = 'de' #if no russian letters in the data
			
			nvDict['Namensvariationen'].append({'name': nameVariation[index].strip(), 'countyCode': countryCode})
			
		self.personDict.update(nvDict)
		
	def formatBorn(self):
		'''
		Formats and adds the birthdates to the dictionary.
		The shape is like:
		{'Geburtsdaten': {'Geburtsdatum': datum, 'Geburtsort': geburtsort}
		'''
		born = self.personDict['Geburtsdaten']
		born = born.replace('*', '').strip().split(',') #split at ',', removes the '*'
		
		for index, content in enumerate(born):
			born[index] = born[index].strip()
		
		bornDict = {'Geburtsdaten': {'Datum': born[0]}}
		if (len(born) == 2): #if only two elements in the list
			bornDict['Geburtsdaten']['Ort'] = born[1]
		if (len(born) > 2): #if more then two elements in the list, put the elements after the first two elements into the second element
			for index, content in enumerate(born):
				if (index > 1):
					born[1] += ', ' + born[index]
			bornDict['Geburtsdaten']['Ort'] = born[1]
		
		self.personDict.update(bornDict)
		
	def formatDeath(self):
		'''
		Formats and adds the deathdates to the dictionary.
		The form is like:
		{'Sterbedaten': {'Sterbedatum': datum, 'Sterbeort': ort, 'Grabstätte': grabstätte}
		'''
		death = self.personDict['Sterbedaten']
		deathDict = {'Sterbedaten': {}}
		
		if (u'Grabstätte:' in death): #if the cemetery is in the data
			death = death.split(u'Grabstätte:') #split at u'Grabstätte'
			cemetery = death[1].strip()
			deathDict['Sterbedaten']['Grabstätte'] = cemetery
			death = death[0].split(',')
		else: #if no cemetery is in the data
			death = death.split(',')
			
		dayOfDeath = death[0].replace(u'\u2020', '').strip()
		deathDict['Sterbedaten']['Datum'] = dayOfDeath
		if (len(death) == 2): #if only two elements in the list
			placeOfDeath = death[1].strip()
			deathDict['Sterbedaten']['Ort'] = placeOfDeath
		if (len(death) > 2): #if more then two elements in the list, put the elements after the first two elements into the second element
			placeOfDeath = death[1].strip()
			for index, content in enumerate(death):
				if (index > 1):
					death[1] += ', ' + death[index]
			deathDict['Sterbedaten']['Ort'] = placeOfDeath
		
		self.personDict.update(deathDict)
		
	def formatProfessions(self):
		'''
		Formats and adds the professions to the dictionary.
		The form is like:
		{'Berufe': [beruf1, beruf2, beruf3]}
		'''
		professions = self.personDict['Berufe'].split(',')
		for index, data in enumerate(professions): #make a list of all professions
			professions[index] = professions[index].strip()
		
		proDict = {'Berufe': professions}
		
		self.personDict.update(proDict)
		
	def formatParagraph(self, paragraph):
		'''
		Formats paragraphs with dots at the beginning.
		Removes the dots and puts in a shape like:
		{'A': [line1, line 2, line3]}
		SL and GPV get a special format:
		{'SL': {'general': [line1, line2, line3]}
		@param paragraph: paragraph to format
		'''
		splitParagraph = self.personDict[paragraph].split('\n')
		splitParagraph = [item.strip().replace(u'\u2022 ', '') for item in splitParagraph if item.strip() != '']
		
		if (paragraph == 'SL' or paragraph == 'GPV'):
			pDict = {paragraph: {'general': splitParagraph}}
		else:	
			pDict = {paragraph: splitParagraph}
			
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
		headLineFound = False
		general = []
		wDict = {'W': {}}
		footDict = {'footnotes': {}}
		
		w = self.personDict['W'].strip().split('\n')
		w = [item for item in w if item.strip() != '']
		
		count = 0
		for index, content in enumerate(w):
			stripContent = content.strip()
			if (not (stripContent[0] == u'\u2022') and len(w)== 1): #first letter isnt u'u2020' (unicode for •), W has only one line
				general.append(content.strip())
			elif (not (stripContent[0] == u'\u2022') and isHeadline == False): #first letter isnt u'u2020', footnote found
				count += 1
				wDict['W'].pop(dictKey, None)
				dictKey += '#footnote' + str(count) + '#'
				wDict['W'][dictKey] = []
				footDict['footnotes'][count] = content.strip().replace('*)', '') #create dictionary with footnotes
			elif (not (stripContent[0] == u'\u2022') and isHeadline == True): #Headline found
				if (index == len(w) - 1):
					wDict = {'W': {'letzteZeile': content.strip()}}
				elif (u'Sumpfgasgährung' in content): #exception to correct wrong assignment
					wDict['W'][dictKey].append(content.strip())
				elif ('Autor des Vorwortes' in content or 'darunter: Die' in content or 'Diverse Publikationen in:' in content): #exception to correct wrong assignment
					general.append(content.strip())
				else:
					dictKey = content.strip().replace('*)', '')
					wDict['W'][dictKey] = []
					isHeadline = False
					headLineFound = True
			if (stripContent[0] == u'\u2022' and count == 0): #first letter is u'u2020' (unicode for •), no headline found
				general.append(content.replace(u'\u2022 ', '').strip()) #no headline -> line to general
				isHeadline = True
			if (stripContent[0] == u'\u2022' and headLineFound == True): #first letter is u'u2020' (unicode for •), headline found
				wDict['W'][dictKey].append(content.replace(u'\u2022 ', '').strip()) #headline -> line to headline
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
		htmlList = openPickle(os.getcwd(), 'listOfAllHTMLSites.pickle') #use the sites on the web
		#htmlList = openPickle(os.getcwd(), 'listOfAllHTMLSitesLocal.pickle') #if html sites are in local folder './html
		
		numberOfPages = len(htmlList)
		
		count = 1
		for index, content in enumerate(htmlList):
			try:
				page = urlopen(content)
			except Exception as e:
				print(e)
			
			fileName = content[content.rfind('/') + 1:]
			fileName = fileName.replace('.html', '').strip()
			
			dataParser = PersonDataParser() #creates the parser
			dataParser.feed(convertHTMLChars(page.read())) #feeds the parser
			dataParser.close()
			
			data = dataParser.getText() #gets the parsed data
			
			dataFormater = DataFormater(data, fileName) #formats the data
			dataFormater.makeDict() #makes the dict
			
			dataDict = dataFormater.getPersonDict() #gets the data
			
			saveCurDict(dataDict, (os.getcwd() + '/pickle'), fileName) #saves the data
			
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
