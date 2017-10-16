#!/usr/bin/env python
"""
Base module to analyze text data to enable question answering (usually entity / concept recognition)
across all words / tokens traversed in the text.
Facilitate generate of interactive HTML webpage to review results.
"""

import sys, os
import time;
import re, string;
from optparse import OptionParser
from cStringIO import StringIO;
from math import sqrt;
from datetime import timedelta;

from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, HtmlResultsFormatter, TabDictReader;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from Util import log;

HTML_START = """<html><head><script>%(script)s</script><style>%(style)s</style></head><body><form name="mainForm">""";
HTML_END = """</form></body></html>""";

import medinfo.textanalysis;
sourceDir = os.path.dirname(medinfo.textanalysis.__file__);
HTML_SCRIPT_FILENAME = "textAnalysis.js";
HTML_SCRIPT = stdOpen(os.path.join(sourceDir, HTML_SCRIPT_FILENAME)).read();

HTML_STYLE_FILES = ("stylesBasic.css","stylesGrey.css");
HTML_STYLE = "";
for styleFilename in HTML_STYLE_FILES:
    styleFile = stdOpen(os.path.join(sourceDir, styleFilename));
    HTML_STYLE += styleFile.read();

# Maximum number of characters to present in question-answer note summaries
DEFAULT_MAX_NOTE_LENGTH = 25;

