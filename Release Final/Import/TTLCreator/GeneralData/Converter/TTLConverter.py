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
from copy import copy

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
        ontTTLRes = TTLRessource("", "owl:Ontology", False)
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
        if "footnotes" in self.personDict:
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
        mainNameTTL = self.createRelToPerson("hasMainName", "MainName", name, False, True, True)
#         mainNameTTL = self.generateRelToPerson("hasMainName", "MainName", name)
        personTTL = self.personTTLSet.getRessourcePerson(self.personDict["ID"])        
        while re.search("#footnote\d+#", name):
            footnote = re.search("#footnote\d+#", name)
            if footnote:
                name = name.replace(footnote.group(),"")
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
        if "Namensvariationen" in self.personDict:
            if "name" in self.personDict["Namensvariationen"][0]:
                varNameList = self.personDict["Namensvariationen"]
                
            else:
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
            nameWithoutFootn = re.sub("#footnote\d+#", "", name)
            nameRu = transLitGerRu(nameWithoutFootn)
#             lastNameRu + ", " + firstNameRu MainName/30013hasMainName1
        mainNameTTLRes = self.personTTLSet.getRessource("MainName/" + self.personDict["ID"] + "hasMainName"+"1")
        name = (name, countryCode)
        varNameTTLRes = self.createRelToRes(mainNameTTLRes, "hasNameVariation", "NameVariation",name , False, True, True)
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
            nameWithoutFootn = re.sub("#footnote\d+#", "", name)
            nameRu = transLitGerRu(nameWithoutFootn)
#             lastNameRu + ", " + firstNameRu
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        varNameTTLRes = self.createRelToRes(personTTLRes, "hasAlternativeName", "AlternativeName", (name, countryCode), False, True, True)
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
                self.createRelToPerson("wasBornOn", "Date", self.personDict["Geburtsdaten"]["Datum"],True,False)
            if "Ort" in self.personDict["Geburtsdaten"]:
# Daten genereieren
                label = self.personDict["Geburtsdaten"]["Ort"]
                self.createRelToPerson("wasBornIn", "Place", label, True, True)    
    
#                 
#                 self.generateRelToPerson("wasBornIn", "Place", self.personDict["Geburtsdaten"]["Ort"])
                
    def generateDeathData(self):
        """Generates TTLData related to Death """
        if "Sterbedaten" in self.personDict:
            if "Datum" in self.personDict["Sterbedaten"]:
                self.createRelToPerson("diedOn", "Date", self.personDict["Sterbedaten"]["Datum"], True, False)
            if "Ort" in self.personDict["Sterbedaten"]:
                self.createRelToPerson("diedIn", "Place", self.personDict["Sterbedaten"]["Ort"], True, True)
    
    def generatePortraitData(self):
        """Generates TTLData related to portrait """
        if "PortraitURL" in self.personDict:
            personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
            personTTLRes.addExtRelation("<http://xmlns.com/foaf/0.1/img>" , "http://pcai042.informatik.uni-leipzig.de/~swp13-wb/" + self.personDict["PortraitURL"])#localhost/~wolfo
    
    def generateRelativesData(self): 
        """Generates TTLData related to relatives """
        if "V" in self.personDict:
            self.createRelToPerson("fatherIs", "RelatedPerson", self.personDict["V"], False, False)
        if "M" in self.personDict:
            self.createRelToPerson("motherIs", "RelatedPerson", self.personDict["M"], False, False)
        if "E" in self.personDict:
            labelE = self.personDict["E"].replace("\n","<br>")
            self.createRelToPerson("wasMarriedTo", "RelatedPerson", labelE, False, False)
        if "G" in self.personDict:
            labelG = self.personDict["G"].replace("\n","<br>")
            self.createRelToPerson("hasSibling", "RelatedPerson", labelG, False, False)
        if "N" in self.personDict:
            labelN = self.personDict["N"].replace("\n","<br>")
            self.createRelToPerson("hasDescendant", "RelatedPerson", labelN, False, False)
    
    def generateLaborData(self):
        """Generates TTLData related to general Labor """
        if "Berufe" in self.personDict:
            if not isinstance(self.personDict["Berufe"], type([])):
                labor = self.personDict["Berufe"].split(", ")
            else:
                labor = self.personDict["Berufe"]
            for oneLabor in labor: 
                self.createRelToPerson("hasGeneralLabor", "GeneralLabor", oneLabor, True, False, True )
    
    def generateAData(self): 
        """Generates TTLData related to Education - A """
        if "A" in self.personDict:
            if isinstance(self.personDict["A"], unicode):
                commentTTL = self.createRelToPerson("hasEducation", "A", self.personDict["A"], False, False)
            elif len(self.personDict["A"]) != 1:
                raise Exception("In 'A' is a Subtitle which is not specified and so deleted.")
            elif self.personDict["A"][0][0] == "yearList":
                #wenn nur eine Fussnote im ersten Feld ist, dann ist das die Fussnote von ganz A
                if re.match("^#footnote\d*#$", self.personDict["A"][0][1][0][0]) and self.personDict["A"][0][1][0][1] == "":
                    footnoteNr = re.search("\d+", self.personDict["A"][0][1][0][0]).group()
                    footnoteText = self.personDict["footnotes"][int(footnoteNr)] 
                    commentTTL = self.createRelToPerson("hasAComment", "AComment", footnoteText, False, False)
                    self.currentFootnote += 1
