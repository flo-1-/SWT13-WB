#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
This module contains a class which generates semantic Data in a .TTL conform text. 

@author: Niklas and Wolf 

"""

import codecs
import sys
import os
import pickle
import cgi #Fuer die HTML Entities

from TTLClasses import TTLSet
from TTLClasses import TTLRessource

from convertHelper import openPickle
from convertHelper import save
from convertHelper import print_what_it_is
from convertHelper import createASCIIString
from convertHelper import transLitGerRu
from convertHelper import getListOfPickles

class PersonConverter():
    """
    This Class contains a TTLSet Object with semantic Data. It generates this Data
    by evaluating a dictinary. This dictionary have to be put in by contructing 
    the class.
    
    """
#     personTTLSet = TTLSet()
    """ 
    A TTLSet object which contains the semantic Data in TTLRessorurce object Format
    """
#     personDict = dict()
    """
    The dictionary which contains the Data out of which the semantic data is generated 
    in the self.generateTTL method.
    """
    
    def __init__(self, personDict):
        """
        Construktor which initiates the self.personTTLSet with base and prefix information,
        integrates self.personDict, and creates a base TTLRessource object with the ID from 
        self.persondict["ID"]
        
        @param personDict: The dict() object which contains the Data which should be converted to
        .TTL formated semantic Data
        
        """
        self.personTTLSet = TTLSet()
        self.initTTLSet
        self.personDict = personDict
        self.createPersonAsRessource()
        
        
    def initTTLSet(self):
        """
        Generated all needed prefixes and a base for the prefix section in the .TTL Data
        
        """
        self.personTTLSet.addBase("http://drw-catalog.saw-leipzig.de/")
        self.personTTLSet.addPrefix("drw-model","http://drw-model.saw-leipzig.de/")
        self.personTTLSet.addPrefix("rdfs","http://www.w3.org/2000/01/rdf-schema#")
        self.personTTLSet.addPrefix("owl","http://www.w3.org/2002/07/owl#")
        ontTTLRes = TTLRessource("", "owl:Ontolgy", False)
        ontTTLRes.addPropLabel("DRW-Catalog") #Labeling the catalog
        ontTTLRes.addPropObj("owl:imports", "drw-model:") #imports the drw/model
        self.personTTLSet.addRessource(ontTTLRes)
    
        
    def generateTTL(self):
        """
        Method to generate semantic Data with the Help of methods:
        self.generateNames and self.generateRestOfInfo
        
        """ 
        self.generateNames()
        try:
            self.generateRestOfInfo()
        except Exception:
            print "Could not be generated:"
            print self.personDict["ID"]
            print self.personDict["Name"]["Nachname"]
            print
    
        
        
    def createPersonAsRessource(self):
        """
        Creates the base TTLRessource of a Person with the ID
        @raise Excetion: If the persondict do not contain the key self.personDict["ID"]
        @return TTLRessource object for the Person which should be integrated.
        """
        if "ID" not in self.personDict:
            raise Exception("Can not create person Ressource. The dictionary has no Key 'ID'") 
        newPersonTTLRes = TTLRessource("ImportantPerson/" + self.personDict["ID"], "drw-model:ImportantPerson", False)
        newPersonTTLRes.addRelationship("drw-model:drwID", '"' + self.personDict["ID"] + '"')
        self.personTTLSet.addRessource(newPersonTTLRes)
        
        return newPersonTTLRes
    
    def generateNames(self):
        """
        Adds the Name construct of the Person with name variations
        @todo: Implement "alternative names" called self.personDict["Alternativname"]
        """
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        self.generateMainName()
        self.generateNameVariations()
    
    def generateMainName(self):
        """
        Adds the Main Name of a Person.
        @todo: Add kyrillic Names self.personDict["Name kyrrilisch"]
        
        """ 
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        firstName = self.personDict["Name"]["Vornamen"]
        lastName = self.personDict["Name"]["Nachname"]
        name = lastName + ", " + firstName
        
        mainNameTTLRes = TTLRessource("MainName/" + self.personDict["ID"], "drw-model:MainName", False)
        mainNameTTLRes.addPropLabel(name)
        
        personTTL.addPropLabel(name)
        personTTL.addPropObj("drw-model:hasMainName", mainNameTTLRes.getURI())
        self.personTTLSet.addRessource(mainNameTTLRes)    
#         Possibility to add first name an last name as separate TTLREssource objects 
#         lastNameTTLRes = TTLRessource("LastName/" + self.personDict["ID"], "drw-model:LastName", False)
#         lastNameTTLRes.addPropLabel(lastName)
#         firstNameTTLRes = TTLRessource("FirstName/" + self.personDict["ID"], "drw-model:FirstName", False)
#         firstNameTTLRes.addPropLabel(firstName)
    
#         mainNameTTLRes.addPropObj("drw-model:firstNameIs", firstNameTTLRes.getURI())
#         mainNameTTLRes.addPropObj("drw-model:lastNameIs", lastNameTTLRes.getURI())
        
#         self.personTTLSet.addRessource(lastNameTTLRes)
#         self.personTTLSet.addRessource(firstNameTTLRes)
    
        
        
    def generateNameVariations(self):
        """
        Reorganizes the Variation Name Construct and generates with the reorganized Data the name 
        variations as TTLRessource Object and integrates it.
        Uses self.generateOneNameVariation method.
        Adds name variations as Ressources to self.personTTLSet and relationship to personTTL
        """ 
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        varNameList = []
        for varName in self.personDict["Namensvariationen"]:
            if varName["sprache"] != "russ.":
                firstName = []
                countryCode = ""
                for oneFirstName in varName["vornamen"]:
                    firstName.append("/".join(oneFirstName))
                firstName = " ".join(firstName)
                lastName = varName["nachname"]
                if varName["sprache"] == "russ. trans.":
                    countryCode = "rude"
                else:# varName["sprache"] == "deutsch":
                    countryCode = "de"
#                else:
#                     print ("Sprache " + varName["sprache"] + "ist nicht unterstuetzt")
                oneNameVar = {"lastName":lastName, "firstName": firstName, "countryCode":countryCode}
                varNameList.append(oneNameVar)
        for nameVarNr in range(len(varNameList)):
            self.generateOneNameVariation(varNameList[nameVarNr], str(nameVarNr))
        
    
    def generateOneNameVariation(self, nameVar, nameVarNr):
        """
        Generates with a name variation construction new variation name TTLRessource objects.
        @requires: Data from self.generateNameVariations 
        @param nameVar: The variation Name Construct 
        @param nameVarNr: The serial Number of one namevariation to create unique URIs
        """
        #adds Label to TTL
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        firstName = nameVar["firstName"]
        lastName = nameVar["lastName"]
        countryCode = nameVar["countryCode"]
        name = lastName + ", " + firstName
        
        isRussianName = False
        if countryCode == "rude":
            isRussianName = True
            countryCode = "de"
            firstNameRu = transLitGerRu(firstName)
            lastNameRu = transLitGerRu(lastName)
            nameRu = lastNameRu + ", " + firstNameRu
        varNameTTLRes = TTLRessource("NameVariation/" + self.personDict["ID"] + "var" +nameVarNr, "drw-model:NameVariation", False)
        varNameTTLRes.addPropLabel(name, countryCode)
        if isRussianName:
            varNameTTLRes.addPropLabel(nameRu, "ru")
            
        mainNameTTLRes = self.personTTLSet.getRessource("MainName/" + self.personDict["ID"])
        mainNameTTLRes.addPropObj("drw-model:hasNameVariation", varNameTTLRes.getURI())
        
        self.personTTLSet.addRessource(varNameTTLRes)
        
#         Code to generate first and last name as TTLRessource object, too.
#         lastNameTTLRes = TTLRessource("LastName/" + self.personDict["ID"] + "var" +nameVarNr, "drw-model:LastName", False)
#         lastNameTTLRes.addPropLabel(lastName, countryCode)
#         if isRussianName:
#             lastNameTTLRes.addPropLabel(lastNameRu, "ru")
#         firstNameTTLRes = TTLRessource("FirstName/" + self.personDict["ID"] + "var" +nameVarNr, "drw-model:FirstName", False)
#         firstNameTTLRes.addPropLabel(firstName, countryCode)
#         if isRussianName:
#             firstNameTTLRes.addPropLabel(firstNameRu, "ru")
       
#         varNameTTLRes.addPropObj("drw-model:firstNameIs", firstNameTTLRes.getURI())
#         varNameTTLRes.addPropObj("drw-model:lastNameIs", lastNameTTLRes.getURI())
        
#         self.personTTLSet.addRessource(lastNameTTLRes)
#         self.personTTLSet.addRessource(firstNameTTLRes)
#         self.personTTLSet.addRessource(mainNameTTLRes)
    
    
    def generateRestOfInfo(self):
        """
        Integrates the most of the Data to the TTLSet by going through the Dictionary and 
        generates for every section the needed TTLRessource Object.
        Integrates: V, M, E, G, N, Berufe, A, B, WL, MG, GPV, W, Q, SL, P
        @todo: "Geburtsdaten", "Sterbedaten", "Quelle" including "First Page" and "Last Page"
        "PortraitURL"
        @todo: RessourcenNamen anpassen
         
        """
        if "V" in self.personDict:
            self.generateRelToPerson("fatherIs", "RelatedPerson", self.personDict["V"])
        if "M" in self.personDict:
            self.generateRelToPerson("motherIs", "RelatedPerson", self.personDict["M"])
        if "E" in self.personDict:
            self.generateRelToPerson("wasMarriedTo", "RelatedPerson", self.personDict["E"])
        if "G" in self.personDict:
            self.generateRelToPerson("hasSibling", "RelatedPerson", self.personDict["G"])
        if "N" in self.personDict:
            self.generateRelToPerson("hasDescendant", "RelatedPerson", self.personDict["N"])
        if "Berufe" in self.personDict:
            self.generateObjectsFromList("hasGeneralLabor", "GeneralLabor", self.personDict["Berufe"].split(", "))
            """@todo: Muss noch allgemein gemacht werden (URIs)"""
        if "A" in self.personDict:
            if self.personDict["A"][0][0] == "yearList":
                self.generateObjectsFromYearList("hasEducation", "Education", self.personDict["A"][0][1])
            #test if "A" has not specified objects
            if len(self.personDict["A"]) != 1:
                raise Exception("In 'A' is a Subtitle which is not specified and so deleted.")
        if "B" in self.personDict:
            # The List of distionction in B
            auszeiListe = [u'Au\u00dferdem:']
            auszeiListe.append(u'Andere \u00c4mter:')
            auszeiListe.append(u'Ehrungen und Auszeichnungen:')
            auszeiListe.append(u'Ehrungen und Auszeichnungen (Auswahl):')
            auszeiListe.append(u'Ehrungen:')
            for sublist in self.personDict["B"]:
                if "footnote" in sublist[0]:
                    raise Exception("There is a Footnote in 'B' which is deleted.") 
                if sublist[0] == "yearList":
                    self.generateObjectsFromYearList("hasStationOfLife", "StationOfLife", sublist[1])
                elif u'Au\u00dferdem:' in sublist[0]:
                    self.generateObjectsFromList("hasOtherStationOfLife", "otherStationOfLife", sublist[1].split("\n"))
                elif u'Ehrungen' in sublist[0]:
#                     print sublist[1]
                    self.generateRelToPerson("hasHounoursAndAwards", "HonoursAndAwards", sublist[1].replace("\n", "<br>"))
                    #@todo: Divide lines in Object. Be carefull with subtitles as: "bennant nach:"
                    if u'(Auswahl' in sublist[0]:
                        self.generateRelToPerson("hasHounoursAndAwardsComment", "HounoursAndAwardsComment", "(Auswahl)")
                       #@todo: Muss noch allgemein gemacht werden (URIs)
                else:
                    raise Exception("There is a Subclass of 'B' which is not in List and because of this deleted.")
        if "WL" in self.personDict:
            self.generateObjectsFromList("hasWL", "WLStationOfLife", self.personDict["WL"].split("\n"))
        if "MG" in self.personDict:
            self.generateRelToPerson("hasMembership", "Membership", self.personDict["MG"])
        if "GPV" in self.personDict:
            if "general" in self.personDict["GPV"]:
                self.generateObjectsFromList("hasGPV", "GPVPublication", self.personDict["GPV"]["general"])
            else:
                raise Exception("In 'GPV' is a subtitle which is not described and because of this Deleted")
        if "W" in self.personDict:
            if "general" in self.personDict["W"]:
                self.generateObjectsFromList("hasW", "WPublication", self.personDict["W"]["general"])
            else:
                raise Exception("In 'W' is a subtitle which is not described and because of this Deleted")
        if "Q" in self.personDict:
            self.generateObjectsFromList("hasQ", "Q", self.personDict["Q"])
        if "SL" in self.personDict:   
            for subtitle in self.personDict["SL"]:   
                if "footnote" in subtitle:
                    raise Esception("There is a footnote in subtitle in SL which is deleted")
                if "general" in subtitle:
                    self.generateObjectsFromList("hasSL", "SLPublication", self.personDict["SL"][subtitle])
                elif "(Auswahl" in subtitle:
                    self.generateObjectsFromList("hasSL", "SLPublication", self.personDict["SL"][subtitle])
                    self.generateRelToPerson("hasSLComment", "SLComment", subtitle)
                else:
                    raise Exception("There is a subtitle in 'SL' which is deleted.\n" + subtitle)
            
        if "P" in self.personDict:
            self.generateObjectsFromList("hasP", "P", self.personDict["P"])
        

    def generateRelToPerson(self, predicate, type, label, nr=""):
        """
        Generic Method to generate new TTLRessource with Relationship to the TTLRessource Object 
        of the person.
        
        @param predicate: The property as URI which describes the Connection to the new TTLRessource
        object
        @param type: The type of the new TTLRessource object
        @param label: the label of the new TTLRessource object
        @param nr: A Numer to create a unique URI for the new TTLRessource if needed
        (more then one Ressource with identical type and label)
        @return: the new TTLRessource object
        """
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        newTTLRes = TTLRessource(type + "/" + self.personDict["ID"] + predicate + nr, "drw-model:" + type, False)
        newTTLRes.addPropLabel(label)
        personTTLRes.addPropObj("drw-model:" + predicate, newTTLRes.getURI())
        
        self.personTTLSet.addRessource(newTTLRes)
        
        return newTTLRes
        
    def generateRelToGivenRes(self, subjectTTLRes, predicate, type, label):
        """
        Add new TTLRessource object and integrates relation to subjectTTLRessource 
        There is no connction to the persons TTLRessource Object
        
        @param subjectTTLRes: The existing TTLRessource to whom the new relation should be integrated
        @param predicate: The property as URI which describes the Connection to the new TTLRessource
        object
        @param type: The type of the new TTLRessource object
        @param label: the label of the new TTLRessource object
        @return: the new TTLRessource object
        
        """
        newTTLRes = TTLRessource(type + "/" + createASCIIString(label), "drw-model:" + type, False)
        newTTLRes.addPropLabel(label)
        subjectTTLRes.addPropObj("drw-model:" + predicate, newTTLRes.getURI())
        
        self.personTTLSet.addRessource(newTTLRes)
        
        return newTTLRes
    
    def generateObjectsFromList(self, predicate, type, labelList):
        """
        Integrates a List of Strings as new TTLRessources of specified type with connection to
        the persons TTLRessource
        Uses self.generateRelToPerson method.
        @param predicate: The property as URI which describes the Connection to the new TTLRessource
        objects
        @param type: The type of the new TTLRessource objects
        @param labelList: A list() object with the labels of the new TTLRessource objects

        """
        for elementNr in range(len(labelList)):
            self.generateRelToPerson(predicate, type, labelList[elementNr], str(elementNr))
    #         "firstName": self.personDict["Name"]["Vornamen"]
    #         lastName = self.personDict["Name"]["Nachname"]
            

    def generateObjectsFromYearList(self, predicate, type, yearList):
        """
        generateObjectsFromYearList => Add year list of objects to self.personTTLSet
        Integrates a list of labels with corresponding Information about the time when it happens.
        
        @param predicate: The property as URI which describes the Connection to the new TTLRessource
        objects
        @param type: The type of the new TTLRessource objects
        @param yearList: A list in this Form [ [<timeInformation>, <labelInformation>], ...]
        Exactly two Elements in sublists!
        @raise Exception: If not exactly two Elements in sublists of yearlist
        """
        for element in yearList:
            if len(element) != 2:
                raise Exception("generateObjectsFromYearList method needs exactly two Elements in sublists")
        yearValueList = []
        entryList = []
        for element in yearList:
            yearValueList.append(element[0])
            entryList.append(element[1])
        for elementNr in range(len(yearList)):
            textTTLRes = self.generateRelToPerson(predicate, type, entryList[elementNr], str(elementNr))
            self.generateRelToGivenRes(textTTLRes, "began", "Date", yearValueList[elementNr])
#             self.generateRelToPerson(predicate, type, labelList[elementNr], str(elementNr))
            
            
    def getTTLSet(self):
        """
        Getter to get whole TTLSet() in current status.
        @return: whole TTLSet() in current status
        """
        return self.personTTLSet
    
    def getStrOfTTLSet(self):
        """
        Getter for whole TTL Text generated by getTTLCode() method of personTTLSet
        @return:   whole TTLSet() in current status in usable .TTL text format.
        """
        return self.personTTLSet.getTTLCode()
        
    
def test():
    """test method"""
    listOfPickles = getListOfPickles()
#     personDict = openPickle(os.getcwd()+"/pickleFiles", "20028.pickle")
#     personDict = openPickle(os.getcwd()+"/pickleFiles", "30732.pickle")
#     personDict = openPickle(os.getcwd()+"/pickleFiles", "30565.pickle")
#     personConverter = PersonConverter(personDict)
#     personConverter.generateTTL()
#     ttlString = personConverter.getStrOfTTLSet()
#     personDict = openPickle(os.getcwd()+"/pickleFiles", "20028.pickle")
#     personConverter = PersonConverter(personDict)
#     personConverter.generateTTL()
#     ttlString = personConverter.getStrOfTTLSet()
#     print ttlString
#     structureAsText = print_what_it_is(personDict, True)
#     save(ttlString, os.getcwd() + "/ttlFiles", "element" , ".ttl")
#       
    for element in listOfPickles:
         personDict = openPickle(os.getcwd()+"/pickleFiles", element)       
         personConverter = PersonConverter(personDict)
         personConverter.generateTTL()
         ttlString = personConverter.getStrOfTTLSet()
         structureAsText = print_what_it_is(personDict, True)
#          print ttlString
         save(ttlString, os.getcwd() + "/ttlFiles", element , ".ttl")

 
    
def main(argv):
    """Main method"""
    test()

if __name__ == "__main__":
    main(sys.argv[1:])
    
 