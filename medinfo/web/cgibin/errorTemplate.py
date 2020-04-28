#!/usr/bin/env python
"""
Simple Python CGI script to relay error message to users in a more pleasing format.
"""

from io import StringIO
import cgi
import cgitb; cgitb.enable()

from .BaseWeb import BaseWeb

class errorTemplate(BaseWeb):
    def __init__(self):
        BaseWeb.__init__(self)

        # Default values to place in template htm file
        self.requestData["errorMsg"]    = ""
        self.requestData["emailErrors"] = ""


    def action_default(self):
        pass;

if __name__ == "__main__":
    webController =  errorTemplate()
    webController.handleRequest(cgi.FieldStorage())