#                     jetzt den Fussnoteneintrag loeschen 
                    del(self.personDict["A"][0][1][0])
                self.createObjectsFromYearList("hasEducation", "A", self.personDict["A"][0][1])
            #test if "A" has not specified objects
            
    
    def generateBData(self):
        """Generates TTLData related to Life Stations - B """
        if "B" in self.personDict:
            if isinstance(self.personDict["B"], unicode):
                commentTTL = self.createRelToPerson("hasStationOfLife", "B", self.personDict["B"], False, False)
            else:
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
                        self.createObjectsFromYearList("hasStationOfLife", "B", sublist[1])
                    elif u'Au\u00dferdem' in sublist[0]:
                        self.createRelToPersonFromList("hasAlsoImportantInfo", "AlsoImportantInfo", sublist[1].split("\n"))
                    elif u'Ehrungen' in sublist[0]:
    #                     print sublist[1]
                        self.createRelToPerson("hasHonoursAndAwards", "HonoursAndAwards", sublist[1].replace("\n", "<br>"))
                        #@todo: Divide lines in Object. Be carefull with subtitles as: "bennant nach:"
                        if u'(Auswahl' in sublist[0]:
                            self.createRelToPerson("hasHonoursAndAwardsComment", "HonoursAndAwardsComment", sublist[0])
                           #@todo: Muss noch allgemein gemacht werden (URIs)
                    elif u'Andere \u00c4mter:' in sublist[0]:
                        self.createRelToPersonFromList("hasOtherOffices", "OtherOffices", sublist[1].split("\n"))
                    else:
                        print sublist[0]
                        raise Exception(u"There is a Subclass of 'B' which is not in List and because of this deleted.")# + "\n" + sublist[0])
    
    def generateWLData(self):
        """Generates TTLData related to Scientific Career  - WL"""
        if "WL" in self.personDict:
            listWL = self.personDict["WL"].split("\n")
            self.createRelToPersonFromList("hasWL", "WL", listWL)
            
    def generateMGData(self):
        """Generates TTLData related to Memberships - MG"""
        if "MG" in self.personDict:
            self.createRelToPerson("hasMG", "MG", self.personDict["MG"])
            
    def generateGPVData(self):
        """Generates TTLData related to printed publication directories - GPV"""
        if "GPV" in self.personDict:
            for subtitle in self.personDict["GPV"]:
                if subtitle == "general":
                    for element in self.personDict["GPV"]["general"]:
                        self.createRelToPerson("hasGPV", "GPV", element )
                elif subtitle == "Deutschsprachige Publikationen:":
                    for element in self.personDict["GPV"][subtitle]:
                        self.createRelToPerson("hasGermanGPV", "GPVGerman", element )
                elif subtitle == "(Auswahl):":
