#!/usr/bin/python
# coding: utf8

from dictHelper import openPickle #open pickle file
from dictHelper import saveCurDict #save to pickle file
from urllib import urlopen #open url

import os #path operations

class HTMLDownloader():
	'''
	Helper class to download the complete drw-catalog from the web so it could
	be parsed faster or easier tested. It saves the sites to the folder ./html
	and creates a file with a list of the local path and filesnames of the sites
	for the	parser.
	'''
	def download(self):
		htmlList = openPickle(os.getcwd(), 'listOfAllHTMLSites.pickle')
		
		htmlListAsList = []
		
		numberOfPages = len(htmlList)
		
		count = 1
		for index, content in enumerate(htmlList):
			try:
				page = urlopen(content)
			except Exception as e:
				print(e)
			
			fileName = content[content.rfind('/') + 1:]
			fileName = fileName.replace('.html', '').strip()
		
			path = (os.getcwd() + '/html')
			if (not (os.path.isdir(path))):
				os.mkdir("/" + path)
			
			try:
				out_file = open(path + '/' + fileName + '.html', 'w')
				out_file.write(page.read())
				out_file.close()
			except IOError:
				print("File not Found. " + str(IOError))
			
			htmlListAsList.append(path + '/' + fileName + '.html')
		
			print(fileName + ' (' + str(count) + '/' + str(numberOfPages) + ')')
			count += 1
			
		saveCurDict(htmlListAsList, (os.getcwd()), 'listOfAllHTMLSitesLocal.pickle')


def main():
	'''
	Main method, starts the download.
	'''
	htmlDownloader = HTMLDownloader()
	htmlDownloader.download()

if __name__ == "__main__":
	main()
