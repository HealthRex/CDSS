#!/usr/bin/env python

# Placeholder character for dynamic SQL queries
SQL_PLACEHOLDER = "?";  

class SQLQueryExample:
    """Application module with example function to implement and test.
    """
    conn = None; # Database connection to read from
    
    def __init__(self, conn):
        """Initialization constructor to specify database connection source"""
        self.conn = conn;

    def queryTrackCounts(self, options):
        """Query sample Chinook database for track counts for artists based on different criteria
        specified in the options.
        
        More information and data schema for Chinook sample database: 
          http://www.sqlitetutorial.net/sqlite-sample-database/
        
        Return columns should be the following:
        - ArtistId
        - Name (artist)
        - Number of Albums for the Artist
        - Number of Tracks within those Albums

        Query options is a dictionary with key-values including:
        - artistPrefix: Only retrieve artists whose name starts with this prefix string
        - invoiceDateStart: Count only tracks which were sold (have a dated invoice) on or after this date
        - invoiceDateEnd: Count only tracks which were sold (have a dated invocie) before this date
        - sortField: Sort criteria (name of column to sort by, optionally followed by "desc" for descending order)
        """
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################

        # queryStr = ???
        # queryParams = ???

        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################

        cursor = self.conn.cursor();
        cursor.execute(queryStr, queryParams);
        results = cursor.fetchall();
        cursor.close();

        return results;

class SQLQuery:
    """Helper class to dynamically build a SQL statement.
    Unlike just appending to a string, allows for addition
    of select, from, where, etc. clauses in any order,
    then generate them in normal order at the end.

    When ready to use, simply convert to a string with placeholders and pass the list of respective parameters
    For example:
        query = SQLQuery();
        query.addSelect("sampleColumn");
        query.addFrom("sampleTable");
        query.addWhereOp("sampleColumn",">", 1000);

        conn = <<<DatabaseConnection>>>;    # Environment specific database connection
        cursor = conn.cursor();
        cursor.execute( str(query), query.getParams() );
    """
    def __init__(self, sqlPlaceholder=SQL_PLACEHOLDER):
        """Allow specification of specific SQL_PLACEHOLDER character. (Different modules use ? vs. %s, etc.)
        """
        self.prefix = None;
        self.delete = False;    # If set, will ignore the select list and make a delete query instead
        self.select = [];
        self.into   = None;
        self.from_  = [];
        self.where  = [];
        self.groupBy= [];
        self.having = [];
        self.orderBy= [];
        self.limit  = -1;
        self.offset = -1;
        self.params = [];
        self.sqlPlaceholder = sqlPlaceholder;

    def setPrefix(self,aPrefix):
        self.prefix = aPrefix;

    def addSelect(self,aSelect):
        self.select.append(aSelect)
    
    def setInto(self,aInto):
        self.into = aInto;

    def addFrom(self,aFrom):
        self.from_.append(aFrom)
    
    def addJoin(self, table, criteria, joinType="INNER"):
        self.from_.append(None);    # Sentinel value to reflect specific join phrase instead of usual comma-separated FROM clause
        self.from_.append("%s JOIN %s\nON %s" % (joinType, table, criteria) );

    def addWhere(self,aWhere):
        self.where.append(aWhere);
    
    def addWhereEqual(self,field,param):
        self.where.append("%s = %s" % (field,self.sqlPlaceholder));
        self.params.append(param);

    def addWhereNotEqual(self,field,param):
        self.where.append("%s <> %s" % (field,self.sqlPlaceholder));
        self.params.append(param);

    def addWhereLike(self,field,param):
        self.where.append("%s like %s" % (field,self.sqlPlaceholder));
        self.params.append(param);

    def addWhereOp(self,field,op,param):
        self.where.append("%s %s %s" % (field,op,self.sqlPlaceholder));
        self.params.append(param);

    def addWhereIn(self,field,paramList):
        placeholders = generatePlaceholders(len(paramList))
        self.where.append("%s IN (%s)" % (field,placeholders));
        self.params.extend(paramList);

    def addWhereNotIn(self,field,paramList):
        placeholders = generatePlaceholders(len(paramList))
        self.where.append("%s NOT IN (%s)" % (field,placeholders));
        self.params.extend(paramList);

    def openWhereOrClause(self):
        """Signal switch from 'and' conjunctions to 'or', which also requires new paranthetical level"""
        self.where.append("(");
    
    def closeWhereOrClause(self):
        self.where.append(")");
    
    def addGroupBy(self,aGroupBy):
        self.groupBy.append(aGroupBy)

    def addHaving(self,aHaving):
        self.having.append(aHaving)

    def addOrderBy(self,aOrderBy,dir=None):
        if dir != None:
            aOrderBy = "%s %s" % (aOrderBy, dir);
        self.orderBy.append(aOrderBy)

    def setLimit(self,limit):
        self.limit = limit
    
    def setOffset(self,offset):
        self.offset = offset
    
    def addParam(self,aParam):
        self.params.append(aParam);

    def getParams(self):
        return self.params;
    
    def __str__(self):
        query = []  # Build list of query components, then join into a string at the end
        
        if self.prefix is not None:
            query.append(self.prefix);
            query.append("\n");

        if self.delete:
            query.append("DELETE");
        else:
            query.append("SELECT");
            for item in self.select:
                query.append(item);
                query.append(",");
            query.pop(); # Remove the last extraneous comma (",")
        
        if self.into is not None:
            query.append("\nINTO");
            query.append(self.into);

        query.append("\nFROM");
        for item in self.from_:
            if item is None:
                # Sentinel value indicating the next FROM clause will be an explictly stated join clause, so discard/overwrite the last comma
                query[-1] = "\n";
            else:
                query.append(item);
                query.append(",");
        query.pop()

        if self.where:
            query.append("\nWHERE");
            conjunction = "\nAND";
            for item in self.where:
                if item == "(": # Just opened up a paranthetical section
                    query.append(item)
                    conjunction = "\nOR"; # Convert to "or" conjunctions (wouldn't be a point in parantheticals if all "and" conjunctions)
                elif item == ")":   # Closing a paranthetical section
                    query.pop();    # Discard last "or" conjunction
                    query.append(item)
                    conjunction = "\nAND";    # Revert to default 'and' conjunctions
                    query.append(conjunction);
                else: 
                    query.append(item)
                    query.append(conjunction)
            query.pop()

        if self.groupBy:
            query.append("\nGROUP BY")
            for item in self.groupBy:
                query.append(item)
                query.append(",")
            query.pop()

        if self.having:
            query.append("\nHAVING")
            for item in self.having:
                query.append(item)
                query.append("\nAND")
            query.pop()

        if self.orderBy:
            query.append("\nORDER BY")
            for item in self.orderBy:
                query.append(item)
                query.append(",")
            query.pop()
                
        if self.limit is not None and self.limit > -1:
            query.append("\nLIMIT")
            query.append(str(self.limit))
        if self.offset is not None and self.offset > -1:
            query.append("OFFSET")
            query.append(str(self.offset))
        
        query.append(";");  # Closing semi-colon
        query = str.join(" ",query) # Join list items into a single string, space-separated
        return query
