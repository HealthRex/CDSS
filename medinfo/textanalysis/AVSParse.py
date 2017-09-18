#!/usr/bin/env python
"""
Read through a series of AVS text documents and generate an interactive HTML
web page that extracts out specific concept entities of interest.
"""

import sys, os;
import time;
import json;
import re, string;
from datetime import datetime;
from optparse import OptionParser
from cStringIO import StringIO;
from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.common.Util import parseDateValue;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;

from BaseTextAnalysis import BaseTextAnalysis, BaseQuestionModule, SectionLineCountQuestion;
from Util import log;

SECTION_HEADERS = \
    set([   "This is your After Visit Summary",
        "About your hospitalization",
        "Additional Discharge Orders",
        "Additional Instructions",
        "Admitted: Admission Type:",
        "Discharge Instructions",
        "Discharge Wound Care",
        "Follow Up (Outside/External)",
        "Follow Up (Stanford or UHA)",
        "Follow Up Instructions",
        "Home Care RN To Open Home Care Case",
        "Immunization History Reviewed",
        "Instruction for continuing your recovery at home",
        "Interagency Referral To Home Health",
        "Interagency Referral to Skilled Nursing Facility",
        "MD to call for questions on these Interagency orders",
        "Medication Information",
        "Notify MD Of Weight Gain",
        "Notify MD",
        "Physical Activity",
        "Please present this summary of care to other physicians who provide your ongoing care",
        "Please present this summary of care to other physicians who provide your ongoing care.",
        "Providers seen during hospitalization",
        "Referring provider for your hospitalization",
        "STOP TAKING these medications",
        "Signifiant Non-Operative/Bedside Procedures",
        "Significant Labs/Diagnostic Test Results",
        "Summary of Hospitalization",
        "Surgery Information",
        "TAKE these medications",
        "Therapy Precautions",
        "These are your currently scheduled appointments",
        "These appointments need to be scheduled (Call the number listed below to schedule appointment)",
        "These referrals need to be scheduled ",
        "Where to Get Your Medications",
        "Why you were hospitalized",
        "Wound Care",
        "You are allergic to the following",
        "Your Diet Orders",
        "Your Laboratory Orders",
        "Your Radiology Orders",
        "Your diagnoses also included:",
        "Your primary diagnosis was:",
    ]);

# Section header prefixes when cannot rely on exact match (e.g., annotated with date information)
# Avoid putting too much here, otherwise have long nested loop
SECTION_HEADER_PREFIXES = \
    [   "Immunization History Reviewed",
    ];

PAGER_NUM_DIGITS = 5;

# Accumulate list of key questions to search for / answer by default
DEFAULT_QUESTION_MODULES = list();

class FollowupPhoneQuestion(BaseQuestionModule):
    """Match up sequences consistent with 10 digit phone number regular expression
    http://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number
    """
    
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = \
            (   "These are your currently scheduled appointments",
                "Follow Up (Outside/External)",
                "Follow Up (Stanford or UHA)",
                "Follow Up Instructions",
                "Referring provider for your hospitalization",
            );
        self.maxExpectedDigits = 10;   # Maximum number of consecutive digits expected to represent a phone number
        self.phoneRegExp = "(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})"
        
    def __call__(self, docModel):
        phoneNumbers = list();
    
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                tokenModels = lineModel["tokenModels"];
                for iToken, tokenModel in enumerate(lineModel["tokenModels"]):
                    (phoneStr, phoneTokenModels) = self.extractPhoneTokenModels(iToken, tokenModels);
                    if len(phoneTokenModels) > 0:
                        for phoneTokenModel in phoneTokenModels:
                            phoneTokenModel[self.getName()] = True;
                        phoneNumbers.append(phoneStr);
        return set(phoneNumbers);   # Ensure a unique set
DEFAULT_QUESTION_MODULES.append(FollowupPhoneQuestion());

