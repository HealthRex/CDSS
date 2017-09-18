from medinfo.dataconversion.Error import *

class Taxonomy():
    def __init__(self, name):
        self.name = name
        self.ICD9Codes = list()
        self.ICPCodes = list()
        self.CPTCodes = list()
        self.ICD9Ranges = list()
        self.ICPRanges = list()
        self.CPTRanges = list()

    def addCodeRange(self, codes, codeType):
        if "range" in codeType:
            if codeType == "ICD_range":
                self.ICD9Ranges.append(codes)
            if codeType == "ICP_range":
                self.ICPRanges.append(codes)
            if codeType == "CPT_range":
                self.CPTRanges.append(codes)
        elif codeType == "ICD":
            self.ICD9Codes += codes
        elif codeType in ["ICP"]:
            self.ICPCodes += codes
        elif codeType == "CPT":
            self.CPTCodes += codes


    def printCodes(self):
        print '\n' + self.name
        print "ICD9Codes: "
        print self.ICD9Codes
        print "ICPCodes: "
        print self.ICPCodes
        print "CPTCodes: "
        print self.CPTCodes