class BaseTextAnalysis:
    connFactory = None;

    def __init__(self):
        self.questionModules = list();
        self.delim = "\t";  # Tab delimited by default, but may need to revise
        self.documentHeader = None;    # Name of the field expected to contain the document text to parse
        self.sectionHeaders = list();
        self.sectionHeaderPrefixes = list();
        self.summaryHeaders = ["iRecord","note_id","pat_mrn_id","pat_enc_csn_id","contact_date","textLength"];   # Lead headers to print to summary output

        self.sampleInterval = 1;    # How many records to traverse before processing one.  Set to a value > 1 to for an evenly spaced sample of the source data
        self.skipDetail = False;    # If set, will skip output of full detailed records (thus only outputting summary table)

    def __call__(self, sourceFile, outputFile):
        headers = sourceFile.readline().split();
        for i, header in enumerate(headers):
            headers[i] = header.lower();

        prog = ProgressDots(50,1);
        summaryRecords = list();

        headerData = {"script": HTML_SCRIPT, "style": HTML_STYLE}

        print >> outputFile, HTML_START % headerData;
        nextRecord = None;
        lastLine = None;

        print >> outputFile, '''<table class="dataTable" cellspacing=0 cellpadding=4>''';
        iRecord = 0;
        for line in sourceFile:
            if self.isNewRecordLine(line):
                # Blank line should signal end of a record
                if nextRecord is not None:
                    # Process the prior record
                    if iRecord % self.sampleInterval == 0:
                        self.processRecord(nextRecord, iRecord);
                        self.outputRecordDetail(nextRecord, outputFile);
                        summaryRecords.append(self.extractSummaryRecord(nextRecord));  # Add just summary information to display later, without keeping whole text file in memory. This can still 2GB RAM per 1000 records, so may be better to route to temporary file instead
                    iRecord += 1;
                    prog.update();

                # Prepare a new record
                nextRecord = dict();
                chunks = line.split(self.delim);
                numChunks = len(chunks);
                for i, header in enumerate(headers):
                    if i < numChunks:
                        nextRecord[header] = chunks[i];
                    else:   # Not enough values.  Probably because continues to next line.  Record blank string
                        nextRecord[header] = "";
                #nextRecord["contact_date"] = DBUtil.parseDateValue(nextRecord["contact_date"]);
            else:   # documentHeader in nextRecord   # Continuing lines of text
                nextRecord[self.documentHeader] += line;

        # Process the last record
        if iRecord % self.sampleInterval == 0:
            self.processRecord(nextRecord, iRecord);
            self.outputRecordDetail(nextRecord, outputFile);
            summaryRecords.append(self.extractSummaryRecord(nextRecord));  # Add just summary information to display later, without keeping whole text file in memory
        iRecord += 1;
        prog.update();
        # prog.printStatus();

        print >> outputFile, '''</table>''';

        self.outputSummaryRecords(summaryRecords, outputFile);

        print >> outputFile, HTML_END;

        #for header in headerSet:
        #    print >> sys.stdout, header;
        return summaryRecords;


    def isNewRecordLine(self, line):
        """Determine if this line represents a new record.  Basically look for tab-delimited data values"""
        return (line[:100].find("\t") >= 0);

    def processRecord(self, record, iRecord):
        """Find the text field and parse through/process it to get desired information"""
        docText = record[self.documentHeader];
        record["iRecord"] = iRecord;
        record["textLength"] = len(docText);

        # Try to spot new lines by several spaces
        docTextLines = docText.replace("    ","\n");

        tokenizeOps = TokenizeOptions();
        tokenizeOps.sectionHeaders = self.sectionHeaders;
        tokenizeOps.sectionHeaderPrefixes = self.sectionHeaderPrefixes;
        docModel = self.tokenizeDocument(docTextLines, tokenizeOps);

        for questionModule in self.questionModules:
            answer = questionModule(docModel);
            docModel[questionModule.getName()] = answer;

        record["docModel"] = docModel;

        # Add token level question annotations
        for lineModel in record["docModel"]["lineModels"]:
            for tokenModel in lineModel["tokenModels"]:
                questionTagsFound = set();
                for questionModule in self.questionModules: # Look for question module tags
                    moduleName = questionModule.getName();
                    if moduleName in tokenModel:
                        questionTagsFound.add(moduleName);
                    record[moduleName] = questionModule.formatAnswer(record["docModel"]);  # Store at record level for summary retrieval later
                tokenModel["questionNames"] = str.join(",", questionTagsFound );
                tokenModel["iRecord"] = iRecord;

        for questionModule in self.questionModules:
            questionData = {"iRecord": record["iRecord"], "name": questionModule.getName(), "answer": questionModule.formatAnswer(record["docModel"]), "notes": questionModule.formatNotes(record["docModel"]) }
            record[questionData["name"]] = questionData["answer"];  # Store at record level for summary retrieval later

    def outputRecordDetail(self, record, outputFile):

        if self.skipDetail:
            return;

        print >> outputFile, \
            '''<tr><th class="subheading">iRecord</th>
                    <th class="subheading">Note ID</th>
                    <th class="subheading">MRN</th>
                    <th class="subheading">Date</th>
                    <th class="subheading">Questions</th>
               </tr>
               <tr>
                    <td class="labelCell" align=center>%(iRecord)s</td>
                    <td class="labelCell" align=center>%(note_id)s</td>
                    <td class="labelCell" align=center>%(pat_mrn_id)s</td>
                    <td class="labelCell" align=center>%(contact_date)s</td>

                    <td class="labelCell" align=center>&nbsp;</td>
                </tr>''' % record;

        print >> outputFile, '''<tr valign=top><td colspan=4 width="70%"><div style="overflow-y: scroll; height: 400px">''';

        lastLineModel = None;
        for lineModel in record["docModel"]["lineModels"]:
            isSectionHeader = lastLineModel is not None and lineModel["section"] != lastLineModel["section"];
            if isSectionHeader:
                print >> outputFile, "<u>",;

            for tokenModel in lineModel["tokenModels"]:
                if len(tokenModel["questionNames"]) > 0:
                    print >> outputFile, '<a name="%(iRecord)d.%(questionNames)s" href="javascript:setQuestionsByName(\'%(questionNames)s\', %(iRecord)d)">' % tokenModel,;

                print >> outputFile, tokenModel["rawToken"],;

                if len(tokenModel["questionNames"]) > 0:
                    print >> outputFile, "</a>",;

            if isSectionHeader:
                print >> outputFile, "</u>",;
            print >> outputFile, "<br>";
            lastLineModel = lineModel;

        print >> outputFile, '''<div></td><td style="padding: 0">'''
        self.outputRecordQuestions(record, outputFile);
        print >> outputFile, '''</td>'''
        print >> outputFile, \
            '''</td></tr>
            <tr><td class=line height=1 colspan=100></td></tr>
            ''';

    def outputRecordQuestions(self, record, outputFile):
        print >> outputFile, '''<table cellspacing=0 cellpadding=2 style="width: 100%;">''';
        print >> outputFile, '''<tr><th class="labelCell"><!-- input type=checkbox name="allQuestionsCheck" onClick="javascript:checkAllQuestions(this, %(iRecord)d)" --></th>''' % record;
        print >> outputFile, '''<th class="labelCell">Name</th><th class="labelCell">Guess</th><th class="labelCell" align=left>Notes</th></tr>''';
        for questionModule in self.questionModules:
            questionData = {"iRecord": record["iRecord"], "name": questionModule.getName(), "answer": questionModule.formatAnswer(record["docModel"]), "notes": questionModule.formatNotes(record["docModel"]) }
            print >> outputFile, '''<tr id="questionName.%(iRecord)d.%(name)s" onClick="javascript:checkQuestionByName('%(name)s', %(iRecord)d)"><td align=center><input type=checkbox name="questionCheck.%(iRecord)d" value="%(name)s" onClick="return checkQuestion(this);"></td>''' % questionData;
            print >> outputFile, '''<td align=center>%(name)s</td><td align=center>%(answer)s</td><td>%(notes)s</td></tr>''' % questionData;

        print >> outputFile, '''</table>''';

    def extractSummaryRecord(self, record):
        summaryRecord = dict();
        for key, value in record.iteritems():
            if not key.startswith(self.documentHeader):
                summaryRecord[key] = value;
        return summaryRecord;

    def outputSummaryRecords(self, summaryRecords, outputFile):
        # Field names with or without using data control links instead of just raw values
        headers = list(self.summaryHeaders);
        controlHeaders = list(self.summaryHeaders);
        for questionModule in self.questionModules:
            headers.append(questionModule.getName());
            controlHeaders.append(questionModule.getName()+".link");

        print >> outputFile, '''<br>
            <table class="dataTable" cellspacing=0 cellpadding=4 style="width: 100%">
            <tr><th class="subheading" colspan=100>Summary Table</th></tr>''';

        textAreaRows = 50;
        if not self.skipDetail:
            # HTML table form with links back to records
            formatter = HtmlResultsFormatter(outputFile, headerRowFormat='th class="labelCell"', align="center");
            formatter.formatTuple(headers); # Header row
            for summaryRecord in summaryRecords:
                for questionModule in self.questionModules:
                    questionName = questionModule.getName();
                    linkFieldName = questionName+".link";
                    summaryRecord[linkFieldName] = ('<a href="javascript:setQuestionsByName(\''+questionName+'\', %(iRecord)s)">%('+questionName+')s</a>') % summaryRecord;
                formatter.formatResultDict(summaryRecord, controlHeaders);

            textAreaRows = 5;   # If showing detail records, pay less attention to the raw text area


        # Raw result content for copy-paste to spreadsheet
        print >> outputFile, '''<tr><td class="labelCell" style="color: 808080" colspan=100>Raw Table (Select All and Copy-Paste to Spreadsheet)</td></tr>''';
        print >> outputFile, '''<tr><td colspan=100><textarea style="width: 100%%;" disabled rows=%d>''' % textAreaRows;
        formatter = TextResultsFormatter(outputFile);
        formatter.formatTuple(headers);
        for summaryRecord in summaryRecords:
            formatter.formatResultDict(summaryRecord, headers);
        print >> outputFile, '''</textarea></td></tr>''';

        print >> outputFile, '''</table>''';
        print >> outputFile, "%d Records Processed" % len(summaryRecords);

    def tokenizeDocument(self, rawText, tokenizeOps):
        """Convert raw text string into a structured, tokenized format.
        Dict with document annotations and
            List of line data
                Each line data being a dict with line annotations and
                    List of word/token data
                        Each word/token data item another dict with annotation information and
                            Source raw word/token
        """
        docModel = dict();
        docModel["rawText"] = rawText;
        docModel["lineModels"] = list();
        rawTextIO = StringIO(rawText);
        for iLine, rawLine in enumerate(rawTextIO):
            line = rawLine.strip();
            lineModel = dict();
            lineModel["rawLine"] = rawLine;
            lineModel["stripLine"] = line;
            lineModel["tokenModels"] = list();
            tokens = line.split();
            for token in tokens:
                tokenModel = dict();
                tokenModel["rawToken"] = token;
                self.annotateTokenModel(tokenModel);    # Do some basic annotations
                lineModel["tokenModels"].append(tokenModel);

            lineModel["section"] = None;
            if tokenizeOps.sectionHeaderPrefixes is not None:
                for sectionHeaderPrefix in tokenizeOps.sectionHeaderPrefixes:
                    if line.startswith(sectionHeaderPrefix):
                        lineModel["section"] = sectionHeaderPrefix;
            if tokenizeOps.sectionHeaders is not None:
                if line in tokenizeOps.sectionHeaders:
                    lineModel["section"] = line;
            if lineModel["section"] is None and iLine > 0:    # No new section found, copy last one if available
                lineModel["section"] = docModel["lineModels"][-1]["section"];

            docModel["lineModels"].append(lineModel);
        return docModel;

    def annotateTokenModel(self, tokenModel):
        """Basic annotations that may be useful to several different parsing questions"""
        token = tokenModel["rawToken"];
        tokenModel["length"] = len(token);
        tokenModel["isalnum"] = token.isalnum();
        tokenModel["isalpha"] = token.isalpha();
        tokenModel["isdigit"] = token.isdigit();
        tokenModel["firstAlnum"] = (tokenModel["length"] > 0 and token[0].isalnum());
        tokenModel["firstAlpha"] = (tokenModel["length"] > 0 and token[0].isalpha());
        tokenModel["firstDigit"] = (tokenModel["length"] > 0 and token[0].isdigit());
        tokenModel["lastAlnum"] = (tokenModel["length"] > 0 and token[-1].isalnum());
        tokenModel["lastAlpha"] = (tokenModel["length"] > 0 and token[-1].isalpha());
        tokenModel["lastDigit"] = (tokenModel["length"] > 0 and token[-1].isdigit());
        tokenModel["noPunctuationToken"] = token.translate(None, string.punctuation);  # Token after discarding any punctuation characters.  Should not need to discard whitespace characters, since token splitting already separates them

    def addParserOptions(self, parser):
        """Base command-line parser options
        """
        parser.add_option("-i", "--sampleInterval", dest="sampleInterval", help="Set to a value >1 to only process a sample of the records based on the specified interval spacing.");
        parser.add_option("-s", "--skipDetail", dest="skipDetail", action="store_true", help="If set, will not output the full record details, just the main summary table.");

    def parseOptions(self, options):
        """Base command-line option parsing
        """
        if options.sampleInterval:
            self.sampleInterval = int(options.sampleInterval);
        self.skipDetail = options.skipDetail;

