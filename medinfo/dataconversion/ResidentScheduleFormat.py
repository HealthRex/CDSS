#!/usr/bin/env python
import sys, os
import time;
import csv;
from datetime import datetime, timedelta;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.db.Model import RowItemModel, RowItemFieldComparator, modelListFromTable, modelDictFromList;

from Util import log;

CHANGE_HOUR = 7;  # Designate 7am as changeover time rather than midnight, otherwise night shift behavior on change dates will be misinterpreted
DEFAULT_INDEX_PREFIX_LENGTH = 5;    # Default number of first letters (prefix) of a provider's name to count as equal / equivalent when guessing provider IDs
PLACEHOLDER_ID_TEMPLATE = "S%03d";  # Template for fake / placeholder provider ID to generate as needed
PLACEHOLDER_ID_BASE_COUNTER = -1000;    # Initial value for fake ID sequence counter in negative values

class ResidentScheduleFormat:
    """Data conversion module to take Resident Schedule Excel spreadsheet
    and convert into relational data structure to faciltiate subsequent database manipulation and analysis.
    """
    def __init__(self):
        """Default constructor"""
        self.changeHour = CHANGE_HOUR;
        self.indexPrefixLength = None;
        self.providersByNamePrefix = None;
        self.placeholderIdCounter = PLACEHOLDER_ID_BASE_COUNTER;

    def parseScheduleItems(self, scheduleFile, baseYear):
        """Given a file reference, parse through contents to generate a list of 
        relational (dictionary) schedule items representing each dated user-rotation schedule component.
        """
        reader = csv.reader(scheduleFile, dialect=csv.excel_tab);  # Assume tab delimited file
        
        # Iterate through header lines until find one that looks like key date row
        # Expect first key line to be the primary date ranges
        row = reader.next();
        while row[-1].isalnum() or row[-1].find("-") < 0:    # Expect date rows formatted like "5/25 - 6/24" so look for a non-alphanumeric row with a '-'' in the middle
            row = reader.next();        
        dateRanges = self.parseDateRanges(row, baseYear);  

        # Expect next line to be mid-rotation split dates
        row = reader.next();    
        splitDates = self.parseSplitDates(row, baseYear); 
        
        scheduleItems = list();
        lastResident = None;
        resTextChunksList = list();
        for textChunks in reader:
            resident = textChunks.pop(0).strip();   # Remove first item corresponding to resident name
            if lastResident is None:    # First entry to start chain
                lastResident = resident;
            elif resident != "" and resident != lastResident:  # New entry means already accumulated all records for prior resident.  Process those now before moving on
                scheduleItems.extend( self.parseResidentScheduleItems(lastResident, resTextChunksList, dateRanges, splitDates) );
                lastResident = resident;
                resTextChunksList = list();    # Clear for new resident info to accumulate
            resTextChunksList.append(textChunks);
        scheduleItems.extend( self.parseResidentScheduleItems(lastResident, resTextChunksList, dateRanges, splitDates) );   # Last pass for the last resident
        return scheduleItems;

    def parseResidentScheduleItems(self, resident, resTextChunksList, dateRanges, splitDates):
        """Parse just the text chunks for an individual resident, being aware of potential for list of multiple rows
        """
        provId = self.inferProvIdFromName(resident);

        for iBlock, dateRange in enumerate(dateRanges):    # Iterate through each major rotation block
            dateRange = dateRanges[iBlock];
            splitDate = splitDates[iBlock];
            
            # First pass through to look for specifically dated rotations
            scheduleItems = list();
            for iRow, resTextChunks in enumerate(resTextChunksList):
                textChunk = resTextChunks[iBlock].strip();
                #print >> sys.stderr, iRow, textChunk
                if textChunk != "" and textChunk[-1].isdigit(): # Ends with a number, must be a date specification
                    subChunks = textChunk.split();  # Separate out date
                    dateRangeText = subChunks.pop(-1);
                    (startText, endText) = dateRangeText.split("-");   # Separate out start from end date
                    startDate = self.parseDateText( startText, dateRange[0], 0 );
                    endDate = self.parseDateText( endText, dateRange[0], 1 );

                    rotation = str.join(' ', subChunks);    # Reconstruct rotation name

                    scheduleItem = {"prov_id": provId, "name": resident, "rotation": rotation, "start_date": startDate, "end_date": endDate};
                    scheduleItems.append(scheduleItem);
                    
            # Second pass to look for rotations without dates specified based on standard dates
            for iRow, resTextChunks in enumerate(resTextChunksList):
                textChunk = resTextChunks[iBlock].strip();
                if textChunk != "" and not textChunk[-1].isdigit(): # Remaining non-blank items that do not end with a number
                
                    subChunks = textChunk.split("|");   # See if split into multiple rotations
                    if len(subChunks) > 1:  # Multiple rotations within time block
                        rotation = subChunks[0].strip();
                        if rotation[0].isalpha():   # Ensure starts with a letter, and not special character for blank placeholder
                            (startDate, endDate) = self.compressDateRange( dateRange[0], splitDate, scheduleItems );  # End split date
                            scheduleItem = {"prov_id": provId, "name": resident, "rotation": rotation, "start_date": startDate, "end_date": endDate};
                            scheduleItems.append(scheduleItem);

                        rotation = subChunks[-1].strip();
                        if rotation[0].isalpha():   # Ensure starts with a letter, and not special character for blank placeholder
                            (startDate, endDate) = self.compressDateRange( splitDate, dateRange[-1], scheduleItems );  # Start on split date
                            scheduleItem = {"prov_id": provId, "name": resident, "rotation": rotation, "start_date": startDate, "end_date": endDate};
                            scheduleItems.append(scheduleItem);
                    else:   # Single rotation spanning the full block
                        rotation = subChunks[0].strip();
                        if rotation[0].isalpha():   # Ensure starts with a letter, and not special character for blank placeholder
                            (startDate, endDate) = self.compressDateRange( dateRange[0], dateRange[-1], scheduleItems );
                            scheduleItem = {"prov_id": provId, "name": resident, "rotation": rotation, "start_date": startDate, "end_date": endDate};
                            scheduleItems.append(scheduleItem);

            # Now yield / generate results, but keep sorted in chronologic order
            scheduleItems.sort( RowItemFieldComparator("start_date") );
            for item in scheduleItems:
                yield item;

    def loadProviderModels( self, providerModels, indexPrefixLength=DEFAULT_INDEX_PREFIX_LENGTH ):
        """Store a copy of the given provider models (expect each to be a dictionary with prov_id, last_name, first_name combinations).
        Prepare an index around these based on first X characters of each name to use when trying to back track
        provider names to prov_ids.
        """
        self.indexPrefixLength = indexPrefixLength;
        self.providersByNamePrefix = dict();
        for provider in providerModels:
            namePrefix = provider["last_name"][:indexPrefixLength] +","+ provider["first_name"][:indexPrefixLength];
            if namePrefix not in self.providersByNamePrefix:
                self.providersByNamePrefix[namePrefix] = list();  # Store a collection to track collisions between multiple providers who have the same first and last name (prefixes)
            self.providersByNamePrefix[namePrefix].append(provider);

    def inferProvIdFromName(self, name):
        """Assume name is separated by comma into "LastName, FirstName"
        Look through providersByNamePrefix dictionary to look for a best match within first X characters of first and last name
        to back track provider ID. If none found, then fill in a fake ID value.
        """
        provIdsStr = None;

        if self.providersByNamePrefix is not None and self.indexPrefixLength is not None:
            chunks = name.split(",");
            lastName = chunks[0].strip();
            firstName = chunks[-1].strip();
            namePrefix = lastName[:self.indexPrefixLength] +","+ firstName[:self.indexPrefixLength];

            if namePrefix in self.providersByNamePrefix:
                providers = self.providersByNamePrefix[namePrefix];
                provIdsStr = str.join(",", [provider["prov_id"] for provider in providers])
        
        if provIdsStr is None:   # Unable to lookup provider IDs. Just makeup a sequential value then
            self.placeholderIdCounter -= 1; # Decrement counter as working with negative values
            provIdsStr = PLACEHOLDER_ID_TEMPLATE % self.placeholderIdCounter;
        return provIdsStr;

    def compressDateRange( self, startDate, endDate, scheduleItems ):
        """Given a list of schedule item with specific date ranges,
        modify the given start and end date range to avoid overlap with any existing ones.
        Simplifying assumption that overlaps will be at ends, not in middle of range or spanning entirety
        """
        for item in scheduleItems:
            if item["start_date"] < endDate and startDate < item["end_date"]: # Overlap
                if startDate < item["start_date"] :   # Overlap trim at end
                    endDate = item["start_date"];
                elif item["end_date"] < endDate: # Overlap trim at start
                    startDate = item["end_date"];
        return (startDate, endDate);                

    def parseDateRanges(self, textChunks, baseYear):
        textChunks = textChunks[1:];    # Discard first chunk, expect to be an unused label

        dateRanges = list();
        lastDate = datetime(baseYear,1,1);   # Start with the expected base year
        for chunk in textChunks:
            (startText, endText) = chunk.split("-");   # Separate out start from end date
            lastDate = startDate = self.parseDateText( startText, lastDate, 0 );
            lastDate = endDate = self.parseDateText( endText, lastDate, 1 );
            dateRanges.append( (startDate,endDate) );
        return dateRanges;
    
    def parseDateText( self, dateText, lastDate, incrementDays=0 ):
        """Parse the date text into a datetime object, expecting
        missing information on year, so use the lastDate's year value as a reference,
        and expect lastDate to occur previous in time to the new one to catch wrapping around the calendar.
        Option to increment the number of days to account for end date night shifts counting up to the next morning.
        Return the parsed datetime object, which should become the new "lastDate".
        """
        (monthText, dayText) = dateText.strip().split("/");
        dateObj = datetime( lastDate.year, int(monthText), int(dayText), self.changeHour );
        if dateObj < lastDate:    # Date value less than the previous, presumably from calendar year wrapping around
            dateObj = datetime( lastDate.year+1, int(monthText), int(dayText), self.changeHour );
        dateObj += timedelta(incrementDays);
        return dateObj;
    
    def parseSplitDates(self, textChunks, baseYear):
        textChunks = textChunks[1:];    # Discard first chunk, expect to be an unused label

        splitDates = list();
        lastDate = datetime(baseYear,1,1);   # Start with the expected base year
        for chunk in textChunks:
            dateText = chunk.replace("(","").replace(")","").strip();   # Drop flanking parantheses
            lastDate = splitDate = self.parseDateText( dateText, lastDate );
            splitDates.append( splitDate );
        return splitDates;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog <inputFile> <outputFile>\n"+\
                    "   <inputFile>     Tab-delimited input file taken from schedule Excel file. Example data format as seen in test case examples. See support/extractExcelSheets.py for help on pulling out Excel sheets into tab-delimited data files.\n"+\
                    "   <outputFile>    File to output results to.  Designate '-' for stdout.";
        parser = OptionParser(usage=usageStr)
        parser.add_option("-i", "--providerIdFilename",  dest="providerIdFilename", help="Name of provider ID CSV file. If provided, then add column for prov_id based on resident first and last name, match within first several characters, or generate ID value if no match found");
        parser.add_option("-y", "--baseYear",  dest="baseYear", help="Year expect dates to start in.");
        parser.add_option("-t", "--changeTime",  dest="changeTime", default=CHANGE_TIME, help="Hour of day that count as delimiter between rotations. Likely should NOT be midnight = 0, because night shifts span midnight. Default to 7 = 7am.");
        (options, args) = parser.parse_args(argv[1:])

        if len(args) >= 2 and options.baseYear:
            log.info("Starting: "+str.join(" ", argv))
            timer = time.time();

            baseYear = int(options.baseYear);

            inFile = stdOpen(args[0]);
            scheduleItems = self.parseScheduleItems(inFile, baseYear);

            outFile = stdOpen(args[1],"w");
            formatter = TextResultsFormatter(outFile);
            formatter.formatResultDicts(scheduleItems);
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = ResidentScheduleFormat();
    instance.main(sys.argv);
