#!/usr/bin/env python
"""Objects to manage different formatting
of results arrays (usually from database calls).
"""
import sys;
import urllib;
import csv; # Does a lot of text table parsing and formatting already
import re;
from Model import RowItemModel;
from medinfo.common.Const import COMMENT_TAG, NULL_STRING;
from Env import CSV_EXPAND_QUOTES;

class ResultsFormatter:
    """Abstract class defining what methods a formatter class should implement
    """
    outFile = None
    def __init__( self, outFile ):
        self.outFile = outFile
        self.groupColumns = False
        self.headerRow = False
        self.currRow = None;
    
    def getOutFile(self):           return self.outFile
    def setOutFile(self,outFile):   self.outFile = outFile

    def getGroupColumns(self):              return self.groupColumns
    def setGroupColumns(self,groupColumns): self.groupColumns = groupColumns

    def getHeaderRow(self):             return self.headerRow
    def setHeaderRow(self,headerRow):   self.headerRow = headerRow

    def formatResultSet( self, results ):
        """Just iteratively call formatTuple for the entire result set.
        
        If groupColumns is true, then, for each item, will check 
        if the item in the immediately preceding tuple was the same.  
        If so, just format a blank string.  However, this only 
        applies if all preceding / higher-order items in the tuple 
        have already been blanked by this same criteria.  For this 
        all to make sense, the columns should sorted by the first
        columns, in the order they appear.
        """
        lastTuple = None
        for self.currRow, tuple in enumerate(results):
            currTuple = tuple
            self.formatTuple(currTuple,lastTuple)
            lastTuple = tuple

    def formatResultDicts(self, resultDicts, columnNames=None, addHeaderRow=False):
        """Instead of printing out a list of lists, print out a list of
        dictionaries' values (RowItemModels).  These will be printed in alphabetical
        order of the column names (dictionary keys) unless a specific set and order
        of columns is specified with the columnNames list parameter.  Similar to
        the formatResultSet method, can option to groupColumns to avoid reprinting
        higher order columns.
        
        addHeaderRow: If set, will output an additional header row of column names
        """
        lastTuple = None
        for self.currRow, rowDict in enumerate(resultDicts):
            if columnNames == None:
                # If column set and order is not specified, just print all columns alphabetically
                columnNames = rowDict.keys()
                columnNames.sort()
            
            if addHeaderRow:
                self.formatTuple(columnNames);
                addHeaderRow = False;   # Reset flag so only doing this once
            
            # Extract dictionary data into a tuple / list
            if not isinstance(rowDict,RowItemModel):
                rowDict = RowItemModel(rowDict)
            tuple = rowDict.valuesByName(columnNames)
            currTuple = tuple
            self.formatTuple(currTuple,lastTuple)
            lastTuple = tuple

    def formatResultDict(self, rowDict, columnNames):
        """Format a single dictionary"""
        if not isinstance(rowDict,RowItemModel):
            rowDict = RowItemModel(rowDict)
        currTuple = rowDict.valuesByName(columnNames)
        self.formatTuple(currTuple);

    def formatTuple( self, tuple, lastTuple=None ):
        """Abstract method, subclasses should override.
        Format the tuple into some string and write it to the outFile.
        """
        raise Exception("Abstract method, should not be called directly")

class TextResultsFormatter(ResultsFormatter):
    """Formatter for reading database output as simple text.
    Defaults to tab-delimited, but can customize.
    Option to escape / URL quote content text to avoid
    special characters (tabs, new lines, etc.) compromising formatting.
    """
    mDelim = None;
    quoteContents = None;
    def __init__(self, outFile, delim=None, quoteContents=False ):
        ResultsFormatter.__init__(self, outFile)
        if delim == None: delim = "\t"  # Default to tab-delimited
        self.mDelim = delim
        self.quoteContents = quoteContents;

    def getDelim(self):         return self.mDelim
    def setDelim(self,delim):   self.mDelim = delim
    
    def formatTuple( self, tuple, lastTuple=None ):
        """Given a result set tuple / row / list, as in from 
        DBUtil.execute(...).fetchXXX(...), write out a 
        representation suitable for text output of one
        line per row, with each column delimited by the 
        delim character.
        """
        tupleLength = len(tuple);
        continueGrouping = self.groupColumns and lastTuple is not None;
        for i, item in enumerate(tuple):
            if self.groupColumns and lastTuple is not None and continueGrouping:
                if item != lastTuple[i]:
                    # Non-match.  Don't try to group anymore
                    continueGrouping = False;
            if not continueGrouping:
                itemText = str(item);
                if self.quoteContents:
                    itemText = urllib.quote(itemText);  # URL quoting to avoid unsafe characters for formatting like tabs or newlines
                self.outFile.write(itemText);
            if i < (tupleLength-1): # Only add delimiters up to the last item
                self.outFile.write(self.mDelim);
        print >> self.outFile # New line

