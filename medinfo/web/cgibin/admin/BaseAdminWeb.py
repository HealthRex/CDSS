#!/usr/bin/env python
"""Base class for supplement page web interface modules"""
import cgi

from medinfo.web.cgibin.BaseWeb import BaseWeb
from medinfo.web.cgibin import Links;

class BaseAdminWeb(BaseWeb):
    """Just add common header links for admin pages"""

    def __init__(self):
        """Constructor.  Just some initializations such as
        addition of default mTemplateDict values.  Be sure the
        subclasses call this method in their own __init__!
        """
        BaseWeb.__init__(self);

        self.mTemplateDict["BASE_LINK_DIR"]         = "../" + Links.BASE_LINK_DIR;
        self.mTemplateDict["HEADER_LINKS"]          = Links.ADMIN_HEADER_LINKS;
        self.mTemplateDict["NAV_LINKS"]             = Links.ADMIN_NAV_LINKS;
        self.mTemplateDict["FOOTER_LINKS"]          = Links.ADMIN_FOOTER_LINKS;
    
if __name__ == "__main__":
    webController =  BaseAdminWeb()
    webController.handleRequest(cgi.FieldStorage())
