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
import re

from TTLClasses import TTLSet
from TTLClasses import TTLRessource

from convertHelper import openPickle
from convertHelper import save
from convertHelper import print_what_it_is
from convertHelper import createASCIIString
from convertHelper import transLitGerRu
from convertHelper import getListOfPickles
from pprint import pprint

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
        self.initTTLSet()
        self.personDict = personDict
        self.createPersonAsRessource()
        self.currentFootnote = 0
        
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
#         ontTTLRes.addPropObj("owl:imports", "drw-model:") #imports the drw/model Do not function
        self.personTTLSet.addRessource(ontTTLRes)
    
        
    def generateTTL(self):
        """
        Method to generate semantic Data with the Help of methods:
        self.generateNames and self.generateRestOfInfo
        
        """ 
        self.generateNames()
        try:
            self.generateRestOfInfo()
        except Exception as thisException:
            print "Could not be generated:"
            print self.personDict["ID"]
            print self.personDict["Name"]["Nachname"]
            print thisException
            print
        if len(self.personDict["footnotes"]) != self.currentFootnote:
            print ("Bei " + self.personDict["ID"] + " " + self.personDict["Name"]["Nachname"])
            print ("Von: " + str(len(self.personDict["footnotes"])) + " Fussnoten sind: " + str(self.currentFootnote) + " Fussnoten erfasst")
        
    def createPersonAsRessource(self):
        """
        Creates the base TTLRessource of a Person with the ID
        @raise Excetion: If the persondict do not contain the key self.personDict["ID"]
        @return TTLRessource object for the Person which should be integrated.
        """
        if "ID" not in self.personDict:
            raise Exception("Can not create person Ressource. The dictionary has no Key 'ID'") 
        newPersonTTLRes = TTLRessource("ImportantPerson/" + self.personDict["ID"], "drw-model:ImportantPerson", False)
        newPersonTTLRes.addRelationship("drw-model:hasID", '"' + self.personDict["ID"] + '"')
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
        if "Alternative Namen" in self.personDict:
            self.generateAlternativeNames()
    
    def generateMainName(self):
        """
        Adds the Main Name of a Person.
        @todo: Add kyrillic Names self.personDict["Name kyrrilisch"]
        
        """ 
        firstName = self.personDict["Name"]["Vornamen"]
        lastName = self.personDict["Name"]["Nachname"]
        name = lastName + ", " + firstName
        self.generateRelToPerson("hasMainName", "MainName", name)
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])        
        personTTL.addPropLabel(name)
        
        
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
                name = lastName + ", " + firstName
                if varName["sprache"] == "russ. trans.":
                    countryCode = "rude"
                elif varName["sprache"] == "deutsch":
                    countryCode = "de"
                elif varName["sprache"].strip() == "":
                    countryCode = False
                else:
                    name = name + " (" + varName["sprache"] + ")"
                    countryCode = False
#                     print ("Sprache " + varName["sprache"] + " ist nicht unterstuetzt")
                oneNameVar = {"name": name, "countryCode":countryCode}
                varNameList.append(oneNameVar)
        for nameVarNr in range(len(varNameList)):
            self.generateOneNameVariation(varNameList[nameVarNr])
        
    
    def generateOneNameVariation(self, nameVar):
        """
        Generates with a name variation construction new variation name TTLRessource objects.
        @requires: Data from self.generateNameVariations 
        @param nameVar: The variation Name Construct 
        """
        if "countryCode" in nameVar:
            countryCode = nameVar["countryCode"]
        else:
            countryCode = False
        name = nameVar["name"]
        isRussianName = False
        if countryCode == "rude":
            isRussianName = True
            countryCode = "de"
#             firstNameRu = transLitGerRu(firstName)
#             lastNameRu = transLitGerRu(lastName)
            nameRu = transLitGerRu(name)