class HtmlResultsFormatter(ResultsFormatter):
    """Formatter for displaying database output in a web table.
    """
    def __init__(self, outFile, headerRowFormat=None, headerColFormat="td", align="left", valign="top", printNone=True, lineSeparators=False ):
        """Initialization constructor.
        outFile: File to write formatted output to.
        headerRowFormat: If non-None, will format the first row differently from the rest, using the format tag specified
        headerColFormat: The first column of each row will be formatted using this tag
        align: All columns will be horizontally aligned according to this parameter.
        """
        ResultsFormatter.__init__(self, outFile)
        self.setHeaderRow(headerRowFormat is not None);
        self.headerRowFormat = headerRowFormat;
        self.headerColFormat = headerColFormat;
        self.align = align;
        self.valign= valign;
        self.printNone = printNone;
        self.lineSeparators = lineSeparators;

    def formatTuple( self, tuple, lastTuple=None ):
        """Given a result set tuple, as in from DBUtil.execute,
        write out a representation  suitable for html output
        with one <tr>...</tr> block per row, with each column
        delimited by <td>...</td> blocks.

        If headerRow was set on instantiation, the first time
        this method is called, the row output will
        formatter based on the specified headerRowFormat.

        This does NOT output the <table> and </table> tags,
        which the caller should manage instead.  This allows
        the caller to set table properties as desired.
        """
        valign = "valign=%s" % self.valign;
        align  = "align=%s" % self.align;
        if self.headerRow: 
            valign = "valign=bottom";
            align = "";
        
        continueGrouping = self.groupColumns and lastTuple is not None;

        if self.lineSeparators != False:
            lineClass = "softLine";
            if isinstance(self.lineSeparators, str):
                lineClass = self.lineSeparators;
            print >> self.outFile, '<tr><td colspan=100 class="%s" height=1></td></tr>' % lineClass;
        print >> self.outFile, "<tr %s %s>" % (valign, align);
        for i, item in enumerate(tuple):
            if self.headerRow:
                self.outFile.write("    <%s>" % self.headerRowFormat)
                self.outFile.write(str(item))
                self.outFile.write("</td>")
                print >> self.outFile
            else:
                if self.groupColumns and lastTuple is not None and continueGrouping:
                    if item != lastTuple[i]:
                        # Non-match.  Don't try to group anymore
                        continueGrouping = False;
                    else:
                        print >> self.outFile, "    <td></td>";
                if not continueGrouping:
                    #rowspan = self.__determineRowspan(i);
                    if i == 0:
                        self.outFile.write("    <%s>" % (self.headerColFormat) );
                    else:
                        self.outFile.write("    <td>" )
                    if item is not None or self.printNone:
                        self.outFile.write(str(item))
                    self.outFile.write("</td>")
                    print >> self.outFile
        print >> self.outFile, "</tr>"
        self.headerRow = False # Only the first tuple should be the "header"


