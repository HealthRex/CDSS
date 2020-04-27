#!/usr/bin/env python
"""Base class for web interface modules.

Check out the Python topic guides on Web and CGI scripting for introductions
http://wiki.python.org/moin/CgiScripts

The following is a quick primer that covers some of the basic concepts
used in this framework, particularly the use of the Python templating system.
http://gnosis.cx/publish/programming/feature_5min_python.html

Refactored in wsgiHandler to mostly use same basic CGI infrastructure while taking advantage of WSGI efficiency

"""
import sys, os;
import logging;
import cgi
from . import Options
from . import Links
from . import Env
import urllib.request, urllib.parse, urllib.error;
import smtplib;
import string;
from io import StringIO;
from time import time;

from medinfo.common.Const import NULL_TAG;

class BaseWeb:
    """Common base class for web interface modules to supply some standard setup,
    parameter extraction, file upload processing methods, etc.
    """
    """Standard suffix expected for corresponding web templates""" 
    TEMPLATE_SUFFIX = ".htm"

    """Format string for option tags"""
    OPTION_TAG = '<option value="%(value)s"%(selected)s>%(text)s</option>'
    SELECT_FIELD_SUFFIX = "Select"
    OPTIONS_FIELD_SUFFIX = "Options"
    
    filePath            = None;
    mHandlers           = None
    mForm               = None
    mTemplateDict       = None
    mTemplateFilename   = None
    requestData = None; # Synonym for mTemplateDict, trying to phase out that long name
    req = None; # For mod_python calls, can get handle on request object directly
    
    disableResponse = (not Env.CGI_TEXT_RESPONSE);
    wsgiResponse = False;
    
    def __init__(self):
        """Constructor.  Some initializations such as
        addition of default mTemplateDict values and
        command handlers (e.g. File uploads).  Be sure the
        subclasses call this method in their own __init__!
        """
        self.filePath = None;   # Need explicitly referenced filePath for WSGI support
        
        self.clearHandlers()

        # Contains all of the name / value pairs that
        # are to be mapped into the template file
        self.requestData = {}
        self.requestData["NULL_TAG"]          = NULL_TAG;
        self.requestData["WEB_CLASS"]         = self.__class__.__name__
        self.requestData["BASE_LINK_DIR"]     = Links.BASE_LINK_DIR;
        self.requestData["HEADER_LINKS"]      = Links.HEADER_LINKS;
        self.requestData["NAV_LINKS"]         = Links.NAV_LINKS;
        self.requestData["FOOTER_LINKS"]      = Links.FOOTER_LINKS;
        self.requestData["ERROR_TEMPLATE"]    = os.path.join(Env.WEB_DIR, "cgibin/errorTemplate.htm");
        self.requestData["ERROR_EMAIL_TEMPLATE"] = os.path.join(Env.WEB_DIR, "resource/errorReport.eml");
        self.requestData["ERROR_EMAIL"]       = Env.ERROR_EMAIL;
        self.requestData["TRACKING_SCRIPT"]  = self.buildTrackingScript();
        self.requestData["timer"] = "...";
        self.mTemplateDict = self.requestData;  # Synonyms, trying to phase out mTemplateDict usage
    
    def addHandler( self, commandName, methodName ):
        """Tells this controller class to look for requests
        that include a form field named 'commandName.'
        If found, the handleRequest method will invoke the
        method named 'methodName' on this instance.
        
        >>> web = ExampleWeb()
        >>> web.addHandler("submit",ExampleWeb.doSubmit.__name__)
        """
        self.mHandlers.append( (commandName,methodName) )
    
    def clearHandlers( self ):
        """Clear any previously added handlers.  Mostly pointless,
        except when caller wishes to clear the default handlers.
        """
        self.mHandlers = []
    
    def handleRequest( self, form=None, req=None ):
        """Primary execution method, finds an appropriate command
        method to execute based on the contents of the form
        which is an instance of cgi.FieldStorage.  Normal case is
        to just call this method as below, letting the cgi module
        take care of all of the parameter parsing and construction.
        
        >>> web.handleRequest( cgi.FieldStorage() )
        
        If no form parameter is given, will default to cgi.FieldStorage()
        
        For mod_python based calls, can add additional request object parameter,
        useful for reporting additional debug information.
        
        Note:  With the given structure, it is possible for a
        single form request to invoke multiple command methods,
        the form just has to contain the commandName field
        for multiple recognized handlers.  The order that
        these are executed will depend on the order in which
        the command handlers were added via the addHandler method.
        """

        if req is not None and "envOptionsCopied" not in os.environ:
            # First time a request is made, and a request object available
            #   must be a mod_python script.  Copy over PythonOption
            #   request directives as environment variables
            for key, value in req.get_options().items():
                os.environ[key] = value;
            os.environ["envOptionsCopied"] = "True";

        if Env.LOGGER_LEVEL == logging.DEBUG:
            # Allow raised exceptions and let cgitb print the stack trace.
            self.__handleRequest(form, req);
        else:
            # Catch exceptions for more graceful error reporting
            try:
                self.__handleRequest(form, req);
            except Exception as exc:
                self.errorResponse(exc);


    def __handleRequest( self, form=None, req=None ):
        """Private version that does most of the work.
        Separate as, depending on logger level, may or may not
        want to print out full error stack trace.
        """
        self.mForm = form
        if self.mForm == None: self.mForm = cgi.FieldStorage()
        self.req = req;
        
        self.maintainParams()

        timer = time(); # Track how long the request processing takes
        self.action_initial();
        for (commandName, methodName) in self.mHandlers:
            if commandName in form and self.requestData[commandName] != "":
                # Use reflection to get a handle on the named method to execute
                commandMethod = getattr(self,methodName)
                commandMethod()
        self.action_final();
        timer = time() - timer;
        self.requestData["timer"] = "(%1.3f sec)" % timer;

        self.response()

    def setFilePath(self, fileObj):
        self.filePath = os.path.dirname(fileObj)

    def wsgiHandler(self, environ, start_response):                    
        """WSGI alternative handler to manage basic CGI requests"""
        self.wsgiResponse = True;

        # Create a web controller instance to copy to ensure thread-safety of web controller attributes
        #   even if multiple users using web server simultaneously
        handlerInstance = self.__class__();
        
        #Set Template Filename
        handlerInstance.setTemplateFilename( os.path.join(self.filePath, self.__class__.__name__ + self.TEMPLATE_SUFFIX) );
        handlerInstance.handleRequest(cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=1))
        
        #Assign output/headers        
        output = handlerInstance.populatedTemplate()        
        response_headers = handlerInstance.returnHeaders(output) 
        status = '200 OK'
        start_response(status, response_headers);
        
        #Examples of printing errors
        #print >> environ['wsgi.errors'], "application debug #2"
        #This one seems to work
        # print("application debug #3", file=sys.stderr)

        del handlerInstance;    # Ensure garbage collection
        
        return [output]
    
    def maintainParams(self):
        """Normal behavior, store all request parameters
        back into the templateDict for maintenance across page views.
        Exception is file parameters.  Don't want to store "value"
        because that would be entire file contents.  Instead,
        maintain the "filename" attribute.
        
        Another exception is select boxes (drop lists).  Name of
        parameter passed in is different than the option tag
        text that must be output to represent that selection.
        """
        self.initializeRequestData();

        if len(self.mForm) > 0:
            self.manualResetParams();
        
        for key in list(self.mForm.keys()):
            field = self.mForm[key]
            if isinstance(field,list):  # Multi-Items 
                selectedValues   = [];
                selectedValueSet = set();  # For faster lookup
                for subfield in field:
                    value = subfield.value;
                    value = self.replaceWhitespace(value);
                    if value == NULL_TAG: value = None;
                    selectedValues.append(value);
                    selectedValueSet.add(value)
                if key.endswith(self.SELECT_FIELD_SUFFIX):  # Multi-select list specifically
                    optionKey = key[0:-len(self.SELECT_FIELD_SUFFIX)] + self.OPTIONS_FIELD_SUFFIX
                    self.requestData[optionKey] = self.optionTagsFromList(Options.FIELD2VALUE[key],Options.FIELD2TEXT[key],selectedValueSet)
                self.requestData[key] = []
                self.requestData[key].extend(selectedValues)
            else:
                value = field.value;
                value = self.replaceWhitespace(value);
                if value == NULL_TAG: value = None;
                if key.endswith(self.SELECT_FIELD_SUFFIX):    # Drop list
                    optionKey = key[0:-len(self.SELECT_FIELD_SUFFIX)] + self.OPTIONS_FIELD_SUFFIX
                    self.requestData[optionKey] = self.optionTagsFromList(Options.FIELD2VALUE[key],Options.FIELD2TEXT[key],field.value)
                    self.requestData[key] = value
                elif field.filename != None:  # File field, just store the filename
                    self.requestData[key] = field.filename
                else:
                    self.requestData[key] = value

    def initializeRequestData(self):
        """Called just as maintainParams beings, allowing sub-classes to override
        for any initialization of the request data first.  Normally this can all
        be done in the controller sub-classes' actual __init__ method, but for
        mod_python calls, the req object is not yet available then, so provide
        another opportunity to intervene here.
        """
        pass;

    def manualResetParams(self):
        """Called just as maintainParams begins.  Sub-classes can override this
        method if they need to manually reset any parameter values before letting 
        them be set / maintained.  Will probably just look like a series of lines like:
        
           self.requestData["myParam"] = "";
        
        Does not make much sense why this should be necessary since maintainParams
        will overwrite these blank values anyway.  The problem is, certain form
        elements will not be submitted at all (unchecked checkboxes and blank text
        fields in PSP files), so the maintainParams method will skip right past
        those unaware.  To ensure those are effectively counted as "blanks", set the
        blank values here, then any non-blank values will overwrite them in maintainParams
        if they exist.
        """
        pass;

    def errorResponse( self, exc ):
        """If an Exception (exc) was thrown during the request handling process,
        respond to the client with this method instead of the standard response method.
        """
        self.setTemplateFilename(self.requestData["ERROR_TEMPLATE"]);
        self.requestData["errorType"]= str(type(exc));
        self.requestData["errorMsg"] = str(exc);
        
        if self.requestData["ERROR_EMAIL"] is not None:
            msg = StringIO();
            msgTemplate = open( self.requestData["ERROR_EMAIL_TEMPLATE"] );
            msg.write(msgTemplate.read() % self.requestData);

            # Add all the CGI debug information to the e-mail
            origStdout = sys.stdout;
            sys.stdout = msg;
            cgi.print_exception(exc);
            cgi.print_arguments();

            cgi.print_form(self.mForm);

            if self.req is None:
                # Looks like a direct CGI request, pull out information from environment then
                cgi.print_environ();
            else:
                # Looks like mod_python or other call, with request object included.  Derive environment from there
                print("<h3>Request Sub-Process Environment</h3>", file=sys.stdout)
                print("<ul>", file=sys.stdout)
                self.req.add_common_vars();
                for key, value in self.req.subprocess_env.items():
                    print("<li>%s: %s</li>" % (key, value), file=sys.stdout)
                print("</ul>", file=sys.stdout)

            sys.stdout = origStdout;

            server = smtplib.SMTP(Env.SMTP_HOST);
            errors = server.sendmail(Env.CDB_EMAIL,self.requestData["ERROR_EMAIL"],msg.getvalue());
            self.requestData["emailErrors"] = str(errors);
            server.quit();
        else:
            self.requestData["emailErrors"] = "No notification e-mail sent";
        
        if not self.disableResponse:
            # CGI Text Response Basics
            self.printTemplate();
        elif self.req is not None:
            # Mod Python call
            self.req.write("<pre>")
            self.req.write("<h3>ChemDB / System Error</h3>")
            self.req.write("""We apologize for the following system error. If the problem persists, please contact <a href="mailto:%(errorEmail)s">%(errorEmail)s</a>.<br><br>""" % {"errorEmail":Env.ERROR_EMAIL} )
            self.req.write("<font color=red>")
            self.req.write(str(exc)) # write the error at the top of the current page 
            self.req.write("</font></pre>")
            # Propagate exception up so regular error processing can be done
            # raise exc;
        # elif self.wsgiResponse:
            # Output method for WSGI handled calls
            # Don't have to do anything, since template output will be the same process

    def action_initial(self):
        """Action command method that will always be called at the beginning of a handleRequest
        call, regardless of whether any form fields have been submitted.
        Sub-classes can override this to achieve default behavior.
        
        This is different than just adding something to the __init__ function, because
        this will happen after things like maintainParams are called to load any
        form data into the requestData first, rather than relying on default values.
        """
        pass;
        
    def action_final(self):
        """Action command method that will always be called at the end of a handleRequest
        call, regardless of whether any form fields have been submitted.
        Sub-classes can override this to achieve default behavior.
        """
        pass;
    
    def requestEnvironment(self):
        """Return a reference to the request environment dictionary.
        Wrap in this method because the access is method is different
        depending on whether this is a CGI or PSP call.
        """
        if self.req is None:
            # Looks like a plain CGI call
            return os.environ;
        else:
            # Looks like a PSP call
            self.req.add_common_vars();
            return self.req.subprocess_env;

    def getCookies(self, cookieClass=None, secret=None):
        """Return a reference to the request cookies dictionary.
        Wrap in this method because the access is method is different
        depending on whether this is a CGI or PSP call.
        """
        cookieDict = None;
        if self.req is not None:
            # PSP call
            import mod_python.Cookie;
            if cookieClass == "signed" and secret is not None: 
                #Signed Cookie
                cookieDict = mod_python.Cookie.get_cookies(self.req, mod_python.Cookie.SignedCookie, secret=secret);        
            else:
                #Non-signed, regular, less secure, user modifiable cookies
                cookieDict = mod_python.Cookie.get_cookies(self.req);
        else:
            # Assume is a CGI call
            import http.cookies;
            cookieDict = http.cookies.SimpleCookie();
            if "HTTP_COOKIE" in os.environ:                
                cookieDict.load(os.environ["HTTP_COOKIE"]);
                
                #Set all default attributes, because they were all lost
                #Actually this does not have the desired affect, all cookies should be set to root path, but they are not.
                #Leaving it in here, perhaps some servers/clients support this 
                for cookieName in cookieDict:
                    cookie = cookieDict[cookieName]
                    cookie.path = '/'        
        return cookieDict;

    def addCookie(self, key, value, cookieClass=None, secret=None, cookieAttributes=[]):
        """Simplest case of adding a name-value pair cookie for session persistence.
        """
        if self.req is not None:
            # PSP call
            import mod_python.Cookie;
            # Check to see if this should be a signed cookie, or a regular cookie
            cookie = mod_python.Cookie.Cookie(key, value);
            
            #Go through and assign all cookie attributes, I know this is cool right?  Variable vaiables!
            for attribute in cookieAttributes:
                if isinstance(attribute['value'], int):                    
                    exec("cookie.%s = %s" % (attribute['name'], attribute['value']))
                else:
                    exec("cookie.%s = '%s'" % (attribute['name'], attribute['value']))
            
            #Add cookie to header
            mod_python.Cookie.add_cookie(self.req, cookie);
        else:
            # Assume is a CGI call
            import http.cookies
            if "HTTP_COOKIE" in os.environ:
                cookie = http.cookies.SimpleCookie(os.environ["HTTP_COOKIE"])          
            else:
                cookie = http.cookies.SimpleCookie()
            
            #Define cookie name and value 
            cookie[key] = value
            
            #Go through and assign all cookie attributes
            for attribute in cookieAttributes:
                cookie[key][attribute['name']] = attribute['value']
            
            #This is the actual header output and will eventually happen in printHeaders response method
            os.environ["HTTP_COOKIE"] = cookie.output(header='')
        
    def addCookieFromRequestData(self, key):
        """Copy named / keyed data in the request to a session cookie,
        but only if the data item exists and is a non-empty string.
        """
        if key in self.requestData and self.requestData[key] != "":
            self.addCookie(key, self.requestData[key]);
    
    def response(self):
        """Deliver response after a handleRequest.  By default,
        just do a printTemplate, substituting in specified
        parameters in the requestData.  Subclasses may override
        this method however to do something different, such
        as redirecting to another page or outputting binary data.
        """
        if not self.disableResponse:
            self.printTemplate()
    
    def populatedTemplate(self):
        """Return the template
        html file out, replacing any parameters in the file
        based on what's been filled in the requestData attribute
        """
        templateFile = open(self.getTemplateFilename(),"r");
        populatedContents = templateFile.read() % self.requestData
        populatedContents = populatedContents.encode('utf-8');
        return populatedContents
    
    def printTemplate(self):
        """Standard end result of web script.  Print the template
        html file out, replacing any parameters in the file
        based on what's been filled in the requestData attribute
        """

        self.printHeaders();
        print()   # Separate headers from body
        # Output the template, replacing key fields by the values in templateDict
        print(self.populatedTemplate().decode());   # in Python3 without .decode(), prints bytes object, i.e., b'<string>'

    def returnHeaders(self, output):
        """Return HTTP headers for WSGI"""        
        headers = [('Content-type', "text/html"),];     # ("Content-length", str(len(output)))]
        # for cookie in self.getCookies():
        #     headers.append((cookie))        
        return headers

    def printHeaders(self):
        """Print HTTP headers before printing any body text"""
        print("Content-type: text/html")
        # Set any Cookies
        print(self.getCookies())
        
    def setTemplateFilename(self, filename):
        self.mTemplateFilename = filename
    
    def defaultTemplateFilename(self):
        """Default template filename is the same as the executing script,
        but ending in .htm instead of .py.
        """
        basename = self.__class__.__name__;
        defaultName = basename + self.TEMPLATE_SUFFIX;
        return defaultName;
    
    def getTemplateFilename(self):
        """If template filename has been manually set by user,
        then just return that.  Otherwise, build the standard
        template filename given the instance class's name.
        """
        if self.mTemplateFilename != None:
            return self.mTemplateFilename
        else:
            return self.defaultTemplateFilename();

    def optionTagsFromList(valueList, textList, selectedValue=None):
        """Generate and return the HTML 
        <option value="%value">%text</option> 
        tags for a given list of values and respective text labels.
        Each value printed will be compared to the selectedValue.
        If so, the option will also be "selected."  
        
        To allow for multiple selections, if selectedValue is found
        to be an instance of a sets.Set object, then, instead of 
        a direct comparison, each value will be searched for as a 
        key in the set.  If found, each of those options will be "selected".
        
        Note that this does NOT write the containing
        <select></select> tags, giving the caller control to 
        define any properties / styles on that tag.
        """
        optionTags = []
        optionDict = {}
        for value, text in zip(valueList,textList):
            optionDict["value"] = value
            optionDict["text"]  = text
            optionDict["selected"] = ""
            if selectedValue is not None:
                if value == selectedValue or (not isinstance(selectedValue, str) and (value in selectedValue)):
                    optionDict["selected"] = " selected"
            optionTags.append(BaseWeb.OPTION_TAG % optionDict)  # Fill in optionDict values into template string
        
        optionTags.append("")                   # Necessary to get last newline at end of string
        optionTagStr = str.join("\n",optionTags)# Join into one big string, by newline characters
        return optionTagStr
    optionTagsFromList = staticmethod(optionTagsFromList);
    
    def optionTagsFromField(self,fieldname,selected=None):
        """Shorthand for optionTagsFromList with default options and selected value."""
        valueList   = Options.FIELD2VALUE[fieldname];
        textList    = Options.FIELD2TEXT[fieldname];

        if selected is None and fieldname in self.requestData:    # Look for a pre-selected option
            selected = self.requestData[fieldname];

        return self.optionTagsFromList(valueList,textList,selected);
    
    def action_uploadFiles( self ):
        """Look for all fields whose name ends with file suffix "File"
        and loads those file contents into the field respectively
        named by that field's prefix.
        
        For example, given an input field of type file named "smilesFile",
        if the contents of that field are non-empty, copy the contents
        into the field (templateDict value) named "smiles"
        """
        for key in list(self.mForm.keys()):
            if key.endswith(self.FILE_FIELD_SUFFIX):
                fileContents = self.mForm[key].value
                if len(fileContents) > 0:
                    targetFieldName = key[0:len(key)-len(self.FILE_FIELD_SUFFIX)]
                    self.requestData[targetFieldName] = fileContents

    def buildTrackingScript(self):
        """Return a tracking (Java)Script to be included in pages 
        to allow for site traffic monitoring
        """
        return Env.TRACKING_SCRIPT_TEMPLATE % self.requestData;

    def replaceWhitespace(self, value):
        """Look for specific whitespace description sequences and replace them
        with the real special characters.
        """
        value = value.replace('\\t','\t');
        value = value.replace('\\n','\n');
        return value;

    def javascriptString(value):
        """Given a string value, replace certain special characters with placeholders so that
        the string can be in turn be used as a JavaScript string for subsequent dynamic manipulation.
        """
        value = value.replace("\\", "\\\\");
        value = value.replace("\n","\\n");
        value = value.replace("\r","");     # Windows newlines are \r\n.  \n already covered above, so drop the \r
        value = value.replace("\'", "\\'");   # Assumes single quote (') is used for JavaScript strings
        return value;
    javascriptString = staticmethod(javascriptString);

    def quoteFilepath( filepath ):
        """Neutralize any special characters for use as a filepath, 
        including '/' which could be a SMILES character.
        Additional issue on Windows systems: File names are NOT case-sensitive.
        This is a problem for SMILES strings where upper vs. lowercase
        atom labels is necessary to distinguish aromatic vs. aliphatic atoms.
        """
        newFilepath = [];   # Reconstruct string, but specially distinguish upper vs. lower case letters
        for char in filepath:
            if char.isupper():
                char = "_"+char;
            newFilepath.append(char);
        newFilepath = str.join('', newFilepath);    # Convert "StringBuffer" into actual string
        newFilepath = urllib.parse.quote(newFilepath,'');  # Neutralize special characters, including "/"
        return newFilepath;
    quoteFilepath = staticmethod(quoteFilepath)

if __name__ == "__main__":
    webController =  BaseWeb()
    webController.handleRequest(cgi.FieldStorage())

