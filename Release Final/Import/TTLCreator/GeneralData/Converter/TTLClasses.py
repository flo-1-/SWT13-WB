#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Contains classes to organize .turtle ressources.

@todo: label hinzufuegen 
@todo: import hinzufuegen
@author: Wolf 

"""

import codecs
import sys
import os
import pickle
import cgi #Fuer die HTML Entities

from convertHelper import openPickle
from convertHelper import print_what_it_is
from convertHelper import save

class TTLSet():
    """
    This class is a set of TTLRessource Object with the possibility to print
    the whole set as one .tutle formated text.

    @author: Wolf Otto
    
    """

#     __base = ""
    """
    stores the base of the turtle File as String
    """
    
#     __prefixes = {}
    """ 
    TTLSet.__prefixes: Stores prefixes of a .turtle file as a dictionary: 
    ''{"Abbreviation":"full uri"}''
    
    """

#     __ttlRessources = {}
    """ 
    TTLSet.__ttlRessources: stores a TTLRessource Object as a dictionary:
    ''{"uri":TTLRessource}''
    """
    def __init__(self):
        self.__base = ""
        self.__prefixes = {}
        self.__ttlRessources = {}
    
    def addRessource(self, newRessource):
        """
        This method adds a new TTLRessource Object
        
        @param newRessource: New TTLRessource
        """ 
        if newRessource.getURI() in self.__ttlRessources:
            self.__ttlRessources[newRessource.getURI()].combineTTL(newRessource)
        else:
            self.__ttlRessources[newRessource.getURI()] = newRessource
            
            
#         else:
#             if newRessource.getURI() in self.__ttlRessources:
#                 raise Exception("Die Ressource gibt es schon.")
#             else:
#                 self.__ttlRessources[newRessource.getURI()] = newRessource

    def addBase(self, uri):
        """
        Adds a base as str to self.__base
        
        """ 
        self.__base = "@base <" + uri + "> . \n"
        
    def addPrefix(self, abbr, uri):
        """
        This method adds a new prefixes.
        
        @param abbr: A str that is the new abbreviation
        @param uri: A str that is the new Uri
        """
        self.__prefixes[abbr] = uri

    def combine(self, newTTLSet):
        """
        Combines an Existing TTLSet with this Set.
        Combines all Prefixes and all Ressources. If some Ressourses have the same URI,
        they will be combined to one URI.
        @param newTTLSet: The TTLSet you want to integrate
        """
        newRessources = newTTLSet.getAllRessources()
        existingRessources = self.__ttlRessources
        for uri in newRessources:
            if uri in self.__ttlRessources:
                self.__ttlRessources[uri].combineTTL(newRessources[uri])
            else:
                self.__ttlRessources[uri] = newRessources[uri]
        for prefix in newTTLSet.getPrefixes():
            if prefix in self.__prefixes:
                if self.__prefixes[prefix] != newTTLSet.getPrefixes()[prefix]:
                    raise Exception("prefix and URI do not correspond") 
            else:
                print newTTLSet.getPrefixes()
                self.__prefixes[prefix] = newTTLSet.getPrefixes()[prefix]
#         self.__ttlRessources.update(newTTLSet.getAllRessources())

    def isRessourceIn(self, uri):
        """
        Checkes if a Ressource is allready in the TTLSet
        @param uri: The URI you want know from if it ist allready in the TTLSet
        @return: True if it exists, False else
        """ 
        if uri in self.__ttlRessources:
            return True
        else:
            return False
        
    def getBase(self):
        """
        getter for the base of the .TTL file for printing
        @return: The base of the .TTL file  in .turtle format
        """ 
        return self.__base
                

    def getRessource(self, uri):
        """
        Getter for a concrete Ressource stored in this object.
        
        @param uri: The full URI without "<" and ">" at the beginning and the end.
        @return: the TTLRessource if uri existes, else "none"
        """
        uri = "<" + uri + ">"
        if uri in self.__ttlRessources:
            return self.__ttlRessources[uri]
    
    def getRessourcePerson(self, personNr):
        """
        Getter for TTLREssource of a Person
        
        @param personNr: The IdentificationNumber of the Person
        @return: TTLRessource of the Person if URI with this Number exists, 
        else: "none" 
        """
        personTTL = self.getRessource("ImportantPerson/" + personNr)
        
        return personTTL

    def getAllRessources(self):
        return self.__ttlRessources
    
    def getPrefixes(self):
        return self.__prefixes
        
    def getPrefixesCode(self):
        """
        method to get the prefixes as a str
        @return: str with all stored prefixes in .turtle format
        """
        returnTTLText = u''
        for abbr in self.__prefixes:
            returnTTLText +="@prefix " + abbr + ": <" + self.__prefixes[abbr] + "> .\n"
        returnTTLText += u'\n'
        
        return returnTTLText
        
    def getTTLCode(self):
        """
        Getter for all Stored Data in .turtle format.
        Includes base and prefixes.
        @return: String aller TTLRessources und der Prefixausgabe in .turtle Formatierung
        """
        ttlText = ""
        ttlText += self.getBase()
        ttlText += self.getPrefixesCode()
        for uri in self.__ttlRessources:
            ttlText += self.__ttlRessources[uri].getTTLCode()
        return ttlText
    
class TTLRessource():
    """
    This class stores one resource with all the concerning Properties.
    """
#     unique = True
    """
    Boolean to say that this Ressource have to be unique and can not be
    combined with other TTLRessources with the same URI.
    """
#     uri = ""
    """The URI as str"""
#     relationships = set()
    """
    a set of tuples: (propertyURI, objectURI)
    A set to guarantee that no doublet could be stored.
    """
    def __init__(self, subjectID, type, unique=True):
        """
        Costruktor
        Creates a Ressource with given URI of the given type.
        @param subjectID: URI of the TTLRessource as str 
        @param type: URI of the type of the TTLRessource   
        @param unique: If TRUE it is allowed to combine this Ressource with 
        another of the same URI  
        """  
        self.unique = unique
        self.uri = u'<' + subjectID + u'>'
        self.relationships = set()
        self.relationships.add(("a", type))
#         print self.getTTLCode()

    
    def addRelationship(self, predicate, object):
        """
        Adds a new Relationship
        @param predicate: URI of the property as str
        @param object: URI of the object as str  
        """
        self.relationships.add((predicate, object))
        
    def addPropObj(self, predicate, object):
        """
        Adds relationship to object
        @param predicate: ist die URI der 
        """
        self.relationships.add((predicate, object))
        
    def addPropData(self, predicate, dataStr, countryCode = False):
        """
        adds relationship to Datatyp
        @param predicate: ist die URI der
        @param dataStr: str with data
        @param countryCode: Country code to add as annotation, if False nothing will 
        be added
        """
        if dataStr:
            dataStr = dataStr.replace('"', '\\"')
            countryAnnotation = ""
            if countryCode:
                countryAnnotation += "@" + countryCode
            self.relationships.add((predicate, '"' + dataStr + '"' + countryAnnotation))

    def addExtRelation(self, predicate, extURI):
        """
        adds external relationship Ressource
        Used for pictures
        @param predicate: property to connect the exernal Ressource
        @param extURI: The URI of the extarnal Ressource
        """
        self.relationships.add((predicate, '<' + extURI + '>' ))
        
    def addExtLiteral(self, predicate, extURI):
        """
        adds external relationship Ressource
        Used for pictures
        @param predicate: property to connect the exernal Ressource
        @param extURI: The URI of the extarnal Ressource
        """
        self.relationships.add((predicate, '"' + extURI + '"' ))

    
    def addPropLabel(self, labelText, countryCode = False):
        """
        adds an label as "rdfs:label" to self.relations
        
        @param labelText: The text of the label as str
        @param countryCode: The country code of the label if False no Countrycode
        is added   
        """
        self.addPropData("rdfs:label", labelText, countryCode)
    
    def getTTLCode(self):
        """
        getter of Ressource in .turtle format
        @return: Ressource in .turtle format as str
        """
        ttlAsText = u''
        ttlAsText += self.uri + "\n"
        for relationship in self.relationships:
            ttlAsText += "\t" + relationship[0] + " " + relationship[1] + " ;\n"
        ttlAsText = ttlAsText[:-2] + ".\n\n" #letztes ";" weg stattdessen "."
        
        return ttlAsText 
        
    def getURI(self):
        """
        getter: Uri of the ressource as str
        @return: Uri of the ressource as str
        """
        return self.uri
     
    def getRelationships(self):
        """
        getter: all relationships 
        @return: Set() of Tuples in this form: (<property>, <URI or "String">
        """
        return self.relationships
    
    def combineTTL(self,ttlToCombine):
        """
        Combines another TTLRessource Object with this one.
        @param ttlToCombine: TTLRessource Object to combine
        @raise Exception: If Unique=False in one of both TTLRessource Object
        @raise Exception: If there is not the same Ressource URI in both objects
        """
        if self.unique == False or ttlToCombine.isUnique() == False:
            if ttlToCombine.getURI() != self.uri:
                raise Exception("Only TTLRessource object with the same Ressource URI could be combined.")
            self.relationships = set.union(self.relationships, ttlToCombine.getRelationships())
            self.relationships.union(ttlToCombine.getRelationships())
            return self
        else:
            raise Exception("unique=True in one of the TTLRessource objects, which should be combined")
# def generateOneRessource():�
    def isUnique(self):
        """
        Asks, if the Ressource is set unique
        @return: True if Ressource is unique, else False
        """
        return self.unique

def test():
    """test method"""
    testRessource = TTLRessource("hallo", "drw-model:Krieg", False)
    testRessource.addRelationship("x", "z")
    testRessource.addRelationship("1", "5")
    testRessource.addRelationship("sdf", "sdfg")
    testRessource.addLabel("Gregor")
    testRessource.addLabel("Gregor", "de") #     print testRessource.getTTLCode()
    testRessource1 = TTLRessource("hallo", "drw-model:Krieg", False)
    testRessource1.addRelationship("x", "z")
    testRessource1.addRelationship("1", "5")
    testRessource1.addRelationship("sdf", "sdfg")
    testRessource1.addLabel("Viktor") #     print testRessource1.getTTLCode()
#     print testRessource.combineTTL(testRessource1).getTTLCode()
    newSet = TTLSet()
    newSet.addPrefix("kurz", "lang")
    newSet.addPrefix("kurzi", "langi")
    newSet.addRessource(testRessource)
    newSet.addRessource(testRessource1)
    print newSet.getTTLCode()

def main(argv):
    """main method"""
    test()

if __name__ == "__main__":
    main(sys.argv[1:])
    
 