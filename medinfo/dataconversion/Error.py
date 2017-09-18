class Error(Exception):
    pass

class StringFormatError(Error):

    def __init__(self, expression):
        print "Invalid string format: " + expression;

class TaxonomyCodeError(Error):
    def __init__(self, codeType):
        print "Unrecognized code type: " + codeType
