#!/usr/bin/env python
"""Just some helper info to help debug web scripts
"""
import io, urllib.request, urllib.parse, urllib.error
import cgi, sys, os
import cgitb; cgitb.enable()

#sys.path.append("/var/www/cgi-bin")
#import CHEM.CombiCDB.Smi2Depict

#os.environ["LD_LIBRARY_PATH"] = "/usr/local/python/lib/python2.3/site-packages/openeye/libs"
#from openeye.oechem import *

def DebugWeb(environ, start_response):
    request = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

    templateDict = {}
    templateDict["importChemDB"] = ""
    templateDict["importOEChem"] = ""
    templateDict["importPsycoPg"] = ""
    
    if "importChemDB" in request: templateDict["importChemDB"] = "checked"
    if "importOEChem" in request: templateDict["importOEChem"] = "checked"
    if "importPsycoPg" in request: templateDict["importPsycoPg"] = "checked"

    html =\
"""
<html>
<body>
<form action="DebugWeb.py" method=get name="debugForm">
    <input type=text name="smiles">
    <A HREF="Draw structure" onClick="popup = window.open('../JMEPopupWeb.py?parentForm=debugForm&smilesField=smiles&smiles='+ document.forms[0].smiles.value +'&JMEPopupWeb=True','jmePopup','resizable=yes,width=400,height=400'); popup.focus(); return false;"><IMG SRC="../../resource/edit.gif" STYLE="width: 19; height: 17; border: 0" alt="Draw structure"></A>
    <br>
    <textarea name="testArea"></textarea>
    <A HREF="Draw structure" onClick="popup = window.open('../JMEPopupWeb.py?parentForm=debugForm&smilesField=testArea','jmePopup','resizable=yes,width=400,height=400'); popup.focus(); return false;"><IMG SRC="../../resource/edit.gif" STYLE="width: 19; height: 17; border: 0" alt="Draw structure"></A>
    <br>
    <select multiple name="testMulti" size=4>
        <option>A
        <option>B
        <option>C
        <option>D
        <option>E
        <option>F
        <option>G
    </select><br>
    <input type=text name="repeater" value="joe"><br>
    <input type=text name="repeater" disabled value="blah"><br>
    <input type=text name="repeater" value="mama"><br>
    
    Import:
    <ul>
        <li><input type=checkbox name="importChemDB" value="checked" %(importChemDB)s> Misc ChemDB Module (requires web server PYTHONPATH to be set to CHEM's parent directory)
        <li><input type=checkbox name="importOEChem" value="checked" %(importOEChem)s> OEChem (requires OEChem installation and web server OE_LICENSE to be set to license file name and location)
        <li><input type=checkbox name="importPsycoPg" value="checked" %(importPsycoPg)s> PsycoPg
    </ul>   
    <input type=file name="testFile"><br>
    <input type=submit name="JMEPopupWeb"><br>
</form>
""" % templateDict

    # Test if external imports work:
    if "importChemDB" in request:
        import CHEM.Common.Env
        html += "<i>Successfully imported a CHEM module</i><br>"
    if "importOEChem" in request:
        from openeye.oechem import OEGraphMol
        mol = OEGraphMol();
        html += "<i>Successfully imported a OEChem module</i><br>"
    if "importPsycoPg" in request:
        import psycopg2
        html += "<i>Successfully imported psycopg2 module</i><br>"

    html += "Request Parameters"
    html += "<table border=1>"
    html += "<tr><th>Key</th><th>Value</th><th>Filename and Type</th></tr>"
    for key in list(request.keys()):
        field = request[key]
        if not isinstance(field,list):
            field = [field];    # Convert to list of size 1
        for item in field:
            html += "<tr><td>%s</td><td><pre>%s</pre></td><td>%s<br><br>%s</td></tr>" % (key,item.value,item.filename,item.type)
    html += "</table>"
    
    html += "Paths (PYTHONPATH)"
    html += "<ul>"
    for path in sys.path:
        html += "<li>"+path+"</li>"
    html += "</ul>\n" 

    #cgi.test()
    html += "<b>Request</b><br>"
    html += str(request)

    html += "<br><b>Environment Variables</b>"
    html += "<table border=1>"
    html += "<tr><th>Key</th><th>Value</th></tr>"
    
    keyList = list(os.environ.keys())
    keyList.sort()
    for key in keyList:
        html += "<tr><td>%s</td><td>%s</td></tr>" % (key,os.environ[key])
    html += "</table>"



    html += "</body>"
    html += "</html>"

    status = '200 OK'
    response_headers = [('Content-type', 'text/html'),
                        ('Content-Length', str(len(html)))]
    start_response(status, response_headers)
    return html

# Initialize Web instance
application = DebugWeb