#                     print self.personDict["GPV"]
                    for element in self.personDict["GPV"][subtitle]:
                        self.createRelToPerson("hasGPV", "GPV", element )
                    self.createRelToPerson("hasGPVComment", "GPVComment", "(Auswahl)")
                else:
                    print subtitle
                    raise Exception("In 'GPV' is a subtitle which is not described and because of this Deleted")
            
            
    def generateWData(self):
        """Generates TTLData related to Scintific Publications - W """
        if "W" in self.personDict:
            for sublist in self.personDict["W"]:
                if sublist == "general":
                    for element in self.personDict["W"]["general"]:
                        self.createRelToPerson("hasW", "W", element, False, False)
                elif "Publikationen in deutscher Sprache" in sublist or "Deutschsprachige Publikationen" in sublist or "<b>Deutsche Arbeiten</b>:" in sublist:
                    #TODO Publikationen in deutscher Sparache hat auch manchmal Jahreszahlen drin
                    self.createRelToPersonFromList("hasWGermanPublication", "WGermanPublication", self.personDict["W"][sublist])
                    
                    if "#footnote" in sublist:
                        newRes = self.createRelToPerson("hasGermanPublicationComment", "GermanPublicationComment", sublist, False, True, False)
#                         print newRes.getTTLCode()
#                         print sublist
#                         if sublist.count("#footnote") != 1:
#                             raise Exception("hier sind zuviele Fussnoten")
#                         footnotePattern = re.search("#footnote\d*#", sublist).group()
#                         footnoteNr = footnotePattern.replace("footnote","").replace("#","")
#                         footnoteText = self.personDict["footnotes"][int(footnoteNr)]                        
#                         self.createRelToPersonFromList("hasGermanPublicationComment", "GermanPublicationComment", footnoteText)
#                         self.currentFootnote += 1
                elif "Russischsprachige Publikationen:" in sublist or "<b>Russische Arbeiten</b>:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.createRelToPersonFromList("hasWRussianPublication", "WRussianPublication", self.personDict["W"][sublist])
                elif "bersetzungen ins Deutsche:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.createRelToPersonFromList("hasWTranslationsToGerman", "WTranslationsToGerman", self.personDict["W"][sublist])
                elif "bersetzungen aus dem Deutschen:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.createRelToPersonFromList("hasWTranslationsFromGerman", "WTranslationsFromGerman", self.personDict["W"][sublist])
                elif "bersetzungen" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.createRelToPersonFromList("hasWTranslations", "WTranslations", self.personDict["W"][sublist])         
                elif "Redaktion von " in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
                    self.createRelToPersonFromList("hasWEditorialOfTranslation", "WEditorialOfTranslation", self.personDict["W"][sublist])         
                elif u"Korrigierte und erg\u00E4nzte Angaben zum GPV:" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
#                     for element in self.personDict["W"][sublist]:
                    self.createRelToPerson("hasWCorrectedAndCompletedInfoOfGPV", "WCorrectedAndCompletedInfoOfGPV", self.personDict["W"][sublist])
                elif u"letzteZeile" in sublist:
                    if "footnote" in sublist:
                        raise Exception("nicht erkannt Fussnote")
#                     for element in self.personDict["W"][sublist]:
                    self.createRelToPerson("hasWInformation", "WInformation", self.personDict["W"][sublist])
                else: 
                    print ("In W wurde diese Ueberschrift nicht erkannt. Bei: " + self.personDict["ID"])
                    print ("Die Ueberschrift lautet: " + sublist)
                    print 
                    
#                     raise Exception("In W wurde diese Ueberschrift nicht erkannt")
                    
    def generateQData(self):
        """Generates TTLData related to Sources - Q """
        if "Q" in self.personDict:
            for element in self.personDict["Q"]:
                self.createRelToPerson("hasQ", "Q", element)
            
    def generateSLData(self):
        """Generates TTLData related to secondary Literature - SL """
        if "SL" in self.personDict:
            for subtitle in self.personDict["SL"]:   
                if "general" in subtitle:
                    for element in self.personDict["SL"][subtitle]:
                        self.createRelToPerson("hasSL", "SL", element)
                elif "(Auswahl" in subtitle:
                    for elementSL in self.personDict["SL"][subtitle]:
                        self.createRelToPerson("hasSL", "SL", elementSL)
                    self.createRelToPerson("hasSLComment", "SLComment", subtitle, False, True)
                elif "footnote" in subtitle:
                    print subtitle
                    raise Exception("There is a footnote in subtitle in SL which is deleted")
                else:
                    print subtitle
                    raise Exception("There is a subtitle in 'SL' which is deleted.\n" + subtitle)
    
    def generatePData(self):
        """Generates TTLData related to known  - P """
        if "P" in self.personDict:
            for element in self.personDict["P"]:
                self.createRelToPerson("hasP", "P", element)
        
