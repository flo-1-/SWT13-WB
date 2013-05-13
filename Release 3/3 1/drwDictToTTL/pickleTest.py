from drwHelper import openPickle
from pprint import pprint

import os

fileName = openPickle((os.getcwd() + '/'), 'personDict.pickle')

pprint(fileName)