class TeamPagerQuestion(BaseQuestionModule):
    """Match up 5 digit pager number somewhere in discharge instructions
    """
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = \
            (   "Additional Instructions",
                "Discharge Instructions",
            );
        self.expectedNumDigits = PAGER_NUM_DIGITS;
        
    def __call__(self, docModel):
        pagerNumbers = list();
    
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                tokenModels = lineModel["tokenModels"];
                for iToken, tokenModel in enumerate(lineModel["tokenModels"]):
                    pagerPrefix = (iToken-1 >= 0 and re.match("(?i)pager", tokenModels[iToken-1]["rawToken"]) );    # Check if a prefix that indicates this is a 5 digit pager number (as opposed to say, a zip code)

                    strippedToken = tokenModel["noPunctuationToken"];
                    if len(strippedToken) > 0 and strippedToken[0] == "p": # Drop leading p for possible text pager prefix
                        pagerPrefix = True;
                        strippedToken = strippedToken[1:];
                    
                    if pagerPrefix and strippedToken.isdigit() and len(strippedToken) == self.expectedNumDigits:
                        tokenModel[self.getName()] = True;
                        pagerNumbers.append(strippedToken);
        return set(pagerNumbers);   # Ensure a unique set
DEFAULT_QUESTION_MODULES.append(TeamPagerQuestion());

class DietOrdersQuestion(SectionLineCountQuestion):
    def __init__(self):
        SectionLineCountQuestion.__init__(self);
        self.expectedSections = ("Your Diet Orders",);
DEFAULT_QUESTION_MODULES.append(DietOrdersQuestion());

class NotifyMDQuestion(SectionLineCountQuestion):
    """Simple check for labeled section, 
        though sometimes people include "Warning Signs" under general Discharge/Additional Instructions
    """
    def __init__(self):
        SectionLineCountQuestion.__init__(self);
        self.expectedSections = ("Notify MD",);
DEFAULT_QUESTION_MODULES.append(NotifyMDQuestion());

class PrimaryDxQuestion(BaseQuestionModule):
    """Looks for label "Your primary diagnosis was:"
    If that is blank or "Not on File" but other "Your diagnoses also included:" has content, should those be counted?
    """
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = ("Why you were hospitalized",);
        
    def __call__(self, docModel):
        diagnosisList = list();
    
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                line = lineModel["stripLine"];
                if line.startswith("Your primary diagnosis was:"):
                    diagnosisStr = line[line.find(":")+1:].strip(); # Pull out string after colon
                    if diagnosisStr != "Not on File":   # Default value if not populated.  Ignore this as blank / empty
                        diagnosisList.append(diagnosisStr);
                    
                    for iToken, tokenModel in enumerate(lineModel["tokenModels"]):
                        tokenModel[self.getName()] = True;  # Highlight the entire line, even if a valid diagnosis not found, so reviewer knows where to look

        return set(diagnosisList);   # Ensure a unique set
DEFAULT_QUESTION_MODULES.append(PrimaryDxQuestion());

class NewRxQuestion(BaseQuestionModule):
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = ("Where to Get Your Medications",);

    def __call__(self, docModel):
        medNames = list();
    
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                tokenModels = lineModel["tokenModels"];
                for iToken, tokenModel in enumerate(tokenModels):   
                    if iToken-1 >= 0 and tokenModels[iToken-1]["rawToken"] == "-":  # Previous token was "-" symbol
                        if tokenModel["firstAlpha"]:    # Make sure not a number, probably pharmacy address
                            tokenModel[self.getName()] = True;
                            medNames.append(tokenModel["rawToken"]);
                    if iToken-1 >= 0 and self.getName() in tokenModels[iToken-1]:  # Previous word was counted
                        # If still an alphabetic word, probably extended drug name
                        if tokenModel["firstAlpha"]:
                            tokenModel[self.getName()] = True;
                            medNames[-1] += " "+tokenModel["rawToken"];   # Append to last answer
                        elif tokenModel["rawToken"] == "-": 
                            # Ran into another delimiter but still looks like prior text.  
                            # Prior must not have been a drug.  Was a city name or something.  Go back and undo label
                            iPriorToken = iToken-1;
                            while iPriorToken >= 0 and self.getName() in tokenModels[iPriorToken]:
                                del tokenModels[iPriorToken][self.getName()];
                                iPriorToken -= 1;
                            medNames.pop();
                nTokens = len(tokenModels);
                if nTokens-1 >= 0 and self.getName() in tokenModels[nTokens-1]:  # Last word was counted
                    # But ran into end of line.  
                    # Last must not have been a drug.  Was a city name or something.  Go back and undo labels
                    iPriorToken = nTokens-1;
                    while iPriorToken >= 0 and self.getName() in tokenModels[iPriorToken]:
                        del tokenModels[iPriorToken][self.getName()];
                        iPriorToken -= 1;
                    medNames.pop();
        return set(medNames);   # Ensure a unique set