#Generic methods
#===============


    def createObjectsFromYearList(self, predicate, type, yearList):
        """
        createObjectsFromYearList => Add year list of objects to self.personTTLSet
        Integrates a list of labels with corresponding Information about the time when it happens.
        
        @param predicate: The property as URI which describes the Connection to the new TTLRessource
        objects
        @param type: The type of the new TTLRessource objects
        @param yearList: A list in this Form [ [<timeInformation>, <labelInformation>], ...]
        Exactly two Elements in sublists!
        @raise Exception: If not exactly two Elements in sublists of yearlist
        """
        def prepareYearValue(yearInformation, yearDict):
            """
            Evaluates the Year information. 
            Year Information are like this: "bis 1899", "vor 1899", "ab 1899", "1899"
            "1899-1900" 
            and all this eventually conntected with ", " like: "1899,1900"
            The method generates a dictionary:
            {begin: [], ended:[], inYear:[]}  with only existing keys.
            (if there is no beginning it is only {ended:[], inYear:[]}
            @param yearInformation: Something like:  "bis 1899", "vor 1899", "ab 1899", "1899" 
            "1899,1900"
            @param yearDict: A Dictionary like this {begin: [], ended:[], inYear:[]}
            it can be an emty Dict to. 
            """
            #             {begin: [], ended:[], inYear:[]}
            yearInformation = yearInformation.split(", ")
            for oneYearInfo in yearInformation:
                prepareCommaSeperatedYearValue(oneYearInfo, yearDict)
            return yearDict
        
        def prepareCommaSeperatedYearValue(yearInformation, yearDict):
            """
            Prepares on Year filter information like "ab" and "ended" and "-"
            insertiton into the dict yearDict with prepareOneYear method
            @param yearInformation: Something like:  "bis 1899", "vor 1899"
            No with "," concatinated Dates.
            @param yearDict: A Dictionary like this {begin: [], ended:[], inYear:[]}
            it can be an emty Dict to. 
            """
            
            if  re.match("^[Aa]b\s",yearInformation[:3]):
                prepareOneYear(yearInformation[3:], "began", yearDict)
            elif re.match("^[Vv]or\s",yearInformation[:4]):
                prepareOneYear(yearInformation[4:], "ended", yearDict)
            elif re.match("[Bb]is\s",yearInformation[:4]):
                prepareOneYear(yearInformation[4:], "ended", yearDict)
            elif yearInformation == "ohne Datum":
                pass         
            elif "-" in yearInformation:
                fromTo = yearInformation.split("-")
                if len(fromTo) != 2:
                    print fromTo
                    print self.personDict["ID"]
                    print "Sonderfall! Ist ein und oder oder drin?"
                else:
                    prepareOneYear(fromTo[0], "began", yearDict)
                    prepareOneYear(fromTo[1], "ended", yearDict)
            else:
                prepareOneYear(yearInformation, "inYear", yearDict)
            
            return yearDict
        
        def prepareOneYear(oneYear, predicate, yearDict):
            """
            inserts a Year into a yearDict
            if the Year has 4 decimal and an optinal footnote it will be appended.
            if there is a "/" both dates for and after "/" will be appended.
            Empty string won't be appended.
            Else there will be a comment on the console it nothing will happen.
            @param oneYear: A Year with propably a footnote like #footnote3#
            @param predicate: the predicate which should be used: "began", "ended" or "inYear" 
             @param yearDict: A Dictionary like this {begin: [], ended:[], inYear:[]}
            it can be an emty Dict to.   
            """
            if re.match("^\d{4}(#footnote\d*#)?$",oneYear):
                if predicate in yearDict:
                    yearDict[predicate].append(oneYear)
                else:
                    yearDict[predicate] = [oneYear]
            elif oneYear == "":
                pass
            elif "/" in oneYear:
                orYears = oneYear.split("/")
                if len(orYears) != 2:
                    print orYears
                    print self.personDict["ID"]
                    print "Sonderfall! Mehrere ','?"
                else:
                    yearDict = prepareOneYear(orYears[0], predicate, yearDict)
                    yearDict = prepareOneYear(orYears[0][:2]+orYears[1], predicate, yearDict)
            else:
                print self.personDict["ID"]
                print ("habe ich noch nicht: " + oneYear)
                    
            return yearDict
      
        for element in yearList:
            if len(element) != 2:
                raise Exception("createObjectsFromYearList method needs exactly two Elements in sublists")
        yearValueList = []
        entryList = []
          
        for element in yearList:
            #split time constructions
