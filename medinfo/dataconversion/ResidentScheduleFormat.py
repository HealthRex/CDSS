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

BASE_YEAR = 2013;   # Year expect dates to start in
CHANGE_HOUR = 7;  # Designate 7am as changeover time rather than midnight, otherwise night shift behavior on change dates will be misinterpreted

class ResidentScheduleFormat:
    """Data conversion module to take Resident Schedule Excel spreadsheet
    and convert into relational data structure to faciltiate subsequent database manipulation and analysis.
    """
    def __init__(self):
        """Default constructor"""
        self.baseYear = BASE_YEAR;
        self.changeHour = CHANGE_HOUR;

    def parseScheduleItems(self, scheduleFile):
        """Given a file reference, parse through contents to generate a list of 
        relational (dictionary) schedule items representing each dated user-rotation schedule component.
        """
        reader = csv.reader(scheduleFile, dialect=csv.excel_tab);  # Assume tab delimited file
        
        # Iterate through header lines until find one that looks like key date row
        # Expect first key line to be the primary date ranges
        row = reader.next();
        while row[-1].isalnum() or row[-1].find("-") < 0:    # Expect date rows formatted like "5/25 - 6/24" so look for a non-alphanumeric row with a '-'' in the middle
            row = reader.next();        
        dateRanges = self.parseDateRanges(row);  

        # Expect next line to be mid-rotation split dates
        row = reader.next();    
        splitDates = self.parseSplitDates(row); 
        
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

                    scheduleItem = {"resident": resident, "rotation": rotation, "start": startDate, "end": endDate};
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
                            scheduleItem = {"resident": resident, "rotation": rotation, "start": startDate, "end": endDate};
                            scheduleItems.append(scheduleItem);

                        rotation = subChunks[-1].strip();
                        if rotation[0].isalpha():   # Ensure starts with a letter, and not special character for blank placeholder
                            (startDate, endDate) = self.compressDateRange( splitDate, dateRange[-1], scheduleItems );  # Start on split date
                            scheduleItem = {"resident": resident, "rotation": rotation, "start": startDate, "end": endDate};
                            scheduleItems.append(scheduleItem);
                    else:   # Single rotation spanning the full block
                        rotation = subChunks[0].strip();
                        if rotation[0].isalpha():   # Ensure starts with a letter, and not special character for blank placeholder
                            (startDate, endDate) = self.compressDateRange( dateRange[0], dateRange[-1], scheduleItems );
                            scheduleItem = {"resident": resident, "rotation": rotation, "start": startDate, "end": endDate};
                            scheduleItems.append(scheduleItem);

            # Now yield / generate results, but keep sorted in chronologic order
            scheduleItems.sort( RowItemFieldComparator("start") );
            for item in scheduleItems:
                yield item;

    def compressDateRange( self, startDate, endDate, scheduleItems ):
        """Given a list of schedule item with specific date ranges,
        modify the given start and end date range to avoid overlap with any existing ones.
        Simplifying assumption that overlaps will be at ends, not in middle of range or spanning entirety
        """
        for item in scheduleItems:
            if item["start"] < endDate and startDate < item["end"]: # Overlap
                if startDate < item["start"] :   # Overlap trim at end
                    endDate = item["start"];
                elif item["end"] < endDate: # Overlap trim at start
                    startDate = item["end"];
        return (startDate, endDate);                

    def parseDateRanges(self, textChunks):
        textChunks = textChunks[1:];    # Discard first chunk, expect to be an unused label

        dateRanges = list();
        lastDate = datetime(self.baseYear,1,1);   # Start with the expected base year
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
    
    def parseSplitDates(self, textChunks):
        textChunks = textChunks[1:];    # Discard first chunk, expect to be an unused label

        splitDates = list();
        lastDate = datetime(self.baseYear,1,1);   # Start with the expected base year
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
        (options, args) = parser.parse_args(argv[1:])

        if len(args) >= 2:
            log.info("Starting: "+str.join(" ", argv))
            timer = time.time();

            inFile = stdOpen(args[0]);
            scheduleItems = self.parseScheduleItems(inFile);

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