#             lastNameRu + ", " + firstNameRu
        mainNameTTLRes = self.personTTLSet.getRessource("MainName/" + self.personDict["ID"] + "hasMainName")
        varNameTTLRes = self.generateRelToGivenRes(mainNameTTLRes, "hasNameVariation", "NameVariation", (name, countryCode), False, True)
        if isRussianName:
            varNameTTLRes.addPropLabel(nameRu, "ru")
        
        
       
    
    def generateAlternativeNames(self):
        """
        Reorganizes the alternative Name Construct and generates with the reorganized Data the name 
        variations as TTLRessource Object and integrates it.
        Uses self.generateOneNameVariation method.
        Adds name variations as Ressources to self.personTTLSet and relationship to personTTL
        """ 
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        varNameList = []
        for varName in self.personDict["Alternative Namen"]:
            if varName["sprache"] != "russ.":
                firstName = []
                countryCode = ""
                for oneFirstName in varName["vornamen"]:
                    firstName.append("/".join(oneFirstName))
                firstName = " ".join(firstName)
                lastName = varName["nachname"]
                name = lastName + ", " + firstName
                if varName["sprache"] == "russ. trans.":
                    countryCode = "rude"
                elif varName["sprache"] == "deutsch":
                    countryCode = "de"
                elif varName["sprache"].strip() == "":
                    countryCode = False
                else:
                    name = name + " (" + varName["sprache"] + ")"
                    countryCode = False
#                     print ("Sprache " + varName["sprache"] + " ist nicht unterstuetzt")
                oneNameVar = {"name": name, "countryCode":countryCode}
                varNameList.append(oneNameVar)
        for nameVarNr in range(len(varNameList)):
            self.generateOneAlternativeName(varNameList[nameVarNr])
            
    def generateOneAlternativeName(self, nameVar):
        """
        Generates with one alternative name construction new alternative name TTLRessource objects.
        @requires: Data from self.generateNameVariations 
        @param nameVar: The variation Name Construct 
        """
        if "countryCode" in nameVar:
            countryCode = nameVar["countryCode"]
        else:
            countryCode = False
        name = nameVar["name"]
        isRussianName = False
        if countryCode == "rude":
            isRussianName = True
            countryCode = "de"
#             firstNameRu = transLitGerRu(firstName)
#             lastNameRu = transLitGerRu(lastName)
            nameRu = transLitGerRu(name)
#             lastNameRu + ", " + firstNameRu
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        varNameTTLRes = self.generateRelToGivenRes(personTTLRes, "hasAlternativeName", "AlternativeName", (name, countryCode), False, True)
        if isRussianName:
            varNameTTLRes.addPropLabel(nameRu, "ru")
            
            
    def generateRestOfInfo(self):
        """
        Integrates the most of the Data to the TTLSet by going through the Dictionary and 
        generates for every section the needed TTLRessource Object.
        Integrates: Geburtsdaten, Sterbedaten, PortraitURL, V, M, E, G, N, Berufe, A, B, WL, MG, GPV, W, Q, SL, P
        @todo: "Quelle" including "First Page" and "Last Page"
        "PortraitURL"
        @todo: RessourcenNamen anpassen
         
        """
        self.generateBirthData()
        self.generateDeathData()
        self.generatePortraitData()
        self.generateRelativesData()
        self.generateLaborData()
        self.generateAData()
        self.generateBData()
        self.generateWLData()
        self.generateMGData()
        self.generateGPVData()
        self.generateWData()
        self.generateQData()
        self.generateSLData()
        self.generatePData()
        
    def generateBirthData(self):
        """Generates TTLData related to Birth """
        if "Geburtsdaten" in self.personDict:
            if "Datum" in self.personDict["Geburtsdaten"]:
                self.generateRelToPerson("wasBornOn", "Date", self.personDict["Geburtsdaten"]["Datum"])
            if "Ort" in self.personDict["Geburtsdaten"]:
                self.generateRelToPerson("wasBornIn", "Place", self.personDict["Geburtsdaten"]["Ort"])
                
    def generateDeathData(self):
        """Generates TTLData related to Death """
        if "Sterbedaten" in self.personDict:
            if "Datum" in self.personDict["Sterbedaten"]:
                self.generateRelToPerson("DiedOn", "Date", self.personDict["Sterbedaten"]["Datum"])
            if "Ort" in self.personDict["Sterbedaten"]:
                self.generateRelToPerson("DiedIn", "Place", self.personDict["Sterbedaten"]["Ort"])
    
    def generatePortraitData(self):
        """Generates TTLData related to portrait """
        if "PortraitURL" in self.personDict:
            personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
            personTTLRes.addExtRelation("<http://xmlns.com/foaf/0.1/img>" , "http://localhost/~wolfo/" + self.personDict["PortraitURL"])
    
    def generateRelativesData(self): 
        """Generates TTLData related to relatives """
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
    
    def generateLaborData(self):
        """Generates TTLData related to general Labor """
        if "Berufe" in self.personDict:
            self.generatePersonObjectsFromList("hasGeneralLabor", "GeneralLabor", self.personDict["Berufe"].split(", "))
            """@todo: Muss noch allgemein gemacht werden (URIs)"""
    
    def generateAData(self):
        """Generates TTLData related to Education - A """
        if "A" in self.personDict:
            if self.personDict["A"][0][0] == "yearList":
                self.generateObjectsFromYearList("hasEducation", "A", self.personDict["A"][0][1])
            #test if "A" has not specified objects
            if len(self.personDict["A"]) != 1:
                raise Exception("In 'A' is a Subtitle which is not specified and so deleted.")
    
    def generateBData(self):
        """Generates TTLData related to Life Stations - B """
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
                    self.generateObjectsFromYearList("hasStationOfLife", "B", sublist[1])
                elif u'Au\u00dferdem' in sublist[0]:
                    self.generatePersonObjectsFromList("hasAlsoImportantInfo", "AlsoImportantInfo", sublist[1].split("\n"))
                elif u'Ehrungen' in sublist[0]:
#                     print sublist[1]
                    self.generateRelToPerson("hasHonoursAndAwards", "HonoursAndAwards", sublist[1].replace("\n", "<br>"))
                    #@todo: Divide lines in Object. Be carefull with subtitles as: "bennant nach:"
                    if u'(Auswahl' in sublist[0]:
                        self.generateRelToPerson("hasHonoursAndAwardsComment", "HonoursAndAwardsComment", sublist[0])
                       #@todo: Muss noch allgemein gemacht werden (URIs)
                elif u'Andere \u00c4mter:' in sublist[0]:
                    self.generatePersonObjectsFromList("hasOtherOffices", "OtherOffices", sublist[1].split("\n"))
                else:
                    print sublist[0]
                    raise Exception(u"There is a Subclass of 'B' which is not in List and because of this deleted.")# + "\n" + sublist[0])
    
    def generateWLData(self):
        """Generates TTLData related to Scientific Career  - WL"""
        if "WL" in self.personDict:
            self.generatePersonObjectsFromList("hasWL", "WL", self.personDict["WL"].split("\n"))
            
    def generateMGData(self):
        """Generates TTLData related to Memberships - MG"""
        if "MG" in self.personDict:
            self.generateRelToPerson("hasMG", "MG", self.personDict["MG"])
            
    def generateGPVData(self):
        """Generates TTLData related to printed publication directories - GPV"""
        if "GPV" in self.personDict:
            if "general" in self.personDict["GPV"]:
                self.generatePersonObjectsFromList("hasGPV", "GPV", self.personDict["GPV"]["general"])
            if len(self.personDict["GPV"]) != 1:
                for subtitle in self.personDict["GPV"]:
                    print subtitle
                raise Exception("In 'GPV' is a subtitle which is not described and because of this Deleted")
            
    def generateWData(self):
        """Generates TTLData related to Scintific Publications - W """
        if "W" in self.personDict:
            for sublist in self.personDict["W"]:
                if sublist == "general":
                    self.generatePersonObjectsFromList("hasW", "W", self.personDict["W"]["general"])
                elif "Publikationen in deutscher Sprache:" in sublist or "Deutschsprachige Publikationen" in sublist:
                    self.generatePersonObjectsFromList("hasWGermanPublication", "WGermanPublication", self.personDict["W"][sublist])
                    if "#footnote" in sublist:
                        if sublist.count("#footnote") != 1:
                            raise Exception("hier sind zuviele Fussnoten")
                        footnotePattern = re.search("#footnote\d*#", sublist).group()
                        footnoteNr = footnotePattern.replace("footnote","").replace("#","")
                        footnoteText = self.personDict["footnotes"][int(footnoteNr)] 
                        self.generateRelToPerson("hasGermanPublicationComment", "GermanPublicationComment", sublist[0])
                        self.currentFootnote += 1
                elif "Russischsprachige Publikationen:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.generatePersonObjectsFromList("hasWRussianPublication", "WRussianPublication", self.personDict["W"][sublist])
                elif "bersetzungen ins Deutsche:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.generatePersonObjectsFromList("hasWTranslationsToGerman", "WTranslationsToGerman", self.personDict["W"][sublist])
                elif "bersetzungen aus dem Deutschen:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.generatePersonObjectsFromList("hasWTranslationsFromGerman", "WTranslationsFromGerman", self.personDict["W"][sublist])
                elif "bersetzungen:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.generatePersonObjectsFromList("hasWTranslations", "WTranslations", self.personDict["W"][sublist])         
                elif "Redaktion von " in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.generatePersonObjectsFromList("hasWEditorialOfTranslation", "WEditorialOfTranslation", self.personDict["W"][sublist])         
                elif u"Korrigierte und erg\u00E4nzte Angaben zum GPV:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.generatePersonObjectsFromList("hasWCorrectedAndCompletedInfoOfGPV", "WCorrectedAndCompletedInfoOfGPV", self.personDict["W"][sublist])
                else: 
                    print "X"
                    print sublist
                    print "X"
                    
    def generateQData(self):
        """Generates TTLData related to Sources - Q """
        if "Q" in self.personDict:
            self.generatePersonObjectsFromList("hasQ", "Q", self.personDict["Q"])
            
    def generateSLData(self):
        """Generates TTLData related to secondary Literature - SL """
        if "SL" in self.personDict:   
            for subtitle in self.personDict["SL"]:   
                if "general" in subtitle:
                    self.generatePersonObjectsFromList("hasSL", "SL", self.personDict["SL"][subtitle])
                elif "footnote" in subtitle:
                    print subtitle
                    raise Exception("There is a footnote in subtitle in SL which is deleted")
                elif "(Auswahl" in subtitle:
                    self.generatePersonObjectsFromList("hasSL", "SL", self.personDict["SL"][subtitle])
                    self.generateRelToPerson("hasSLComment", "SLComment", subtitle)
                else:
                    raise Exception("There is a subtitle in 'SL' which is deleted.\n" + subtitle)
    
    def generatePData(self):
        """Generates TTLData related to known Portraits - P """
        if "P" in self.personDict:
            self.generatePersonObjectsFromList("hasP", "P", self.personDict["P"])
        