#             {begin: [], ended:[], inYear:[]}
            yearInformation = element[0]
            yearDict = {}
            #Wenn nur eine Fussnote beim Jahr steht und im Eintrag nichts ist, gilt die 
            #Fussnote fuer ganz A oder B.
            yearDict = prepareYearValue(yearInformation, yearDict)
            yearValueList.append(yearDict)
            entryList.append(element[1])
        for elementNr in range(len(yearList)):   
#             thing = re.match("^([\d\D]*\sProfessor)\sf\Sr\s([\S\s]+)\san\sder\s([\S\s]+)$", entryList[elementNr])
#             thing = re.match("^(Dekan)\sder\s([\S\s]+)\sder\s([\S\s]+)$", entryList[elementNr])
#             thing = re.match("^(Studium)\sder\s([\S\s]+)\san\sder\s([\S\s]+)$", entryList[elementNr])
#             thing = re.match("^(Habilitation)\san\sder\s([\S\s]+)$", entryList[elementNr])
#             thing = re.match("^(Habilitation)\sin\s([\S\s]+)$", entryList[elementNr])
#             thing = re.match("^(Promotion)\szum\s([\S\s]+)\sin\s([\S\s]+)$", entryList[elementNr])
#             if thing:
#                 print(thing.groups())
            #Creation of the new Object with Relation to a Person
            if yearValueList[elementNr]:
                textTTLRes = self.createRelToPerson(predicate, type, entryList[elementNr], False, False, True)
            # if there are no Yearinformation the Ressource is only a literal
            else:
                textTTLRes = self.createRelToPerson(predicate, type, entryList[elementNr], False, False, False)
            #here the Year Information is connected
            if "inYear" in yearValueList[elementNr]:
                for oneYear in yearValueList[elementNr]["inYear"]:
                    #The year element is a unique Ressource. Every 1899 is the same. 
                    self.createRelToRes(textTTLRes, "inYear", "Year", oneYear, True, True, True)
            if "began" in yearValueList[elementNr]:
                for oneYear in yearValueList[elementNr]["began"]: 
                    self.createRelToRes(textTTLRes, "began", "Year", oneYear, True, True, True)
            if "ended" in yearValueList[elementNr]:
                for oneYear in yearValueList[elementNr]["ended"]: 
                    self.createRelToRes(textTTLRes, "ended", "Year", oneYear, True, True, True)
    
    
    def createRelToPersonFromList(self, predicate, type, labelList, independentRes=False, clearFootnotes=False, haveToBeRes=False):
        """
        Creates a new ressources out of a list of labels in connection to the TTLRessource of the 
        person which is generated.
        
        @param predicate: The URI of the relation between the existing Ressource and the new one.
        @param type: The URI of the type of the new object.
        @param labelList: A list of labels, which all shall be new Ressources. 
        List of String or tuple with country code like:
        ("hallo", "de") will be "hallo"@de
        @param independentRes: Determines that the new Ressource have a general URI, propably the Ressource 
        allready exists, then the new Information will be append to the existing one.
        If "False" the Ressource will be unique with the persons ID in URI.
        @param clearFootnotes: The Footnotes will not be seen any more in the Label if True
        If False: #footnote2# will be [1]
        @param haveToBeRes: If False, if it is not needed, the Information will only be added as a literal.
        If there are any Footnotes, or Year Connections it will be nevertheless a Ressource
        """
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        for oneLabel in labelList:
            newTTLRes = self.createRelToRes(personTTLRes, predicate, type, oneLabel,independentRes, clearFootnotes, haveToBeRes)
              
          
    def createRelToPerson(self, predicate, type, label, independentRes=False, clearFootnotes=False, haveToBeRes=False):
        """
        Creates a new ressource in connection to the TTLRessource of the person which is generated.
        
        @param predicate: The URI of the relation between the existing Ressource and the new one.
        @param type: The URI of the type of the new object.
        @param label: The label of the new Object. String or tuple with country code like:
        ("hallo", "de") will be "hallo"@de
        @param independentRes: Determines that the new Ressource have a general URI, propably the Ressource 
        allready exists, then the new Information will be append to the existing one.
        If "False" the Ressource will be unique with the persons ID in URI.
        @param clearFootnotes: The Footnotes will not be seen any more in the Label if True
        If False: #footnote2# will be [1]
        @param haveToBeRes: If False, if it is not needed, the Information will only be added as a literal.
        If there are any Footnotes, or Year Connections it will be nevertheless a Ressource
        """
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        newTTLRes = self.createRelToRes(personTTLRes, predicate, type, label,independentRes, clearFootnotes, haveToBeRes)

        return newTTLRes
        
    def createRelToRes(self, existingTTLRes, predicate, type, label, independentRes=False, clearFootnotes=False, haveToBeRes=False):
        """
        Creates a new ressource in connection to an existing Ressource.
        If #footnote<int># in label a comment will be added as Ressource
        If a Internet Link with http:// in String a homepage Ressource will be added.
        If #internNameLink#<5 x int>#endNameNr#<Name>#/internNameLink# in Text,
        A connection to a Person Ressource will be added. If the Person not in TTLSet as 
        TTLRessource, the PErson will be added (without label) 
        
        @param existingTTLRes: The existing TTL Ressource where the new Information should be added.
        @param predicate: The URI of the relation between the existing Ressource and the new one.
        @param type: The URI of the type of the new object.
        @param label: The label of the new Object. String or tuple with country code like:
        ("hallo", "de") will be "hallo"@de
        @param independentRes: Determines that the new Ressource have a general URI, propably the Ressource 
        allready exists, then the new Information will be append to the existing one.
        If "False" the Ressource will be unique with the persons ID in URI.
        @param clearFootnotes: The Footnotes will not be seen any more in the Label if True
        If False: #footnote2# will be [1]
        @param haveToBeRes: If False, if it is not needed, the Information will only be added as a literal.
        If there are any Footnotes, or Year Connections it will be nevertheless a Ressource 
         
        """
        haveToBeRes = True
        if isinstance(label, tuple):
            labelCountryCode = label[1]
            label = label[0]
        else:
            label = label
            labelCountryCode = False
        oldlabel = label
        personTTLRes = self.personTTLSet.getRessourcePerson(self.personDict["ID"])
        #Fussnoten erzeugen
        footnoteTTLs, label = self.createFootnotes(label, clearFootnotes)
        #Vebundene Personen erzeugen
        connectedPersonTTLs, label = self.createConPersons(label)
        connectedLinks, label = self.createLinks(label)
        #URI bestimmen
        if independentRes:
            newTTLURI = type + "/" + createASCIIString(label)