DEFAULT_QUESTION_MODULES.append(NewRxQuestion());

class StopRxQuestion(BaseQuestionModule):
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = ("STOP TAKING these medications",);

    def __call__(self, docModel):
        medNames = list();
    
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                tokenModels = lineModel["tokenModels"];
                for iToken, tokenModel in enumerate(tokenModels):   
                    if iToken == 0 and tokenModel["isalnum"]:  # First tokens of non-blank lines should be med names
                        tokenModel[self.getName()] = True;
                        medNames.append(tokenModel["rawToken"]);
                    if iToken-1 >= 0 and self.getName() in tokenModels[iToken-1]:  # Previous word was counted
                        # If still an alphabetic word, probably extended drug name
                        if tokenModel["firstAlpha"]:
                            tokenModel[self.getName()] = True;
                            medNames[-1] += " "+tokenModel["rawToken"];   # Append to last answer
                nTokens = len(tokenModels);
        return set(medNames);   # Ensure a unique set
DEFAULT_QUESTION_MODULES.append(StopRxQuestion());

class FollowupScheduleQuestion(BaseQuestionModule):
    """Looks for date-times under currently scheduled appointments, but may not be any
    easy way to isolate which are the "PCP" appointments.  Some are labeled Primary Care or Internal Medicine,
    but some have no labels, and for some patients, Oncology followup may be the more relevant "primary" followup anyway.
    """
    def __init__(self):
        BaseQuestionModule.__init__(self);
        self.expectedSections = ("These are your currently scheduled appointments",);

    def __call__(self, docModel):
        scheduleDates = list();
    
        for iLine, lineModel in enumerate(docModel["lineModels"]):
            if self.isLineInExpectedSection(lineModel):
                line = lineModel["stripLine"];
                endDateTimePos = max( line.find(" AM "), line.find(" PM ") );   # Expect the datetime string to end with AM or PM
                if endDateTimePos > 0:
                    candidateStr = line[:endDateTimePos+3]; # +3 to include the space and AM or PM
                    parsedValue = parseDateValue(candidateStr);
                    if isinstance(parsedValue,datetime):    # Valid date parsed out
                        scheduleDates.append(candidateStr);  # For consistency, should only be storing string values???
                        
                        # Label all tokens up to the AM / PM
                        for iToken, tokenModel in enumerate(lineModel["tokenModels"]):
                            tokenModel[self.getName()] = True;
                            if tokenModel["rawToken"] in ("AM","PM"):
                                break;  # Don't label beyond the date string

        return set(scheduleDates);
DEFAULT_QUESTION_MODULES.append(FollowupScheduleQuestion());

class AdditionalInstructionQuestion(SectionLineCountQuestion):
    def __init__(self):
        SectionLineCountQuestion.__init__(self);
        self.expectedSections = ("Additional Instructions","Discharge Instructions");

    def getName(self):
        return "AddnInstr";
DEFAULT_QUESTION_MODULES.append(AdditionalInstructionQuestion());

class AVSParse(BaseTextAnalysis):
    def __init__(self):
        BaseTextAnalysis.__init__(self);
        self.questionModules = DEFAULT_QUESTION_MODULES;
        self.documentHeader = "avs_summary";
        self.delim = None; # None Means any whitespace
        self.sectionHeaders = SECTION_HEADERS;
        self.sectionHeaderPrefixes = SECTION_HEADER_PREFIXES;


    def isNewRecordLine(self, line):
        """Determine if this line represents a new record.  
        Tab-delimitations messed up in last version, so look for start and end with a number
        """
        return BaseTextAnalysis.isNewRecordLine(self,line) or (line[0].isdigit() and line[-2].isdigit());  # -2, because expect newline character to end line

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <sourceFile> [<outputFile>]\n"+\
                    "   <sourceFile>     Source file of text data from data warehouse\n"+\
                    "   <outputFile>    HTML report file with analysis of source\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        BaseTextAnalysis.addParserOptions(self, parser);
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            BaseTextAnalysis.parseOptions(self, options);
            
            sourceFile = stdOpen(args[0]);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, "<!-- %s -->" % json.dumps(summaryData);

            # Run the actual analysis
            self(sourceFile, outputFile);
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = AVSParse();
    instance.main(sys.argv);