class BaseQuestionModule:
    """Base class for question annotation modules"""
    def __init__(self):
        self.expectedSections = None;
        self.maxNoteLength = DEFAULT_MAX_NOTE_LENGTH;

    def __call__(self, docModel):
        """Given tokenized document (data dict with list of text line data, each a list of token/word data),
        Return best guess for answer to this module's question.
        Annotate document token data based on areas of apparent relevance
        """
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                for iToken, tokenModel in enumerate(lineModel["tokenModels"]):
                    #tokenModel[self.getName()] = True;
                    pass;

        raise NotImplementedError();

    def isLineInExpectedSection(self, lineModel):
        return (lineModel["section"] in self.expectedSections and lineModel["stripLine"] != lineModel["section"]);  # Ignore the section header line itself

    def getName(self):
        questionName = self.__class__.__name__;
        if questionName.endswith("Question"):
            questionName = questionName[:-len("Question")];
        return questionName;

    def formatAnswer(self, docModel):
        """Given a processed document model, return a string representation of this question's answer.
        Default report a count of number of target strings / items found
        """
        answer = 0;
        if self.getName() in docModel:
            items = docModel[self.getName()];
            answer = len(items);
        return answer;

    def formatNotes(self, docModel):
        """Given a processed document model, return a string representation of any notes about this question's answer.
        Default present a pipe-separated list of the target strings / items found
        """
        notes = 0;
        if self.getName() in docModel:
            items = docModel[self.getName()];
            notes = str.join("| ", items);
            if len(notes) > self.maxNoteLength:
                notes = notes[:self.maxNoteLength]+"...";
        return notes;

    def extractPhoneTokenModels(self, iStartToken, tokenModels):
        """Determine if the next series of token models (starting with the iStartToken position)
        represents a telephone number.  If so, return that subset of token models.  Empty list otherwise.
        """
        numericTokenModels = list();
        numDigits = 0;
        # Iterate from iStartToken and accumulate list of all numeric tokens (after discarding punctuation) until
        #   reach non-numeric token or reach expected phone number size
        for iToken in xrange(iStartToken, len(tokenModels)):
            tokenModel = tokenModels[iToken];
            if tokenModel["noPunctuationToken"].isdigit():
                numericTokenModels.append(tokenModel);
                numDigits += len(tokenModel["noPunctuationToken"]);
                if numDigits >= self.maxExpectedDigits:
                    # Stop accumulating numbers as should have more than enough to define a phone number
                    #   Anything more likely represents something else (a date string or something)
                    break;
            else:
                break;  # Non-numeric character, must not be a phone number anymore

        # Rebuild into a string can do a regular expression match against
        compositeStrTokens = list();
        for tokenModel in numericTokenModels:
            compositeStrTokens.append( tokenModel["rawToken"] );
        compositeStr = str.join(" ", compositeStrTokens);

        phoneMatch = re.match(self.phoneRegExp, compositeStr);

        if not phoneMatch:    # Discard if does not match phone number structure
            numericTokenModels = list();
            compositeStr = "";

        return (compositeStr, numericTokenModels);

class SectionLineCountQuestion(BaseQuestionModule):
    """Specific implementation of a question which just looks for the named
    expected sections and counts up the number of lines of text under them
    """
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = None;   # Subclass still needs to define this

    def __call__(self, docModel):
        lines = list();

        for iLine, lineModel in enumerate(docModel["lineModels"]):
            line = lineModel["stripLine"];
            if self.isLineInExpectedSection(lineModel):
                if not line.startswith("Complete by:") and line != "":  # Ignore lines without much meaning
                    lines.append(line);
                    tokenModels = lineModel["tokenModels"];
                    for iToken, tokenModel in enumerate(tokenModels):
                        tokenModel[self.getName()] = True;
        return lines;



class TokenizeOptions:
    """Simple struct to store parsing and tokenizing options"""
    def __init__(self):
        self.sectionHeaders = None; # Line values expected to represent section headers
        self.sectionHeaderPrefixes = None;  # Prefixes of lines expected to represent section headers