#             print newTTLURI
        else:
            number = 1
            newTTLURI = type + "/" + self.personDict["ID"] + predicate + str(number)
            while self.personTTLSet.isRessourceIn("<" + newTTLURI + ">"):
                number += 1
                newTTLURI = type + "/" + self.personDict["ID"] + predicate + str(number)
        #Neue Ressource erzeugen
#         if True:
        if oldlabel != label or haveToBeRes:
            newTTLRes = TTLRessource(newTTLURI, "drw-model:" + type, False)
            newTTLRes.addPropLabel(label, labelCountryCode)
            #When links where in Label, they will now be added to the Ressource
            if connectedLinks:
                for linkDate in connectedLinks:
                    newTTLRes.addExtLiteral("<http://xmlns.com/foaf/0.1/homepage>", linkDate[0])
                    if linkDate[1] != "":
                        newTTLRes.addPropData("drw-model:hasDate", linkDate[1])
    #                 print newTTLRes.getTTLCode()
            #Fussnoten verknuepfen
            self.connectFootnotes([personTTLRes, newTTLRes], footnoteTTLs)
            #Neu erzeugte verbundene Personen verknuepfen
            self.connectPersons(newTTLRes, connectedPersonTTLs)
            
            existingTTLRes.addPropObj("drw-model:" + predicate, newTTLRes.getURI())
            
            self.personTTLSet.addRessource(newTTLRes)
            
            return newTTLRes
        else:
            existingTTLRes.addPropData("drw-model:" + predicate, label)
 

    
    def createFootnotes(self, label, clearFootnotes=False):
        """
        Creates a new comment as TTLRessource if #footnote<int># in label.
        There no connection to a Ressource. The Connection should be Created with
        self.connectFootnotes afterwards. 
        @param label: The String of an Label which have propably an #footnote<int># inside
        @param clearFootnotes: If True any reference to the comment inside the label will be deleted
        False: there will be a Reference in the new label like: #footnote3# => [3] 
        @return: FootnotesAs TTL and cleared label
        """
        oldlabel = label
        footnoteTTLs = []
        regSearchString = "#footnote\d*#"