#Generic methods
#===============

    def generateRelToPerson(self, predicate, type, label, nr="", notFootnote=True):
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
        while "#footnote" in label and notFootnote:
            label = self.generateFootnote(newTTLRes, label)
        notFootNote = True
        while "#internNameLink#" in label and notFootnote:
            label = self.generateNameLinks(newTTLRes, label)        
        newTTLRes.addPropLabel(label)
        personTTLRes.addPropObj("drw-model:" + predicate, newTTLRes.getURI())
        
        self.personTTLSet.addRessource(newTTLRes)
        
        return newTTLRes
        
    def generateFootnote(self, ttlWithFootnotes, label):
        commentPredicate = "hasComment"
        commentType = "Comment"
        regSearchString = "#footnote\d*#"
        reFootnote = re.search(regSearchString, label)
#         print "Fussnote:"
        footnoteNr = reFootnote.group().replace("#footnote", "").replace("#", "")
#         print footnoteNr
        commentLabel = self.personDict["footnotes"][int(footnoteNr)]
#         print commentLabel
        label = label.replace(reFootnote.group(), "[" + footnoteNr + "]" )
#                 newCommentTTLRes = generateRelToPerson(type + "/" + self.personDict["ID"] + commentPredicate + str(self.currentFootnote), "drw-model:" + commentType, False)
                #Legt die Fussnoten Ressource an
        newCommentTTLRes = self.generateRelToPerson(commentPredicate, commentType, commentLabel, str(footnoteNr), False)