class TabDictReader(csv.DictReader):
    """Extension to csv.DictReader but with custom options setup
    to read tab-delimited files into a dictionary object for each row,
    keyed by the header values in the first row.
    Furthermore, will look for and skip any lines starting with the COMMENT_TAG and
    strip any flanking whitespace.
    """
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect=None, delimiter=None, *args, **kwds):
        self.commentLines = list(); # Track comment lines
        self.firstLine = None;  # Track the first non-comment line
        
        if dialect is None:
            dialect = csv.excel_tab;
        if delimiter is None:
            delimiter = "\t";
        lineGenerator = self.lineGenerator(f, delimiter);
        csv.DictReader.__init__(self, lineGenerator, fieldnames=fieldnames, restkey=restkey, restval=restval, dialect=dialect, delimiter=delimiter, *args, **kwds);
    
    def lineGenerator(self, f, delimiter):
        # Generator expression to drop lines that start with comment tag
        # http://stackoverflow.com/questions/14158868/python-skip-comment-lines-marked-with-in-csv-dictreader
        for line in f:
            if line.startswith(COMMENT_TAG):
                self.commentLines.append(line);
            else:
                if self.firstLine is None:
                    self.firstLine = line;
                cleanLine = line.strip(" \r\n");  # Lose flanking spaces or newlines (but avoid removing things like tabs that may represent column delimiters)
                if delimiter == ",":   # May need special quote processing, unless tab-delimited probably fine???
                    if CSV_EXPAND_QUOTES:
                        cleanLine = re.sub(r'([^%(delim)s"])"([^%(delim)s"])' % {"delim": delimiter}, r'\1""\2', cleanLine);    # Make sure internal quotes are double-quoted
                        cleanLine = re.sub(r'([^%(delim)s"])""%(delim)s' % {"delim": delimiter}, r'\1"""%(delim)s' % {"delim": delimiter}, cleanLine); # Double (but not triple) quotes next to a delimiter doesn't make sense, must mean a quote charater intended
                        cleanLine = re.sub(r'%(delim)s""([^%(delim)s"])' % {"delim": delimiter}, r'%(delim)s"""\1' % {"delim": delimiter}, cleanLine); # Double (but not triple) quotes next to a delimiter doesn't make sense, must mean a quote charater intended
                    pass;
                #print >> sys.stderr, line;
                #print >> sys.stderr, cleanLine;
                yield cleanLine;

def pandas_read_table(infile, *args, **kwds):
    """Simple wrapper function for default arguments to read a pandas dataframe 
    from a tab-delimited file and ignoring comment lines.
    """
    import pandas as pd;    # Only import as needed
    return pd.read_table(infile, comment=COMMENT_TAG, na_values=[NULL_STRING], *args, **kwds);

def tab2df(infile, *args, **kwds):
    """Synonym function that may be more intuitive"""
    return pandas_read_table(infile, *args, **kwds);
    
def pandas_write_table(df, outfile, *args, **kwds):
    """Simple wrapper function to output pandas dataframe contents
    to a tab-delimited output file.
    """
    outfile.write(df.to_csv(sep='\t',index=False, na_rep=NULL_STRING, *args, **kwds));

def df2tab(df, outfile, *args, **kwds):
    """Synonym function that may be more intuitive"""
    return pandas_write_table(df, outfile, *args, **kwds);
    

def sanitizeNames(names):
    """Given a list of name strings, 
    replace any non-alphanumerics with underscore _.
    Lowercase characters only
    Also ensure unique column names (append numerical suffixes if duplicates)
    """
    newNames = list();
    newNameSet = set();
    for i, oldName in enumerate(names):
        newColChars = list();
        for char in oldName:
            if char.isalnum():
                newColChars.append(char);
            else:
                newColChars.append("_");
        newName = str.join("", newColChars);
        newName = newName.lower();
        if newName in newNameSet:    # Duplicates, start trying modifying with suffixes
            iSuffix = 1;
            modName = "%s_%s" % (newName,iSuffix);
            while modName in newNameSet:
                iSuffix += 1
                modName = "%s_%s" % (newName,iSuffix);
            newName = modName;  # Found one not a duplicate
        newNames.append(newName);
        newNameSet.add(newName);
    return newNames;

def pandas_to_sqlconn(df, tableName="data", conn=None):
    """Turning pandas dataframe into SQL queryable in memory object
    Column names will be cleaned up as per sanitizeNames.
    https://plot.ly/python/big-data-analytics-with-pandas-and-sqlite/
    Returns connection to the SQL object.
    """
    import sqlite3;   # Only import as needed
    if conn is None:
        #conn = create_engine("sqlite:///:memory:");    # In memory database
        conn = sqlite3.connect(":memory:"); # In memory database
    
    # Sanitize column names
    df.columns = sanitizeNames(df.columns);
    
    df.to_sql(tableName, conn, if_exists='replace');
    return conn;

def df2sql(df, tableName="data", conn=None):
    """Synonym function that may be more intuitive"""
    return pandas_to_sqlconn(df, tableName, conn);


def pandas_read_sql_query(query, conn):
    """To query dataframes back out,
    just enter a SQL query, using "data" as the source table name
    (unless a different one was specified in the dataframe_to_sqlconn) process.
    For example:
        select *
        from data
        where col1 = 1
        limit 10
    """
    import pandas as pd; # Only Import as needed
    return pd.read_sql_query(query, conn);
    
def sql2df(query, conn):
    """Synonym function that may be more intuitive"""
    return pandas_read_sql_query(query, conn);