#         print(label)
        while re.search(regSearchString, label):
            reFootnote = re.search(regSearchString, label)
            footnoteNr = reFootnote.group().replace("#footnote", "").replace("#", "")
            commentLabel = self.personDict["footnotes"][int(footnoteNr)]
            if clearFootnotes:
                label = label.replace(reFootnote.group(), "" )
            else: 
                label = label.replace(reFootnote.group(), "[" + footnoteNr + "]" )
            connectedLinks, commentLabel = self.createLinks(commentLabel)
            connectedPersonTTLs, commentLabel = self.createConPersons(commentLabel)
            commentURI = "Comment/" + self.personDict["ID"] + "_" + footnoteNr
            newCommentTTLRes = TTLRessource(commentURI, "drw-model:Comment" , False)
            # Connect person to comment who where mentioned in comment label.
            if connectedPersonTTLs:
                self.connectPersons(newCommentTTLRes, connectedPersonTTLs)
            #adds links in comment          
            if connectedLinks:
                for linkDate in connectedLinks:
                    newCommentTTLRes.addExtRelation("<http://xmlns.com/foaf/0.1/homepage>", linkDate[0])
                    if linkDate[1] != "":
                        newCommentTTLRes.addPropData("drw-model:hasDate", linkDate[1])
            
             #LAbel hinzufuegen
            
            newCommentTTLRes.addPropLabel(commentLabel)
            self.personTTLSet.addRessource(newCommentTTLRes)
#             print newCommentTTLRes.getTTLCode()
            footnoteTTLs.append(newCommentTTLRes)
            self.currentFootnote += 1
#         if oldlabel != label:
#             print oldlabel
#             print label
        return footnoteTTLs, label
    
    
    
    def connectFootnotes(self,ttlList, footnoteTTLs):
        """
        connect all footnoteTTLS to all Ressources in ttlList.
        @param ttlList: List of TTLRessource object which have a connection to a comment.
        @param footnoteTTLs: The comment TTLRessource objects.
        """
        for oneFootnote in footnoteTTLs:
            for oneTTLRes in ttlList:
                oneTTLRes.addPropObj("drw-model:hasComment", oneFootnote.getURI())
                
    
    
    def createLinks(self, label):
        """
        Adjust the label and replaces the link with "Online Ressource". 
        @param label: The String of an Label which have propably an #footnote<int># inside
        @return: list of tuples (clearedLabel, date), string of cleared label 
        """
        connectedLinks = []
        while re.search("(http://[\S]+)\s", label):
            link = re.search("(http://[\S]+)\s", label).group().strip()
            if link[-1:] == ",":
                link = link[:-1]
    #        Wenn der Link am Ende steht wird er ganz aus dem Label entfernt.
            linkWithDate = re.search("(\(?http://[\S]+)\s\(?\d+\.\d+\.\d+\)?\.\s*", label)
            if linkWithDate:
                linkWithDate = linkWithDate.group()
                date =re.search("\d+\.\d+\.\d+", linkWithDate).group()
                if "(" not in linkWithDate and ")" in linkWithDate:
                    label = label.replace(linkWithDate, "") + "Online Ressource)."
                else:
                    label = label.replace(linkWithDate, "").strip() + " (Online Ressource)."
                connectedLinks.append((link,date))
            else:
                label = label.replace(link, "Online Ressource")
                connectedLinks.append((link,""))    
            
        return connectedLinks, label

    def createConPersons(self, label):
        """
        Creates new Persons for all #internNameLink#\d+#endNameNr#[\D]*#/internNameLink#" found in
        a label.
        @param label: The label with potentialy a namelink inside.
        Name link is formed like this:"#internNameLink#\d+#endNameNr#[^#]*#/internNameLink#"
        @return: The TTLRessource objects of the connected Persons as List, new label  
        """ 
        newPersonTTLs = []
        regSearchString = "#internNameLink#\d+#endNameNr#[^#]*#/internNameLink#"
        while re.search(regSearchString, label):
             reNameLink = re.search(regSearchString, label)
             oldNameLink = reNameLink.group()
             linkedPersonNr = re.search("\d{5}",oldNameLink).group()
             nameLink = copy(oldNameLink)
             nameLink = nameLink.replace("#internNameLink#", "")
             nameLink = nameLink.replace("#/internNameLink#", "")
             name = nameLink.replace(linkedPersonNr + "#endNameNr#", "")
             del(nameLink)
             personURI = "ImportantPerson/" + linkedPersonNr
             newPersonTTLRes = TTLRessource( personURI,"drw-model:ImportantPerson", False)
             self.personTTLSet.addRessource(newPersonTTLRes)
             newPersonTTLs.append(newPersonTTLRes)
             
             label = label.replace(oldNameLink, '#name#' + name + "#/name#" )
             
        return newPersonTTLs, label
    
    def connectPersons(self, ttlResToConnect, connectedPersonTTLs):
        """
        Sets Connections from TTLRessource Object to a List of TTLREssource object
        @param ttlResToConnect: The TTLRessource which should be connected to the other 
        Ressources
        @param connectedPersonTTLs: The TTLRessource objects of the Ressources who are 
        connected to the first TTLRessource 
        """
        for onePersonTTL in connectedPersonTTLs:
            ttlResToConnect.addPropObj("drw-model:hasNameLink", onePersonTTL.getURI())

            
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
        
       

