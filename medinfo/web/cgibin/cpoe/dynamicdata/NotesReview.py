#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
from cStringIO import StringIO;
import urllib;

from datetime import datetime, timedelta;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.cpoe.SimManager import SimManager;
from medinfo.cpoe.Const import BASE_TIME, TIME_FORMAT;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;

LINE_TEMPLATE = \
    """
    <tr>
        <td align=center><a href="javascript:loadNoteContent(%(sim_note_id)s)">%(note_type)s %(sim_state_id)s</a></td>
        <td align=center><a href="javascript:loadNoteContent(%(sim_note_id)s)">%(service_type)s</a></td>
        <td align=center><a href="javascript:loadNoteContent(%(sim_note_id)s)">%(author_type)s</a></td>
        <td align=center><a href="javascript:loadNoteContent(%(sim_note_id)s)">%(note_time.format)s</a>
            <input type=hidden name="noteContent.%(sim_note_id)s" value="%(content.quoted)s">
        </td>
    </tr>
    """;

class NotesReview(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    """
    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["sim_patient_id"] = "";
        self.requestData["sim_time"] = "";
        
        self.requestData["detailTable"] = "";
        self.requestData["initialNoteContent"] = "";
        
        self.addHandler("sim_patient_id", NotesReview.action_default.__name__);
        
    def action_default(self):
        """Present currently selected set of pending clinical item orders"""
        patientId = int(self.requestData["sim_patient_id"]);
        simTime = int(self.requestData["sim_time"]);
        
        # Load lookup table to translate note type IDs into description strings
        noteTypeById = DBUtil.loadTableAsDict("sim_note_type");
        
        manager = SimManager();
        results = manager.loadNotes(patientId, simTime);
        
        htmlLines = list();
        for dataModel in results:
            self.formatDataModel(dataModel, noteTypeById);
            htmlLines.append( LINE_TEMPLATE % dataModel );
        self.requestData["detailTable"] = str.join("\n", htmlLines );
        
        if len(results) > 0:
            self.requestData["initialNoteContent"] = results[0]["content"];

    def formatDataModel(self, dataModel, noteTypeById):
        """Populate dataModel with formatted items"""
        dataModel["note_type"] = noteTypeById[dataModel["note_type_id"]]["name"];
        dataModel["service_type"] = noteTypeById[dataModel["service_type_id"]]["name"];
        dataModel["author_type"] = noteTypeById[dataModel["author_type_id"]]["name"];
        dataModel["note_time.format"] = (BASE_TIME + timedelta(0,dataModel["relative_time"])).strftime(TIME_FORMAT);
        dataModel["content.quoted"] = urllib.quote(dataModel["content"]);
        
# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  NotesReview()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
if __name__.startswith("_mod_wsgi_"):
    webController = NotesReview()
    webController.setFilePath(__file__)
    application = webController.wsgiHandler 