"""Common objects / base classes used to support DB interactions.
"""
from .Env import SQL_PLACEHOLDER;

class RowItemModel(dict):
    """Generic object class to model rows from database tables.
    Basically is just a dictionary mapping column names to values, but
    extra abstraction for additional data and functions.
    """

    """Name of the table this is supposed to represent a row of"""
    tableName = None;

    """Simple boolean field indicating whether this item is newly inserted
    this run, or if it was retrieved as an existing row.
    """
    isNew = None;

    """If generated as a series of items, can record the index position in the original list here"""
    index = None;

    """Can also count up the number of new items found, not just the total count"""
    newCount = None;

    """Arbitrary child data if needed, perhaps to precompute some child data before actual traversal to children"""
    childData = None;

    def __init__(self,initData=None,dataKeys=None):
        """Initialization constructor.  If no parameters provided, will
        just create an empty model object.  If a single dictionary
        parameter is provided, will copy over the contents into the row
        item model.  If two parameters are provided, expect these to be
        a list of data values and a list of data names / keys to be
        added in the row item model.
        """
        dict.__init__(self);
        self.update(initData,dataKeys)

    def update(self, initData=None, dataKeys=None):
        """Same like the constructor but can do at any time to update (overwrite)
        or extend the data already in the model.
        """
        if initData is not None:
            if dataKeys is not None:
                # Have both initData and dataKeys.  Expect these to be lists of data and names / keys
                for key, value in zip(dataKeys, initData):
                    self[key] = value
            else:
                # Only have initData, expect this to be a dictionary.  Copy over contents
                for key, value in initData.items():
                    self[key] = value
        return self

    def valuesByName(self, columnNames):
        """Return the values in the dictionary as a list.  Unlike the basic
        dict.values() method, can provide a list of columnNames to only return
        the values keyed by the names provided in that list, and in that order.
        """
        values = []
        for col in columnNames:
            values.append(self[col])
        return values

def modelListFromTable(results,columnNames=None):
    """Given a table (2D array) of result items, where each row represents
    an row / item / object from the database, create an equivalent list of
    RowItemModels representing those items.

    If the columnNames are not supplied, then requires that the first row
    of the results table actually be the names
    of the columns to key the items of the RowItemModels by.
    If used the DBUtil.execute method, this is easy as you just need to set
    the "includeColumnNames" parameter.
    """
    modelList = []
    for row in results:
        if columnNames is None:
            columnNames = row;
        else:
            modelList.append(RowItemModel(row,columnNames))
    return modelList

def modelDictFromList(modelList,columnName,listValues=False):
    """Given a list of model objects, create a dictionary keyed by
    the models' values of the columnName attribute with values
    equal to the corresponding model objects.

    If listValues is True, rather the dictionary values being the
    model objects themselves, they will instead be list objects
    with the models appended into the lists.  This would be uninteresting
    for "unique key" columnNames as it would just create dictionary
    where every value is a list of size 1.  However, this is important
    for non-unique key columnNames to make sure that model objects
    from the original list are not overwritten / lost.
    """
    modelDict = {};
    for model in modelList:
        key = model[columnName];
        if listValues:
            if key not in modelDict:
                modelDict[key] = [];    # Create a new list
            modelDict[key].append(model);
        else:
            modelDict[key] = model;
    return modelDict;

def columnFromModelList(modelList,columnName):
    """Given a list of model objects and the name of a
    "column" / attribute, return a list representing
    a "column" of those values, one from each model object.

    Alternatively can use python list comprehension
    column = [model[columnName] for model in modelList];
    """
    column = [];
    for model in modelList:
        column.append(model[columnName]);
    return column;

class RowItemFieldComparator:
    """Comparator object to compare pairs of RowItemModel objects,
    though it will work on any dictionary object.
    Takes a field name (column name / key) as an initialization parameter.
    Compares the total RowItemModel objects based on the each objects
    field value namd by the given key.

    Use to sort lists of RowItemModels / dicts like:

    >>> from medinfo.db.Model import RowItemFieldComparator
    >>> itemList = \
    ...     [   {"a":1,"b":2},
    ...         {"a":5,"b":9},
    ...         {"a":3,"b":4},
    ...         {"a":8,"b":2},
    ...         {"a":1,"b":5},
    ...     ];
    >>> itemList.sort( RowItemFieldComparator("a") );
    >>> for item in itemList:
    ...     print item
    ...
    {'a': 1, 'b': 2}
    {'a': 1, 'b': 5}
    {'a': 3, 'b': 4}
    {'a': 5, 'b': 9}
    {'a': 8, 'b': 2}

    Though modern Python also enable this with key functions:
    >>> itemList.sort( key=lambda item: item["a"] )

    """
    def __init__(self, fieldNames, desc=False):
        if isinstance(fieldNames,str):
            fieldNames = [fieldNames];  # Looks like a single field string, treat as a single item then
        self.fieldNames = fieldNames;
        self.desc = desc;


    def __call__(self, item1, item2):
        values1 = list();
        for fieldName in self.fieldNames:
            values1.append(item1[fieldName]);

        values2 = list();
        for fieldName in self.fieldNames:
            values2.append(item2[fieldName]);

        result = (values1 > values2) - (values1 < values2)
        if self.desc:
            result *= -1;
        return result;


class SQLQuery:
    """Helper class to dynamically build a SQL statement.
    Unlike just appending to a string, allows for addition
    of select, from, where, etc. clauses in any order,
    then generate them in normal order at the end.

    When ready to use, simple convert to a string with placeholders and pass the list of respective parameters
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
        self.select.append(aSelect);

    def addDelete(self,aSelect):
        self.delete = True;
        self.select.append(aSelect);

    def setInto(self,aInto):
        self.into = aInto;

    def addFrom(self,aFrom):
        self.from_.append(aFrom);

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

        query = str.join(" ",query) # Join list items into a single string, space-separated
        return query

    def totalQuery(self):
        """Return a comparable query but that selects for the total result count
        rather than the data from the base query.
        Basically copy the query but replace select columns with "count(*)"
        and ignore any order by clauses
        """
        aTotalQuery = SQLQuery();
        aTotalQuery.addSelect("count(*)");
        aTotalQuery.from_ = self.from_;
        aTotalQuery.where = self.where;
        aTotalQuery.params = self.params;
        return aTotalQuery


def generatePlaceholders(count, sqlPlaceholder=SQL_PLACEHOLDER):
    """Returns a comma-separated string of query placeholders (e.g. %s),
    perfect for use in an "in" clause.
    """
    placeholders = "%s,"%(sqlPlaceholder)          # Use the standard placeholder character
    placeholders = placeholders * count             # Repeat the placeholder (with comma) accordingly
    placeholders = placeholders[:-1]                # Trim the extra comma at the end.
    return placeholders