#                 print newCommentTTLRes.getTTLCode()
        newCommentTTLRes.addRelationship("drw-model:hasNumber", footnoteNr)
        ttlWithFootnotes.addRelationship("drw-model:hasComment", newCommentTTLRes.getURI())
        self.personTTLSet.addRessource(newCommentTTLRes)
        self.currentFootnote += 1 #zur Kontrolle, ob ale Fussnoten gefunden wurden
        
        return label
        
    def generateNameLinks(self, ttlWithNames, label):
        """
        Generic method to Create out of a label with "#internNameLink#<Number>#endNameNr#<Name>#/internNameLink#"
        patterns inside the Label new Labels without these patterns and relations to the related Person.
        @param ttlWithNames: TTLResource where the new information should be added
        @param label: Label of this Ressource with  "#internNameLink#<Number>#endNameNr#<Name>#/internNameLink#"
        annotations
        @return: new cleaned Label
        """
        commentPredicate = "hasNamelink"
        commentType = "ImportantPerson"
        regSearchString = "#internNameLink#\d*#endNameNr#[\D]*#/internNameLink#"
        reNameLink = re.search(regSearchString, label)
        if not reNameLink:
            raise Exception("#internNameLink# ist falsch formatiert")
#         print "Name:"
        oldNameLink = reNameLink.group()
        newNameLink = oldNameLink.replace("#internNameLink#", "").replace("#/internNameLink#", "")
        linkedPersonNr = re.search("\d*",newNameLink).group()
        name = newNameLink.replace(linkedPersonNr + "#endNameNr#", "")
#         print oldNameLink
#         print linkedPersonNr
#         print name
        
#         print footnoteNr
#         print commentLabel
        label = label.replace(oldNameLink, '#name#' + name + "#/name#" )
#         print label
#                 newCommentTTLRes = generateRelToPerson(type + "/" + self.personDict["ID"] + commentPredicate + str(self.currentFootnote), "drw-model:" + commentType, False)
                #Legt die Fussnoten Ressource an
        #creates a ne Linked Person
        newPersonTTLRes = TTLRessource("ImportantPerson/" + linkedPersonNr, "drw-model:ImportantPerson", False)
        newPersonTTLRes.addRelationship("drw-model:hasID", '"' + linkedPersonNr + '"')
        newPersonTTLRes.addRelationship("drw-model:hasConnectionTo", "<ImportantPerson/" + self.personDict["ID"] + ">")
#         print newPersonTTLRes.getTTLCode()
        self.personTTLSet.addRessource(newPersonTTLRes)
        #creates Link to this Person
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        personTTLRes.addRelationship("drw-model:hasConnectionTo", "<ImportantPerson/" + linkedPersonNr + ">")
        #createsLinkTo
#         print personTTLRes.getTTLCode()
        
        return label
    
    def generateRelToGivenRes(self, subjectTTLRes, predicate, type, newLabel, notInternnameLink=True, unique = False):
        """
        Add new TTLRessource object and integrates relation to subjectTTLRessource 
        There is no connction to the persons TTLRessource Object
        
        @param subjectTTLRes: The existing TTLRessource to whom the new relation should be integrated
        @param predicate: The property as URI which describes the Connection to the new TTLRessource
        object
        @param type: The type of the new TTLRessource object
        @param newLabel: the label of the new TTLRessource object if it is a set (label, countryCode) the
        countrycode will be added to the Label
        @return: the new TTLRessource object
        
        """
        if isinstance(newLabel, tuple):
            label = newLabel[0]
            labelCountryCode = newLabel[1]
        else:
            label = newLabel
            labelCountryCode = False
        labelWithoutFootnote = label
        if "#footnote" in label:
            if label.count("footnote")>1:
                raise Exception("Mehrere Fussnoten in einer Zeitangabe")
            else:
                footnoteString = re.search("#footnote\d*#", label).group()
                labelWithoutFootnote = label.replace(footnoteString, "")
        if unique:
            ident = self.personDict["ID"]
            individNr = 0
            testUri = type + "/" + ident + "_" + str(individNr)
            while True:
                if self.personTTLSet.isRessourceIn("<" + testUri + ">"):
                    individNr += 1
                    testUri = type + "/" + ident + "_" + str(individNr)
                else:
                    break
            uri = testUri
            newTTLRes = TTLRessource(uri, "drw-model:" + type, False)
        else:
            newTTLRes = TTLRessource(type + "/" + createASCIIString(labelWithoutFootnote), "drw-model:" + type, False)
        while "#footnote" in label:
            label = self.generateFootnote(newTTLRes, label)
        while "#internNameLink#" in label and notInternNameLink:
            label = self.generateNameLinks(newTTLRes, label)        
        newTTLRes.addPropLabel(label, labelCountryCode)
        subjectTTLRes.addPropObj("drw-model:" + predicate, newTTLRes.getURI())
        
        self.personTTLSet.addRessource(newTTLRes)
        
        return newTTLRes
    
    def generatePersonObjectsFromList(self, predicate, type, labelList):
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
            
