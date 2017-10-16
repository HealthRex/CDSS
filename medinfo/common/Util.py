#!/usr/bin/env python
"""Miscellaneous utility functions used across the application
"""
import Const, Env
import sys, os
import logging
import urllib;
import time;
import re;
from datetime import datetime, timedelta;
import math;
import json;
from Const import DEFAULT_DATE_FORMATS, NULL_STRING, FALSE_STRINGS;

log = logging.getLogger("CDSS")
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)


def isStdFile(filename):
    """Given a filename, determine if it is meant to represent
    sys.stdin / sys.stdout or just a regular file based on the
    convention of the filename "-" or if parameter left blank / None.
    """
    if filename is None:
        return True;
    else:
        sourceDir, sourceBase = os.path.split(filename)
        return filename == Const.STD_FILE;

def stdOpen(filename,mode="r",stdFile=None):
    """Wrapper around basic file "open" method.  If specified filename
    is recognized as representing stdin or stdout (see "isStdFile")
    then return the designated stdFile object (presumably sys.stdin or sys.stdout).
    
    Also provide automatic unzipping of gzipped files.  If find default
    GZip file extension, will automatically open the file using gzip opener
    for transparent access.
    """
    if stdFile is None:
        if mode.startswith("w"):
            stdFile = sys.stdout;
        else:
            stdFile = sys.stdin
        
    if isStdFile(filename):
        return stdFile
    else:
        if filename.endswith(Const.GZIP_EXT):
            import gzip;
            return gzip.open(filename,mode);
        else:
            return open(filename,mode)

def loadJSONDict(sourceStr, keyType=None, valueType=None):
    """Load a source string as a JSON dictionary.
    Beyond just json.loads, also option to specify expected data types for the keys and values.
    Otherwise JSON forces keys to be strings.
    """
    resultDict = json.loads(sourceStr);
    if keyType is not None and valueType is not None:
        origDict = resultDict;
        resultDict = dict();    # Create a new copy with customized datatypes
        for origKey, origValue in origDict.iteritems():
            newKey = origKey;
            newValue = origValue;
            if keyType is not None: 
                newKey = keyType(origKey);
            if valueType is not None:
                newValue = valueType(origValue);
            resultDict[newKey] = newValue;
    return resultDict;

class ProgressDots:
    """Clone of OEChem OEDots class, to add progress indicator to long processes,
    without actually requiring OEChem as a dependency.
    """
    def __init__( self, big=None, small=None, name="items", stream=sys.stderr, total=None ):
        """Constructor.
        big - Number of updates before completing a progress output line. Leave as None to print every minute
        small - Number of updates before outputting a progress dot. Leave as None to print every second
        name - Name of the items being processed.
        stream - Stream to send progress output to.  Defaults to sys.stderr.
        total - If specified, the total number of items expected to process, so can provide completion estimate
        """
        self.big = big;
        self.small = small;
        self.total = total;
        self.name = name;
        self.stream = stream;
        self.count = 0;
        self.start = time.time();
        self.lastSmallPrintTime = self.getTime(); # Keep track of the last time printed something for feedback
        self.lastBigPrintTime = self.getTime();

        """
        if total is not None:
            # If total estimated size is provided, then adapt big and small progress counter sizes
            #   to be of proportional size to avoid excessively large or small counters.
            if big is None:
                self.big = 10**(int(math.log(total,10))-1);   # Break down into at least 10 big lines (one less log_base10), up to 100
                self.big = max(self.big, Const.PROG_BIG);   # Avoid excessively small counter sizes if working with small files
            if small is None:
                self.small = 10**(int(math.log(total,10))-1) * Const.PROG_SMALL / Const.PROG_BIG;   # Small progress just as standard ratio of dots to the big line
                self.small = max(self.small, Const.PROG_SMALL);   # Avoid excessively small counter sizes
        """


    def Update(self,step=1):    # Overload for backwards compatibility
        self.update(step);
    def update(self,step=1):
        """Update the progress counter by an increment of size step (default=1).
        Well output progress dots or line information to the stream if
        reached an appropriate big or small increment.
        """
        self.count += step;
        if self.small is not None and self.small > 0 and self.count % self.small == 0:
            self.stream.write(".");
        if self.big is not None and self.big > 0 and self.count % self.big == 0:
            self.PrintStatus();

        # If no counter increments specified, do it based on time elapsed since last print
        if self.small is None or self.big is None:
            currTime = self.getTime();
            if self.small is None and (currTime - self.lastSmallPrintTime) > Const.PROG_SMALL_TIME:   # Update at least every 1 second
                self.stream.write(".");
                self.lastSmallPrintTime = currTime;
            if self.big is None and (currTime - self.lastBigPrintTime) > Const.PROG_BIG_TIME:  # Update at least every minute
                self.printStatus();
                self.lastBigPrintTime = currTime;
    
    def GetCounts(self):
        return self.getCounts();
    def getCounts(self):
        """Get the current count of updates"""
        return self.count;
    
    def GetTime(self):
        return self.getTime();
    def getTime(self):
        """Get the time (in seconds) since the progressindicator was created."""
        return time.time()-self.start;

    def PrintStatus(self):
        return self.printStatus();
    def printStatus(self):
        if self.stream is not None:
            secondsElapsed = self.getTime();
            estimateStr = "";
            if self.total is not None and self.total > 0:
                # Total count supplied, provide estimate until completion
                secondsRemaining = 0;
                if self.count > 0:
                    secondsRemaining = (self.total - self.count) * (secondsElapsed / self.count);
                estimateStr = ", ~%s until %d done" % (timedelta(0,round(secondsRemaining)), self.total);
            print >> self.stream, "%d %s after %s%s" % (self.count, self.name, timedelta(0,round(secondsElapsed)), estimateStr );
            self.stream.flush();


def fileLineCount(inputFile):
    """Count up the (remaining) number of lines in an inputFile. 
    Note that this iterates through the lines in the file object, so you will lose your place in the file.
    Presumably you'd have to reopen the file to start over (or use file.tell and file.seek).
    """
    nLines = 0;
    for line in inputFile:
        nLines += 1;
    return nLines;

def parseDateValue(chunk,dateFormat=None):
    """Parse the string chunk into a datetime object using specified or default date format strings
    """
    if chunk == NULL_STRING:
        return None;
    if isinstance(chunk,datetime):
        # Already parsed, no reason to repeat
        return chunk;
    
    dateFormats = list();
    if dateFormat is not None:
        dateFormats.append(dateFormat);
    dateFormats.extend(DEFAULT_DATE_FORMATS);   # Still add default parsers for extra options

    returnValue = chunk;
    for dateFormat in dateFormats:
        try:
            timeTuple = time.strptime(chunk, dateFormat);
            returnValue = datetime(*timeTuple[:6]);
            break;  # No need to try further formats
        except ValueError:
            # Invalid date parsing, likely not matching a format
            pass;   # Just move on to trying next format
    return returnValue;


def isTrueStr(testStr):
    return isNotFalseStr(testStr);
    
def isNotFalseStr(testStr):
    """Simple check to see if input string is NOT any kind of representation of a boolean False, 
    essentially assuming True string
    """
    if testStr is None: return None;
    return (testStr.lower() not in FALSE_STRINGS);

def asciiSafeStr(s, replaceChar="_"):
    """Ensure the given input string can safely be encoded to ASCII.
    If find non-ascii Unicode characters (often symbols or letters with accent marks, etc.),
    then replace those symbols with the given replacement character.
    """
    try:
        s = s.encode('ascii');
    except UnicodeDecodeError:
        s = re.sub(r'[\x80-\xFF]','_', s);
    return s;
