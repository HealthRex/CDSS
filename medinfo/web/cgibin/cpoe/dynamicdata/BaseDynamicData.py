#!/usr/bin/env python
import sys, os;
import cgi

import medinfo.web.cgibin.cpoe.dynamicdata;
from medinfo.web.cgibin.cpoe.BaseCPOEWeb import BaseCPOEWeb;

class BaseDynamicData(BaseCPOEWeb):
    def __init__(self):
        # Super-class init should setup lots of common drop-list data
        BaseCPOEWeb.__init__(self);

    def defaultTemplateFilename(self):
        """Dynamic data pages may be called from other scripts in other directories,
        so make sure the reference to the template files are by absolute reference.
        """
        directory = os.path.dirname(medinfo.web.cgibin.cpoe.dynamicdata.__file__);
        
        return os.path.join( directory, BaseCPOEWeb.defaultTemplateFilename(self) );
