import docx
import csv
import re
import os
from medinfo.dataconversion.Taxonomy import *

FILE_PREFIX = "medinfo/dataconversion/taxonomyData/"

class TaxonomyReader():

    def __init__(self):
        self.taxonomyMap = dict()
        self.taxonomyNames = self.listTaxonomyNames()

    def listTaxonomyNames(self):
        names = list()
        filename = FILE_PREFIX + "taxonomyNames.txt"
        f = open(filename, 'r')
        pattern = re.compile(r'(.+) \(imported\)')
        for line in f:
            name = str.upper(re.findall(pattern, line)[0])
            names.append(name)
        f.close()
        return names

    def createTaxonomyMapping(self):
        """ Parses docx file for each Taxonomy and
            creates a Taxonomy object from parsed data.
        """
        for filename in os.listdir(FILE_PREFIX):
            if filename.endswith(".docx"):
                for name in self.taxonomyNames:
                    if name in str.upper(filename):
                        newTaxonomyName = name
                        if name == "HIGH RISK":
                            continue
                        if name == "HEPATITIS C":
                            newTaxonomyName = "HEPATITIS C INFECTION"
                            if "POSITIVE" in filename:
                                newTaxonomyName = "HEPATITIS C POSITIVE"
                        newTaxonomy = Taxonomy(newTaxonomyName)

                        # Parse docx file for new taxonomy and
                        # add code ranges to Taxonomy object.
                        doc = docx.Document(FILE_PREFIX + filename)
                        for para in doc.paragraphs:
                            line = para.text
                            pattern = re.compile(r'%s,(\w+),(.+)' % newTaxonomyName)
                            match = re.findall(pattern, line)
                            if match:
                                codeType = match[0][0]
                                values = str.split(str(match[0][1]),',')
                                newTaxonomy.addCodeRange(values, codeType)
                        self.taxonomyMap[newTaxonomyName] = newTaxonomy
                        break

        return self.taxonomyMap


    def printMapping(self):
        pass

if __name__=="__main__":
    tr = TaxonomyReader();
    taxonomyMap = tr.createTaxonomyMapping();
    #tr.printMapping();
