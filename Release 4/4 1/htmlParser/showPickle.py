#!/usr/bin/python
# coding: utf8

from dictHelper import openPickle #open pickle files
from pprint import pprint #print

import os #path operations

class TestPickle():
	'''
	Class for showing the content of the pickle files. So its easier to find
	possible errors from the parser or the formater.
	'''
	def showPickle(self):	
		'''
		Method to show the content of all or one specific pickle file.
		The pickle files have to be in a ./pickle folder.
		'''
		print('(1) all\n(2) one specific')
		
		input_menu = ''
		correct = False
		
		while(correct == False):
			input_menu = raw_input('\n1 or 2: ')
			if (input_menu == '1' or input_menu == '2'):
				correct = True
		
		if (input_menu == '1'):
			path = os.getcwd() + '/pickle'
			
			dirList = os.listdir(path)
			
			for fileName in dirList:
				fileInDir = openPickle((os.getcwd() + '/pickle'), fileName)
				print(fileName + '\n')
				pprint(fileInDir)
				print('\n')
		else:
			input_person = raw_input('\npersonid: ')
			try:
				pprint(openPickle((os.getcwd() + '/pickle'), input_person + '.pickle'))
			except:
				pass
				
def main():
	'''
	Main Method, starts showPickle().
	'''
	pickleTest = TestPickle()
	pickleTest.showPickle()
	
if __name__ == '__main__':
	main()
