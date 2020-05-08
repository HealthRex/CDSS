#!/usr/bin/env python
"""Standard conversion from older CGI HTML template files to 
basic PSP files that can function equivalently.
"""
import sys;
import os;
import time;
from optparse import OptionParser
from .Util import log;

def generatePSPfromCGITemplate( cgiTemplateFilename, linkConversion=False ):
    """Standard conversion from older CGI HTML template files to 
    basic PSP files that can function equivalently.
    
    Expects name of the cgiTemplateFile (e.g., Smi2DepictWeb.htm).
    Will generate a PSP file in the same directory (e.g., Smi2DepictWeb.psp).
    
    To get the controller module import correct, assumes that all of these
    are under the CHEM.Web.cgibin package or a sub-package.

    linkConversion: If set, will swap all .py (apparent links) to .psp.
    """
    # Figure out all of the file names, directories, etc.
    cgiAbspath = os.path.abspath(cgiTemplateFilename);
    cgiBaseFilename = os.path.basename(cgiAbspath);
    baseDir = os.path.dirname(cgiAbspath);
    baseName = os.path.splitext(cgiBaseFilename)[0];
    
    pspBaseFilename = baseName + ".psp";
    pspAbspath = os.path.join(baseDir, pspBaseFilename);
    
    # Figure out if there are any subpackages between this file and the base cgibin directory
    subpackages = [];
    while not baseDir.endswith("cgibin") and len(baseDir) > 0:
        dirSplit = os.path.split(baseDir);
        subpackages.append( dirSplit[-1] );
        baseDir = dirSplit[0];
    subpackages.reverse();  # Undo reverse iteration    
    subpackages.append( baseName );
    subpackageStr = str.join(".", subpackages );
    
    # Dictionary of terms to fill in generated template with
    templateDict = {"subpackages": subpackageStr, "baseName": baseName };

    # Start generating the PSP, beginning with controller request handling header
    pspFile = open(pspAbspath,"w");
    pspFile.write \
    ("""<%%
from CHEM.Web.cgibin.%(subpackages)s import %(baseName)s;

controller = %(baseName)s();
controller.disableResponse = True;  # PSP content below will be the response / output
controller.handleRequest(req.form, req); # Process any actions and parameter maintenance
reqData = controller.requestData;   # Short-hand reference to form and output data
%%>
""" % templateDict
    );
    
    cgiFile = open(cgiAbspath);
    for cgiLine in cgiFile:
        pspLine = convertCGI2PSPLine( cgiLine, linkConversion );
        pspFile.write( pspLine );
    
    cgiFile.close();
    pspFile.close();

def convertCGI2PSPLine( cgiLine, linkConversion=False ):
    """Convert a single line from a CGI HTML template to PSP equivalent.

    linkConversion: If set, will swap all .py (apparent links) to .psp.
    """
    pspLine = cgiLine.replace("%(", "<%= reqData['");
    pspLine = pspLine.replace(")s", "'] %>");
    pspLine = pspLine.replace("%%", "%");
    if linkConversion:
        pspLine = pspLine.replace(".py", ".psp");
    return pspLine;

def main(argv):
    """Main method, callable from command line"""
    usageStr =  "usage: %prog [options] <cgiFile1> <cgiFile2> ...\n"+\
                "   <cgiFileX>    CGI template files to convert to PSP\n"
    parser = OptionParser(usage=usageStr)
    parser.add_option("-l", "--noLinkConversion", dest="noLinkConversion", action="store_true", help="If set, will NOT swap all .py (apparent links) to .psp.")
    (options, args) = parser.parse_args(argv[1:])

    timer = time.time();

    if len(args) > 0:
        for cgiTemplateFilename in args:
            log.info("Converting %s" % cgiTemplateFilename );
            generatePSPfromCGITemplate( cgiTemplateFilename, not options.noLinkConversion );
    else:
        parser.print_help()
        sys.exit(-1)

    timer = time.time() - timer;
    log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    main(sys.argv);
    