#!/usr/bin/env python
"""Test case for respective module in medinfo.Common package"""

import sys, os
from cStringIO import StringIO
import unittest

from datetime import datetime;

from Const import LOGGER_LEVEL, RUNNER_VERBOSITY;
from Util import log;

from Util import DBTestCase;

from medinfo.common.test.Util import MedInfoTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

# String representations for boolean values
TRUE_STR = "1";
FALSE_STR = "0";
# PostgreSQL uses "t" and "f"


class TestDBUtil(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

        self.SCRIPT_FILE = StringIO()
        self.SCRIPT_FILE.write("# Create table to test on.  Also testing that comment tag is recognized\n")
        self.SCRIPT_FILE.write("\n")
        self.SCRIPT_FILE.write("create table TestTypes\n")
        self.SCRIPT_FILE.write("(\n")
        self.SCRIPT_FILE.write("    TestTypes_id    serial,\n")
        self.SCRIPT_FILE.write("    MyText          varchar(50),    /* Same as character varying, also test standard SQL comment tags */\n")
        self.SCRIPT_FILE.write("    MyInteger       integer,\n")
        self.SCRIPT_FILE.write("    MyReal          real,   -- Floating point number, also test standard SQL comment tag\n")
        self.SCRIPT_FILE.write("    MyDateTime      TIMESTAMP,   -- PostgreSQL uses TIMESTAMP, but MySQL doesn't do NULL values right, so have to use DATETIME for MySQL?\n")
        self.SCRIPT_FILE.write("    MyYesNo         boolean\n")
        self.SCRIPT_FILE.write(");\n")
        self.SCRIPT_FILE.write("ALTER TABLE TestTypes ADD CONSTRAINT TestTypes_id PRIMARY KEY (TestTypes_id);\n");  # Should auto-create testtypes_testtypes_id_seq sequence
        self.SCRIPT_FILE.write("CREATE INDEX TestTypes_MyInteger_INDEX ON TestTypes(MyInteger);\n")
        self.SCRIPT_FILE.write("\n")
        self.SCRIPT_FILE.write("insert into TestTypes (MyText,MyInteger,MyReal,MyDateTime,MyYesNo)\n")
        self.SCRIPT_FILE.write("values ('Sample Text',  123,123.45,'2004-09-08 19:41:47.292000',True);\n")
        self.SCRIPT_FILE.write("insert into TestTypes (MyText,MyInteger,MyReal,MyDateTime,MyYesNo)\n")
        self.SCRIPT_FILE.write("values ('Joe Mama',     234,23.45,'1990-10-03 19:41:47.292000',False);\n")
        self.SCRIPT_FILE.write("insert into TestTypes (MyText,MyInteger,MyReal,MyDateTime,MyYesNo)\n")
        self.SCRIPT_FILE.write("values ('Mo Fo',        345,3.45,'2014-01-04 19:41:47.292000',True);\n")
        self.SCRIPT_FILE.write("\n")
        self.SCRIPT_FILE = StringIO(self.SCRIPT_FILE.getvalue())

        self.DATA_TABLE= "TestTypes";
        self.DATA_COLS = "MyInteger\tMyReal\tMyYesNo\tMyText\n";

        self.DATA_FILE = StringIO()
        self.DATA_FILE.write('100\t100.1\tNone\tATest\n');
        self.DATA_FILE.write('200\t200.2\t'+FALSE_STR+'\tNone\n');
        self.DATA_FILE.write('200\t200.2\t'+FALSE_STR+'\t\n');  # Skip None tag at end of line, test that white space won't get lost
        self.DATA_FILE.write('300\t\t'+TRUE_STR+'\tCTest\n');
        self.DATA_FILE = StringIO(self.DATA_FILE.getvalue())

        self.DATA_ROWS = [];
        self.DATA_ROWS.append([100,100.1,None,  "ATest",]);
        self.DATA_ROWS.append([200,200.2,False, None,]);
        self.DATA_ROWS.append([300,None,True,  "CTest",]);

        self.MULTI_LINE_DATA_FILE = StringIO()
        self.MULTI_LINE_DATA_FILE.write('myinteger\t"MyReal"\t"MyYesNo"\tMyText\n');
        self.MULTI_LINE_DATA_FILE.write('100\t100.1\tNone\t"""A"" Test and ""more"""\n');
        self.MULTI_LINE_DATA_FILE.write('200\t200.2\t'+FALSE_STR+'\t""\n');
        self.MULTI_LINE_DATA_FILE.write('300\tNone\t'+TRUE_STR+'\t"C\\nTest"\t\n');
        self.MULTI_LINE_DATA_FILE = StringIO(self.MULTI_LINE_DATA_FILE.getvalue())

        self.MULTI_LINE_DATA_ROWS = [];
        self.MULTI_LINE_DATA_ROWS.append([100,100.1,None,  '"A" Test and "more"',]);
        self.MULTI_LINE_DATA_ROWS.append([200,200.2,False, None,]);
        self.MULTI_LINE_DATA_ROWS.append([300,None,True,  'C\\nTest',]);

        # ID summary data to make it easier to verify stuff
        self.COL_NAMES = self.DATA_COLS.split();
        self.ID_COL = self.COL_NAMES[0];
        self.ID_DATA = [];
        for row in self.DATA_ROWS:
            self.ID_DATA.append(row[0]);

        # Build query to get update rows
        self.DATA_QUERY = SQLQuery();
        for col in self.COL_NAMES:
            self.DATA_QUERY.addSelect(col);
        self.DATA_QUERY.addFrom(self.DATA_TABLE);
        self.DATA_QUERY.addWhereIn(self.ID_COL,self.ID_DATA);
        self.DATA_QUERY.addOrderBy(self.ID_COL);



    def tearDown(self):
        """Restore state from any setUp or test steps"""
        try:
            DBUtil.execute("drop table TestTypes")
            pass
        except Exception, err:
            log.warning(err)
            pass

        DBTestCase.tearDown(self);

    def test_runDBScript(self):
        # Just run a DB Script and make sure no ProgrammingErrors are raised.
        DBUtil.runDBScript( self.SCRIPT_FILE, False )

        # Run some other commands to see if scripts produced expected results
        results = DBUtil.execute("select * from TestTypes where MyInteger > %s", (200,))
        self.assertEqual( 2, len(results) )

        # Test extra "includeColumnNames" parameter
        results = DBUtil.execute("select TestTypes_id,MyText,MyInteger,MyReal,MyDateTime,MyYesNo from TestTypes where MyInteger < %s", (100,), True)
        expected = ["TestTypes_id","MyText","MyInteger","MyReal","MyDateTime","MyYesNo"]
        for iCol in range(len(expected)):       # Ignore case for comparison
            expected[iCol] = expected[iCol].lower();
            results[0][iCol] = results[0][iCol].lower();
        self.assertEqual( expected, results[0] )
        self.assertEqual( 0, len(results)-1 )


    def test_runDBScript_commandline(self):
        # Equivalent to test_runDBScript, but try higher level interface
        #   through command-line "main" method
        origStdin = sys.stdin
        sys.stdin = self.SCRIPT_FILE
        argv = ["DBUtil.py","--script","-"]
        DBUtil.main(argv)
        sys.stdin = origStdin

        # Run some other commands to see if scripts produced expected results
        results = DBUtil.execute("select * from TestTypes where MyInteger > %s", (200,))
        self.assertEqual( 2, len(results) )

        results = DBUtil.execute("select * from TestTypes where MyInteger < %s", (100,))
        self.assertEqual( 0, len(results) )

    def test_runDBScript_skipErrors(self):
        # Similar to test_runDBScript_commandline, but test skipErrors option
        origStdin = sys.stdin
        sys.stdin = self.SCRIPT_FILE
        argv = ["DBUtil.py","--script","-"]
        DBUtil.main(argv)
        sys.stdin = origStdin

        # Run script again.  Should generate errors from redundant create table, etc.  But skip
        self.SCRIPT_FILE.seek(0)
        origStdin = sys.stdin
        sys.stdin = self.SCRIPT_FILE
        argv = ["DBUtil.py","--script","--skipErrors","-"]
        DBUtil.main(argv)
        sys.stdin = origStdin

        # Run script again.  Should generate errors from redundant create table, etc.  Verify by catch
        self.SCRIPT_FILE.seek(0)
        origStdin = sys.stdin
        sys.stdin = self.SCRIPT_FILE
        argv = ["DBUtil.py","--script","-"]
        expectErr = True
        actualErr = False
        try:
            DBUtil.main(argv)
        except Exception, err:
            actualErr = True
        self.assertEqual(expectErr,actualErr)
        sys.stdin = origStdin


    def test_execute_commandline(self):
        # Run basic executes for both an update and a select query, but
        #   using the higher-level command-line "main" method interface

        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        origStdout  = sys.stdout
        sys.stdout  = StringIO()
        argv = ["DBUtil.py","select count(*) from TestTypes where MyInteger > 200","-"]
        DBUtil.main(argv)
        self.assertEqual( 2, int(sys.stdout.getvalue()) )
        sys.stdout  = origStdout

        origStdout  = sys.stdout
        sys.stdout  = StringIO()
        argv = ["DBUtil.py","insert into TestTypes (MyText,MyInteger,MyYesNo) values ('Another',255,True)","-"]
        DBUtil.main(argv)
        #self.assertEqual( 1, int(sys.stdout.getvalue()) )
        sys.stdout  = origStdout

        origStdout  = sys.stdout
        sys.stdout  = StringIO()
        argv = ["DBUtil.py","select count(*) from TestTypes where MyInteger > 200","-"]
        DBUtil.main(argv)
        self.assertEqual( 3, int(sys.stdout.getvalue()) )
        sys.stdout  = origStdout

        # Different test, includeColumnNames
        origStdout  = sys.stdout
        sys.stdout  = StringIO()
        argv = ["DBUtil.py","-c","select TestTypes_id,MyText,MyInteger,MyReal,MyDateTime,MyYesNo from TestTypes where MyInteger > 200 and MyYesNo = True","-"]
        DBUtil.main(argv)
        sampleLines = sys.stdout.getvalue().split("\n")
        expected = ["TestTypes_id","MyText","MyInteger","MyReal","MyDateTime","MyYesNo"]
        sampleColumns = sampleLines[0].split()
        for iCol in range(len(expected)):   # Case-insensitive comparison
            expected[iCol] = expected[iCol].lower()
            sampleColumns[iCol] = sampleColumns[iCol].lower();
        for iCol, col in enumerate(sampleColumns):
            self.assertEqual(expected[iCol],col)
        self.assertEqual( 2+1+1, len(sampleLines) ) # 2 data lines + 1 column name line + 1 newline at end of output
        sys.stdout  = origStdout

    def test_insertFile(self):
        # Create a test data file to insert, and verify no errors
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        tableName = "TestTypes"

        idFile = StringIO()

        DBUtil.insertFile( self.MULTI_LINE_DATA_FILE, tableName, None, "\t", idFile );  # Assume column names extracted from first row of data file

        # Verify number rows inserted
        self.assertEqual( len(self.MULTI_LINE_DATA_ROWS), idFile.getvalue().count("\n") )
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertEqual( self.MULTI_LINE_DATA_ROWS, results );

    def test_insertFile_commandline(self):
        # Similar to test_insertFile, but from higher-level command-line interface
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        tableName = "TestTypes"
        columnNames = self.DATA_COLS.split();

        idFile = StringIO()

        # Slightly different test, specify tab as delimiter, not just any whitespace
        origStdin = sys.stdin
        origStdout = sys.stdout
        sys.stdin = self.MULTI_LINE_DATA_FILE
        sys.stdout = idFile
        argv = ["DBUtil.py","-i-","-d\\t","-t"+tableName,"-o-"]
        DBUtil.main(argv)
        sys.stdout = origStdout
        sys.stdin = origStdin

        self.assertEqual( 3, idFile.getvalue().count("\n") )
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertEqual( self.MULTI_LINE_DATA_ROWS, results );

    def test_insertFile_skipErrors(self):
        # Similar to test_insertFile_commandline, but just test to see if skipErrors option works
        # Test run will show errror / warning messages from the app, but these are expected
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        tableName = "TestTypes"
        columnNames = ["MyReal","MyYesNo","MyText","MyInteger"]

        idFile = StringIO()

        # Try with bogus data that should generate errors

        dataFile = StringIO()
        dataFile.write("ABCD\tPositive\tBadTest\t100.123\n");
        dataFile.write("700.7\t"+FALSE_STR+"\tXTest\t777\n");
        dataFile.write("1,099\tNegative\tMoBadTest\tfoo\n");
        dataFile = StringIO(dataFile.getvalue())

        idFile = StringIO()

        origStdin = sys.stdin
        origStdout = sys.stdout
        sys.stdin = dataFile
        sys.stdout = idFile
        argv = ["DBUtil.py","-i-","-t"+tableName,"-o-"]
        argv.extend(columnNames)
        expectErr = True
        actualErr = False
        try:
            DBUtil.main(argv)
        except Exception, err:
            actualErr = True
        self.assertEqual(expectErr,actualErr)
        sys.stdout = origStdout
        sys.stdin = origStdin

        # Expect no rows succesffuly inserted since errors in input
        self.assertEqual( 0, idFile.getvalue().count("\n") )
        results = DBUtil.execute("select count(*) from TestTypes where MyText like %s",("%Test",))
        self.assertEqual( 0, results[0][0] )


        # Try again, with bogus data that should generate errors
        dataFile = StringIO()
        dataFile.write("ABCD\tPositive\tBadTest\t100.123\n");
        dataFile.write("700.7\t"+FALSE_STR+"\tXTest\t777\n");
        dataFile.write("1,099\tNegative\tMoBadTest\tfoo\n");
        dataFile = StringIO(dataFile.getvalue())

        idFile = StringIO()

        origStdin = sys.stdin
        origStdout = sys.stdout
        sys.stdin = dataFile
        sys.stdout = idFile
        argv = ["DBUtil.py","-i-","-t"+tableName,"-o-","-e"]    # -e option skipsErrors
        argv.extend(columnNames)
        DBUtil.main(argv)
        sys.stdout = origStdout
        sys.stdin = origStdin

        # Still expect 1 row to get through successfuly, despite other invalid input
        self.assertEqual( 1, idFile.getvalue().count("\n") )
        results = DBUtil.execute("select count(*) from TestTypes where MyText like %s",("%Test",))
        self.assertEqual( 1, results[0][0] )

    def test_insertFile_dateParsing(self):
        # Create a test data file to insert, and verify no errors
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        tableName = "TestTypes"
        columnNames = ["MyInteger","MyText","MyDateTime"]

        dataFile = StringIO()
        dataFile.write('''-1\t"12/11/2010"\t"12/11/2010"\n''');
        dataFile.write('''-2\t"2013-04-15 13:45:21"\t"2013-04-15 13:45:21"\n''');
        dataFile.write('''-3\t"2003-04-15 10:45:21"\t"2003-04-15 10:45:21"\n''');
        dataFile.write('''-4\t"4/11/12 6:20"\t"4/11/12 6:20"\n''');
        dataFile = StringIO(dataFile.getvalue())


        dateColFormats = {"myDateTime":None}    # Deliberately change capitalization to ensure robustness
        DBUtil.insertFile( dataFile, tableName, columnNames, dateColFormats=dateColFormats)

        verifyQuery = \
            """select MyInteger, MyText, MyDateTime
            from TestTypes
            where MyInteger < 0
            order by MyInteger desc
            """;

        expectedData = \
            [   [   -1, "12/11/2010", datetime(2010,12,11)  ],
                [   -2, "2013-04-15 13:45:21", datetime(2013,4,15,13,45,21) ],
                [   -3, "2003-04-15 10:45:21", datetime(2003,4,15,10,45,21) ],
                [   -4, "4/11/12 6:20", datetime(2012,4,11,6,20) ],
            ];

        # Verify rows inserted with properly parsed dates
        results = DBUtil.execute(verifyQuery);
        self.assertEqual( expectedData, results );

    def test_insertFile_escapeStrings(self):
        # Create a test data file to insert, and verify no errors
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        tableName = "TestTypes"
        columnNames = ["MyInteger","MyText"]

        dataFile = StringIO()
        dataFile.write('''-1\t"A"\n''');
        dataFile.write('''-2\t"B\xaeb"\n''');
        dataFile.write('''-3\t"C"\n''');
        dataFile.write('''-4\tD\n''');
        dataFile = StringIO(dataFile.getvalue())

        DBUtil.insertFile( dataFile, tableName, columnNames, escapeStrings=True);

        verifyQuery = \
            """select MyInteger, MyText
            from TestTypes
            where MyInteger < 0
            order by MyInteger desc
            """;

        expectedData = \
            [   [   -1, "A"],
                [   -2, u"B\\xaeb"],
                [   -3, "C"],
                [   -4, "D"],
            ];

        # Verify rows inserted with properly parsed dates
        results = DBUtil.execute(verifyQuery);
        self.assertEqual( expectedData, results );

    def test_identityQuery(self):
        DBUtil.runDBScript( self.SCRIPT_FILE, False )

        # Run some other commands to see if scripts produced expected results
        results = DBUtil.execute("select max(TestTypes_id) from TestTypes");
        lastSeq = results[0][0]

        conn = DBUtil.connection()
        try:
            cur  = conn.cursor()
            cur.execute("insert into TestTypes (MyText,MyInteger,MyYesNo) values ('Another',255,True)")
            cur.execute( DBUtil.identityQuery("TestTypes") )
            self.assertEqual( lastSeq+1, cur.fetchone()[0] )

            cur.execute("select TestTypes_id from TestTypes where MyText = 'Another' and MyInteger = 255")
            self.assertEqual( lastSeq+1, cur.fetchone()[0] )
        finally:
            conn.close()

    def test_nullCheck(self):
        DBUtil.runDBScript( self.SCRIPT_FILE, False )

        conn = DBUtil.connection()
        try:
            DBUtil.execute("insert into TestTypes (MyText,MyInteger) values ('Test With Null', 255)",conn=conn);
            DBUtil.execute("insert into TestTypes (MyText,MyInteger,MyReal,MyDateTime) values ('Test With Not Null', 255, 1.23, '2005-03-06')",conn=conn);

            result = DBUtil.execute("select MyText from TestTypes where MyInteger = 255 and MyReal is null",conn=conn);
            self.assertEqual('Test With Null', result[0][0] )
            result = DBUtil.execute("select MyText from TestTypes where MyInteger = 255 and MyReal is not null",conn=conn);
            self.assertEqual('Test With Not Null', result[0][0] )

            # Would not work with MySQL if used TIMESTAMP data type.  Should be DATETIME.  (TIMESTAMP tries to auto-fill values, so no nulls allowed?)
            result = DBUtil.execute("select MyText from TestTypes where MyInteger = 255 and MyDateTime is null",conn=conn);
            self.assertEqual('Test With Null', result[0][0] )
            result = DBUtil.execute("select MyText from TestTypes where MyInteger = 255 and MyDateTime is not null",conn=conn);
            self.assertEqual('Test With Not Null', result[0][0] )

        finally:
            conn.close()

    def test_findOrInsertItem(self):
        DBUtil.runDBScript( self.SCRIPT_FILE, False )

        searchDict = {}
        insertDict = {}

        searchDict["TestTypes_id"] = +123
        log.debug("Insert a new item using default params")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict)
        self.assertEqual(+123,data)
        self.assertEqual(True,isNew)

        log.debug("Find the existing item")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict)
        self.assertEqual(+123,data)
        self.assertEqual(False,isNew)

        insertDict["TestTypes_id"] = +456
        log.debug("Find existing item, with optional insert data")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict, insertDict)
        self.assertEqual(+123,data)
        self.assertEqual(False,isNew)

        searchDict["TestTypes_id"] = +789
        insertDict["TestTypes_id"] = +789
        insertDict["MyInteger"] = 123
        log.debug("Insert a new item with actual data")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict, insertDict)
        self.assertEqual(+789,data)
        self.assertEqual(True,isNew)

        searchDict["TestTypes_id"] = +234
        insertDict["TestTypes_id"] = +234
        log.debug("Retrieve a different column")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict, insertDict, retrieveCol="MyText")
        self.assertEqual(None,data)
        self.assertEqual(True,isNew)

        searchDict["TestTypes_id"] = +345
        insertDict["TestTypes_id"] = +345
        insertDict["MyText"] = "testText"
        log.debug("Insert and retrieve a different column")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict, insertDict, retrieveCol="MyText")
        self.assertEqual("testText",data)
        self.assertEqual(True,isNew)

        insertDict["MyText"] = "newText";
        log.debug("Try inserting a different value under an existing row.  Should NOT work")
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict, insertDict, retrieveCol="MyText")
        self.assertEqual("testText",data)
        self.assertEqual(False,isNew)

        log.debug("Try inserting a different value under an existing row, but force the update")
        insertDict["MyText"] = "newText";
        (data,isNew) = DBUtil.findOrInsertItem("TestTypes", searchDict, insertDict, retrieveCol="MyText", forceUpdate=True)
        self.assertEqual("newText",data)
        self.assertEqual(False,isNew)


    def test_updateFromFile(self):
        # Create a test data file to insert, and verify no errors
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        # Insert some blank data first to update
        for idValue in self.ID_DATA:
            DBUtil.execute("insert into TestTypes ("+self.ID_COL+") values (%s)",(idValue,));

        # Negative test case
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertNotEqual( self.DATA_ROWS, results );

        # Now do the actual update from the file
        DBUtil.updateFromFile( self.DATA_FILE, self.DATA_TABLE, self.COL_NAMES, delim="\t" );

        results = DBUtil.execute( self.DATA_QUERY );
        self.assertEqual( self.DATA_ROWS, results );


    def test_updateFromFile_commandline(self):
        # Similar to test_updateFromFile, but from higher-level command-line interface
        DBUtil.runDBScript( self.SCRIPT_FILE, False ) # Assume this works based on test_runDBScript method

        # Insert some blank data first to update
        for idValue in self.ID_DATA:
            DBUtil.execute("insert into TestTypes ("+self.ID_COL+") values (%s)",(idValue,));

        # Negative test case
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertNotEqual( self.DATA_ROWS, results );

        # Now do the actual update from the file, but build in column names to data file
        dataFileWithCols = StringIO();
        dataFileWithCols.write(self.DATA_COLS);
        dataFileWithCols.write(self.DATA_FILE.getvalue());
        dataFileWithCols = StringIO(dataFileWithCols.getvalue());

        sys.stdin = dataFileWithCols;
        argv = ["DBUtil.py","-u-","-t"+self.DATA_TABLE,"-d\\t"]
        DBUtil.main(argv)

        # Verify positive results
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertEqual( self.DATA_ROWS, results );

        ########################################################
        # Repeat test but data file will use more than one key column (adding MyText)
        # Further note that MyText is used as both a key column to look up the row to update
        #   and as a value column to modify
        dataFileWithCols = StringIO()
        dataFileWithCols.write("MyInteger\tMyText\tMyText\tMyReal\tMyYesNo\n");
        dataFileWithCols.write("100\tATest\tAAA\tNone\t"+TRUE_STR+"\t\n");
        dataFileWithCols.write("200\tNone\tBBB\t222.2\tNone\t\n");
        dataFileWithCols.write("300\tCTest\tNone\t333.3\t"+TRUE_STR+"\t\n");
        dataFileWithCols = StringIO(dataFileWithCols.getvalue())

        # Expected results after this update
        self.DATA_ROWS = [];
        self.DATA_ROWS.append([100,None, True, "AAA",]);
        self.DATA_ROWS.append([200,200.2,False, None,]); # This row is unchanged, because one of the key values cannot be found as null
        self.DATA_ROWS.append([300,333.3,True,  None,]);

        # Negative test case
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertNotEqual( self.DATA_ROWS, results );

        # Now do the actual update from the file, but with an extra parameter specifying 2 key columns
        sys.stdin = dataFileWithCols;
        argv = ["DBUtil.py","-u-","-t"+self.DATA_TABLE,"-n2"]
        DBUtil.main(argv)

        # Verify positive results
        results = DBUtil.execute( self.DATA_QUERY );
        self.assertEqual( self.DATA_ROWS, results );

    def test_deleteRows(self):
        DBUtil.runDBScript( self.SCRIPT_FILE, False );

        query = "select count(*) from TestTypes;";

        # Insert some test data to delete
        tableName = "TestTypes"
        columnNames = self.DATA_COLS.split();

        idFile = StringIO()
        DBUtil.insertFile( self.DATA_FILE, tableName, columnNames, None, idFile )
        idValues = idFile.getvalue().split();

        # Count up rows before and after delete
        initialCount = DBUtil.execute( query )[0][0];
        DBUtil.deleteRows("TestTypes", idValues);
        afterCount = DBUtil.execute( query )[0][0];

        self.assertEqual( initialCount-len(idValues), afterCount );

        # Reinsert the test data to try deleting them by a non-default Id column
        idFile = StringIO()
        DBUtil.insertFile( self.DATA_FILE, tableName, columnNames, None, idFile )

        nonDefaultIds = [100,200];
        initialCount = DBUtil.execute( query )[0][0];
        DBUtil.deleteRows("TestTypes", nonDefaultIds, "MyInteger");
        afterCount = DBUtil.execute( query )[0][0];


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestDBUtil("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestDBUtil("test_insertFile_skipErrors"));
    #suite.addTest(TestDBUtil('test_insertFile_dateParsing'));
    #suite.addTest(TestDBUtil('test_deleteRows'));
    suite.addTest(unittest.makeSuite(TestDBUtil));
    return suite;

if __name__=="__main__":
    log.setLevel(LOGGER_LEVEL)

    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