def generateTTLFromDRWPickles():
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
            personDict = openPickle(os.getcwd()+"/pickleFromDRW", element)       
            personConverter = PersonConverter(personDict)
            personConverter.generateTTL()
            newTTLSet = personConverter.getTTLSet()#auskommentieren
            allTTLs.combine(newTTLSet)
            ttlString = personConverter.getStrOfTTLSet()
            ttlString = italicHTML(ttlString)
#             structureAsText = print_what_it_is(personDict, True)
#          print structureAsText
            save(ttlString, os.getcwd() + "/ttlFiles", element , ".ttl")
    ttlString = allTTLs.getTTLCode()
    ttlString = italicHTML(ttlString)
    save(ttlString, os.getcwd(), "TTLResPart1" , ".ttl")


def generateTTLFromHTML():
    """test method"""
    pfadZuPickles = os.getcwd() + "/pickleFromHTML"
    filesInFolder = os.listdir(pfadZuPickles)
    filesInFolder = [file for file in filesInFolder if ".pickle" in file]

    allTTLs = TTLSet()
    allTTLs.addBase("http://drw-catalog.saw-leipzig.de/")  
    for element in filesInFolder:
#         if element == "30749.pickle":    
        if True:
            personDict = openPickle(os.getcwd()+"/pickleFromHTML", element)
            #Vorbereiten: 
            if "GPV" in personDict:
                if isinstance(personDict["GPV"], unicode):
                    newList = personDict["GPV"]
                    del(personDict["GPV"])
                    newList = newList.strip().split('\n')
                    personDict["GPV"] = {"general":newList}                    

            if "portraitURL" in personDict:
                personDict["PortraitURL"] = personDict["portraitURL"]
                del(personDict["portraitURL"]) 
#             if "A" in personDict:
#                 if "endNameNr" in personDict["A"]:
#                     print "juhuu"
#                 pprint(personDict["A"]["general"][0])
#             if personDict["ID"] == "30264":
#                 pprint(personDict["GPV"])
#             if "MG" in personDict:
#                 if not "\n" in personDict["MG"] and "," in personDict["MG"]:
#                     dings = personDict["MG"].split(",")
#                     for dangs in dings:
#                         print dangs
#                 pprint(personDict["MG"])
            personConverter = PersonConverter(personDict)
            personConverter.generateTTL()
            newTTLSet = personConverter.getTTLSet()#auskommentieren
            allTTLs.combine(newTTLSet)
            ttlString = personConverter.getStrOfTTLSet()
            ttlString = italicHTML(ttlString)
#             structureAsText = print_what_it_is(personDict, True)
#          print structureAsText
            save(ttlString, os.getcwd() + "/ttlFilesHTML", element , ".ttl")
    ttlString = allTTLs.getTTLCode()
    ttlString = italicHTML(ttlString)
    save(ttlString, os.getcwd(), "TTLResPart2" , ".ttl")
    
    
def main(argv):
    """Main method"""
    generateTTLFromHTML()
    generateTTLFromDRWPickles()


if __name__ == "__main__":
    main(sys.argv[1:])
    
 