#     def generateObjectsFromList(self, ressource, predicate, type, labelList):
#         """
#         
#         """
#         for elementNr in range(len(labelList)):
#             self.generateRelToGivenRes(ressource, predicate, type, labelList[elementNr], True, True)

    
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
            #split time constructions
            yearInformation = element[0]
            if element[0] == "ohne Datum" or element[0] == "":
                yearValueList.append({})
            elif re.match("<.*>",element[0]):
                print element[0]
                yearValueList.append({})
            elif re.match("\d{4}-\d{4}",element[0]) and len(element[0]) == 9:
                yearValueList.append({"began": element[0][:4], "ended":element[0][-4:]})
            elif re.match("\d{4}",element[0]) and len(element[0]) == 4:
#                 print element[0]
                yearValueList.append({"onDay": element[0]})
            elif re.match("[Vv]or\s\d{4}",element[0]) and len(element[0]) == 8:
#                 print element[0][4:]
                yearValueList.append({"ended": element[0][4:]})
            elif re.match("[Aa]b\s\d{4}",element[0]) and len(element[0]) == 7:
#                 print element[0][3:]
                yearValueList.append({"began": element[0][3:]})
            else:
#                 print element[0]
                yearValueList.append({"began": element[0]}) 
            entryList.append(element[1])
        for elementNr in range(len(yearList)):
            textTTLRes = self.generateRelToPerson(predicate, type, entryList[elementNr], str(elementNr))
            if "isOn" in yearValueList[elementNr]:
                self.generateRelToGivenRes(textTTLRes, "inYear", "Year", yearValueList[elementNr]["inYear"])
            if "began" in yearValueList[elementNr]:
                self.generateRelToGivenRes(textTTLRes, "began", "Year", yearValueList[elementNr]["began"])
            if "ends" in yearValueList[elementNr]:
                self.generateRelToGivenRes(textTTLRes, "ended", "Year", yearValueList[elementNr]["ended"])
            
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
        
def italicHTML(text):
    """
    Replace "#italic#" to "<i>" and "#/italic#" to "</i>"
    @param text: input Text
    @return Text without "#italic#"
    """
    text = text.replace("#italic#","<i>")
    text = text.replace("#/italic#","</i>")
    text = text.replace("#name#","<span style='font-variant:small-caps;'>")
    text = text.replace("#/name#",'</span>')

    return text    

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
# #     
    allTTLs = TTLSet()
    allTTLs.addBase("http://drw-catalog.saw-leipzig.de/")  
    for element in listOfPickles:
#         if element == "30749.pickle":    
        if True:
            personDict = openPickle(os.getcwd()+"/pickleFiles", element)       
            personConverter = PersonConverter(personDict)
            personConverter.generateTTL()
            newTTLSet = personConverter.getTTLSet()#auskommentieren
            allTTLs.combine(newTTLSet)
            ttlString = personConverter.getStrOfTTLSet()
            ttlString = italicHTML(ttlString)
            structureAsText = print_what_it_is(personDict, True)
#          print structureAsText
            save(ttlString, os.getcwd() + "/ttlFiles", element , ".ttl")
    ttlString = allTTLs.getTTLCode()
    ttlString = italicHTML(ttlString)
    save(ttlString, os.getcwd(), "allRessources" , ".ttl")
 
    
def main(argv):
    """Main method"""
    test()

if __name__ == "__main__":
    main(sys.argv[1:])
    
 