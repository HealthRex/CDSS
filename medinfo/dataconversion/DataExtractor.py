#!/usr/bin/env python
"""Utilities for extracting and formatting clinical database content
into matrix formats usable for machine learning / regression applications.
"""

from optparse import OptionParser
import sys, os;
import time;
from cStringIO import StringIO;
from datetime import datetime, timedelta;
import numpy as np;
from heapq import heappush, heappop;

from medinfo.cpoe.Const import SECONDS_PER_DAY, DELTA_NAME_BY_DAYS;
from medinfo.common.Const import NULL_STRING;

from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList, columnFromModelList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from Util import log;
import Util;

from Const import SENTINEL_RESULT_VALUE;

class DataExtractor:
    def __init__(self):
        self.dataCache = None;  # Allow use of dataCache to avoid cost of repeated queries (e.g., clinical item query by name translation to IDs). Caller should set to a dict() instance to use

    def loadMapData(self,filename):
        """Read the named file's contents through a TabDictReader to enable data extraction.
        If cannot find file by absolute filename, then look under default mapdata directory.
        """
        try:
            return TabDictReader(stdOpen(filename));
        except IOError:
            # Unable to open file directly. See if it's in the default mapdata directory
            appDir = os.path.dirname(Util.__file__);
            defaultFilename = os.path.join(appDir, "mapdata", filename);
            try:
                return TabDictReader(stdOpen(defaultFilename));
            except IOError:
                # May need to add default extension as well
                defaultFilename = defaultFilename + ".tab";
                return TabDictReader(stdOpen(defaultFilename));

    def parsePatientFile(self, patientFile, colNames):
        """Parse out a patient data file. Just assumes one column will be an integer patient_id.
        Return as dictionary keyed by patientId.
        Means data cannot allow for repeats of patients across rows (e.g., multiple admissions).
        Use parsePatientEpisodeFile for more general use case (multiple index times per patient)
        """
        # Just parse out as if episode file, but assume only a single episode per patient
        patientEpisodes = self.parsePatientEpisodeFile(patientFile, colNames);
        patientById = dict();
        for patient in patientEpisodes:
            patientId = patient["patient_id"];
            patientById[patientId] = patient;
        return patientById;

    def parsePatientEpisodeFile(self, patientEpisodeFile, colNames):
        """Parse out a patient encounter data file.
        Just assumes one integer column patient_id.
        Allows for repeat patient rows (e.g., multiple encounters or index times for each patient).
        Updates colNames with any columns encountered so can keep track of accumulated columns of patient
        data (in consistent order).
        """
        #log.info("Parse patient (encounter) file");
        patientEpisodes = list();
        reader = TabDictReader(patientEpisodeFile)
        for patientEpisode in reader:
            patientId = int(patientEpisode["patient_id"]);
            patientEpisode["patient_id"] = patientId;
            patientEpisodes.append(patientEpisode);

        colNames.append("patient_id");
        for col in reader.fieldnames:
            if col != "patient_id":
                colNames.append(col);
        return patientEpisodes;

    def generateDateRangeIndexTimes(self, startDateCol, endDateCol, patientList, colNames, timeInterval=timedelta(1)):
        """Look for named start and end date columns for each patient record, then
        generate a new dictionary by patient ID and date, for each day from start date to end date (inclusive).
        timeInterval - Defaults to 1 day, but can set to a different interval interment
        If just want to have a single index time, then use the same start and end date column
        or set timeInterval to None.
        Input is a list of patient record rows, which then allows for repeat patient records, which still makes
        sense if they span separate non-overlapping date periods (e.g., multiple admissions).
        If overlapping date periods,
        then subsequent patientEpisodeByIndexTimeById results will get clobbered with collisions on same overlapping dates.
        """
        patientEpisodeByIndexTimeById = dict();
        newColNames = list();   # Keep track of new columns
        for patient in patientList:
            patientId = patient["patient_id"];
            (patientEpisodeByIndexTime, newColNames) = self.generateDateRangeIndexTimes_singlePatient(startDateCol, endDateCol, patient, timeInterval);
            if patientId not in patientEpisodeByIndexTimeById:
                patientEpisodeByIndexTimeById[patientId] = dict();
            patientEpisodeByIndexTimeById[patientId].update(patientEpisodeByIndexTime);
        colNames.extend(newColNames);
        return patientEpisodeByIndexTimeById;

    def generateDateRangeIndexTimes_singlePatient(self, startDateCol, endDateCol, patient, timeInterval=timedelta(1)):
        """Look for named start and end date columns for the patient record, then
        generate a new dictionary by patient ID and date, for each day from start date to end date (inclusive).
        timeInterval - Defaults to 1 day, but can set to a different interval interment
        If just want to have a single index time, then use the same start and end date column
        or set timeInterval to None.
        Input is a list of patient record rows, which then allows for repeat patient records, which still makes
        sense if they span separate non-overlapping date periods (e.g., multiple admissions).
        If overlapping date periods,
        then subsequent patientEpisodeByIndexTimeById results will get clobbered with collisions on same overlapping dates.
        """
        patientId = patient["patient_id"];
        patientEpisodeByIndexTime = dict();
        patient[startDateCol] = DBUtil.parseDateValue(patient[startDateCol]);
        patient[endDateCol] = DBUtil.parseDateValue(patient[endDateCol]);
        indexTime = patient[startDateCol];

        while indexTime <= patient[endDateCol]:
            patientCopy = dict(patient);
            patientCopy["index_time"] = indexTime;
            patientCopy["days_until_end"] = (patient[endDateCol]-indexTime).total_seconds() / SECONDS_PER_DAY;
            patientEpisodeByIndexTime[indexTime] = patientCopy;

            if timeInterval is not None:
                indexTime = indexTime + timeInterval;
            else:
                break;  # Time Interval not specified, means only want the first record without interval repetitions

        colNames = ["index_time","days_until_end"];
        return (patientEpisodeByIndexTime, colNames);

    def queryClinicalItems(self,clinicalItemIds,patientIds,outputFile=None):
        """Query for all patient items that match with the given
        clinical item IDs and patient IDs and stream the results out to the given outputFile.
        If outputFile is None, then just return the results as an in memory table.
        """
        #log.info("Query Clinical Items: %s" % str(clinicalItemIds) );
        if isinstance(patientIds,int):
            patientIds = [patientIds];  # Single value, convert to a list of size 1
        formatter = None;
        if outputFile is not None:  # Stream output to formatter to avoid keeping results in memory
            formatter = TextResultsFormatter(outputFile);

        colNames = ["patient_id","item_date"];

        query = SQLQuery();
        for col in colNames:
            query.addSelect(col);
        query.addFrom("patient_item");
        query.addWhereIn("clinical_item_id", clinicalItemIds );
        query.addWhereIn("patient_id", patientIds );
        query.addOrderBy("patient_id");
        query.addOrderBy("item_date");

        return DBUtil.execute( query, includeColumnNames=True, formatter=formatter );

    def queryClinicalItemsByName(self,clinicalItemNames,patientIds,outputFile=None, col=None, operator=None, prefix=None, daysBins=None):
        """Look for clinical items by name.  Will match by SQL "LIKE" so can use wild-cards,
        or can use ~* operator for additional regular expression matching.
        """
        #log.info("Query Clinical Items: %s" % str(clinicalItemNames) );

        clinicalItemIds = None;
        cacheKey = str(clinicalItemNames);  # See if repeated prior requests can cache
        if self.dataCache is not None and cacheKey in self.dataCache:
            clinicalItemIds = self.dataCache[cacheKey];
        else:
            if col is None:
                col = "name";
            if operator is None:
                operator = "like";

            query = SQLQuery();
            query.addSelect("clinical_item_id");
            query.addFrom("clinical_item");

            nameClauses = list();
            for itemName in clinicalItemNames:
                nameClauses.append("%s %s %%s" % (col,operator) );
                query.params.append(itemName);
            query.addWhere( str.join(" or ", nameClauses) );

            results = DBUtil.execute(query);
            clinicalItemIds = [row[0] for row in results];

        if len(clinicalItemIds) == 0:
            return list();  # Empty result set

        return self.queryClinicalItems(clinicalItemIds, patientIds, outputFile);

    def queryClinicalItemsByCategory(self,categoryIds,patientIds,outputFile=None,prefix=None, daysBins=None):
        """Look for clinical items by category specifications.
        """
        clinicalItemIds = None;
        cacheKey = str(categoryIds);  # See if repeated prior requests can cache
        if self.dataCache is not None and cacheKey in self.dataCache:
            clinicalItemIds = self.dataCache[cacheKey];
        else:
            query = SQLQuery();
            query.addSelect("clinical_item_id");
            query.addFrom("clinical_item");
            query.addWhereIn("clinical_item_category_id",categoryIds);
            results = DBUtil.execute(query);
            clinicalItemIds = [row[0] for row in results];

        if len(clinicalItemIds) == 0:
            return list();  # Empty result set

        return self.queryClinicalItems(clinicalItemIds, patientIds, outputFile);

    def parseClinicalItemFile(self, itemFile, patientIdCol="patient_id", timeCol="item_date"):
        """Parse out the temp file generated by queryClinicalItems into a
        itemDatesByPatientId dictionary with each value being a list of ordered item times
        where the clinical items of interest occurred for the given patient ID.
        """
        itemRowIter = TabDictReader(itemFile);
        return self.parseClinicalItemData(itemRowIter, patientIdCol, timeCol);

    def parseClinicalItemData(self, itemRowIter, patientIdCol="patient_id", timeCol="item_date"):
        """More general version of clinical item data parser, does not necessarily come
        from a file stream, could be any reader / iterator over rows of item data.
        For example from a TabDictReader over the temp file or modelListFromTable from database query results.
        """
        itemTimesByPatientId = dict();
        for itemData in itemRowIter:
            patientId = int(itemData[patientIdCol]);
            itemTime = DBUtil.parseDateValue(itemData[timeCol]);

            itemData[patientIdCol] = patientId;
            itemData[timeCol] = itemTime;

            if patientId not in itemTimesByPatientId:
                itemTimesByPatientId[patientId] = list();
            itemTimesByPatientId[patientId].append( itemTime );

        return itemTimesByPatientId;

    def parseClinicalItemData_singlePatient(self, itemRowIter, patientId=None, patientIdCol="patient_id", timeCol="item_date"):
        """Parse out the data for a single patient. If none found, then return None
        """
        itemTimes = None;
        itemTimesByPatientId = self.parseClinicalItemData(itemRowIter, patientIdCol, timeCol);
        if patientId is None:   # Then assume first one encountered is the patient ID of interest
            patientIds = itemTimesByPatientId.keys();
            if patientIds:
                patientId = patientIds[0];
        if patientId in itemTimesByPatientId:
            itemTimes = itemTimesByPatientId[patientId];
        return itemTimes;

    def generateClinicalItemIndexTimes(self, itemTimesByPatientId, patientById, colNames, preDays, postDays):
        """Look for item occurrences for each patient, and generate a new dictionary
        by patient ID and date per time an item occurred, and for each day + or - designated time range
        """
        patientEpisodeByIndexTimeById = dict();
        newColNames = list();   # Keep track of newly added columns
        for patientId, itemTimes in itemTimesByPatientId.iteritems():
            patient = patientById[patientId];
            (patientEpisodeByIndexTimeById[patientId], newColNames) = self.generateClinicalItemIndexTimes_singleRecord(itemTimes, patient, colNames, preDays, postDays);
        colNames.extend(newColNames);
        return patientEpisodeByIndexTimeById;

    def generateClinicalItemIndexTimes_singleRecord(self, itemTimes, patient, preDays, postDays):
        """Look for item occurrences for the patient, and generate a new dictionary
        by patient ID and date per time an item occurred, and for each day + or - designated time range
        """
        patientId = patient["patient_id"];
        patientEpisodeByIndexTime = dict();
        for itemTime in itemTimes:
            itemDay = datetime(itemTime.year, itemTime.month, itemTime.day);  # Capture at day resolution

            for iPreDay in xrange(preDays):
                keyDay = itemDay + timedelta(-iPreDay);
                patientCopy = dict(patientById[patientId]);
                patientCopy["index_time"] = keyDay;
                patientEpisodeByIndexTime[keyDay] = patientCopy;

            for iPostDay in xrange(+1,postDays+1):
                keyDay = itemDay + timedelta(+iPostDay);
                patientCopy = dict(patientById[patientId]);
                patientCopy["index_time"] = keyDay;
                patientEpisodeByIndexTime[keyDay] = patientCopy;
        colNames = ["index_time"];
        return (patientEpisodeByIndexTime, colNames);

    def addTimeCycleFeatures_singlePatient(self, patientEpisodeByIndexTime, timeCol, timeAttr):
        colNames = None;
        for patientEpisode in patientEpisodeByIndexTime.itervalues():
            colNames = self.addTimeCycleFeatures_singleEpisode(patientEpisode, timeCol, timeAttr);
        return colNames;

    def addTimeCycleFeatures_singleEpisode(self, patientEpisode, timeCol, timeAttr):
        """Look for a datetime value in the patientEpisode identified by the timeCol name.
        Add features to the patientEpisode based on the timeAttr string
        ("month","day","hour","minute","second"), including the sine and cosine
        of the time attribute value relative to the maximum possible value to reflect
        cyclical time patterns (e.g., seasonal patterns over months in a year,
        or daily cycle patterns over hours in a day).
        """
        timeObj = patientEpisode[timeCol];
        # Use introspection (getattr) to extract some time feature from the time object,
        #   as well as the maximum and minimum possible values to set the cycle range
        maxValue = getattr(timeObj.max, timeAttr);
        thisValue = getattr(timeObj, timeAttr);
        minValue = getattr(timeObj.min, timeAttr);

        radians = 2*np.pi * (thisValue-minValue) / (maxValue+1-minValue);

        patientEpisode["%s.%s" % (timeCol,timeAttr)] = thisValue;
        patientEpisode["%s.%s.sin" % (timeCol,timeAttr)] = np.sin(radians);
        patientEpisode["%s.%s.cos" % (timeCol,timeAttr)] = np.cos(radians);

        colNames = ["%s.%s" % (timeCol,timeAttr), "%s.%s.sin" % (timeCol,timeAttr), "%s.%s.cos" % (timeCol,timeAttr)];

        return colNames;

    def addClinicalItemFeatures(self, itemTimesByPatientId, patientEpisodeByIndexTimeById, colNames, itemLabel, daysBins=None):
        """Given the clinical item event times for each patient, add values/features to the
        patient records relative to the index time for each patient record.

        daysBins: If specified a list of integer days, then count up number of occurrences of
            the given event times with +/- each days bin size of the index time.
            If not specified, then default to list from medinfo.cpoe.Const.DELTA_NAME_BY_DAYS;
        """
        newColNames = list();   # Keep track of newly added columns
        for patientId, patientEpisodeByIndexTime in patientEpisodeByIndexTimeById.iteritems():
            itemTimes = None;
            if patientId in itemTimesByPatientId:  # Have items to lookup against
                itemTimes = itemTimesByPatientId[patientId];
            newColNames = self.addClinicalItemFeatures_singlePatient(itemTimes, patientEpisodeByIndexTime, itemLabel);
        colNames.extend(newColNames);

    def addClinicalItemFeatures_singlePatient(self, itemTimes, patientEpisodeByIndexTime, itemLabel, daysBins=None):
        """Given the clinical item event times for the patient, add values/features to the
        patient records relative to the index time for each patient record copy.

        daysBins: If specified a list of integer days, then count up number of occurrences of
            the given event times with +/- each days bin size of the index time.
            If not specified, then default to list from medinfo.cpoe.Const.DELTA_NAME_BY_DAYS;
        """
        if daysBins is None:
            daysBins = DELTA_NAME_BY_DAYS.keys();
            daysBins.sort();

        # Find items most proximate before and after the index item for each patient
        # Record timedelta separating nearest items found from index item
        # Count up total items found before, after, and within specified days time bins
        preTimeLabel = "%s.preTimeDays" % itemLabel;
        postTimeLabel = "%s.postTimeDays" % itemLabel;
        preLabel = "%s.pre" % itemLabel;
        postLabel = "%s.post" % itemLabel;

        for indexTime, patient in patientEpisodeByIndexTime.iteritems():
            # Initialize values to null for not found
            patient[preTimeLabel] = None;
            patient[postTimeLabel] = None;
            patient[preLabel] = 0;
            patient[postLabel] = 0;
            for daysBin in daysBins:
                patient["%s.%dd" % (preLabel,daysBin)] = 0;
                patient["%s.%dd" % (postLabel,daysBin)] = 0;

            if itemTimes is not None:
                for itemTime in itemTimes:
                    timeDiffDays = (itemTime - indexTime).total_seconds() / SECONDS_PER_DAY;
                    if timeDiffDays < 0: # Item occurred prior to index time
                        if patient[preTimeLabel] is None:
                            patient[preTimeLabel] = timeDiffDays;
                        elif abs(timeDiffDays) < abs(patient[preTimeLabel]):
                            # Found an item time more proximate to the index time
                            patient[preTimeLabel] = timeDiffDays;
                        patient[preLabel] += 1;
                        for daysBin in daysBins:
                            if abs(timeDiffDays) <= daysBin:
                                patient["%s.%dd" % (preLabel,daysBin)] += 1;

                    else:   # Item occurred after index time
                        if patient[postTimeLabel] is None:
                            patient[postTimeLabel] = timeDiffDays;
                        elif abs(timeDiffDays) < abs(patient[postTimeLabel]):
                            # Found an item time more proximate to the index time
                            patient[postTimeLabel] = timeDiffDays;
                        patient[postLabel] += 1;
                        for daysBin in daysBins:
                            if abs(timeDiffDays) <= daysBin:
                                patient["%s.%dd" % (postLabel,daysBin)] += 1;

        colNames = [preTimeLabel,postTimeLabel,preLabel,postLabel];
        for daysBin in daysBins:
            colNames.append("%s.%dd" % (preLabel,daysBin));
            colNames.append("%s.%dd" % (postLabel,daysBin));

        return colNames;

    def queryLabResults(self, labBaseNames, patientIds, outputFile=None):
        """Query for all lab results that match with the given
        result base names and patient IDs and stream the results out to the given outputFile.
        If outputFile is None, then just return the results as an in memory table.
        """
        #log.info("Query out lab results, takes a while");

        if isinstance(patientIds,int):
            patientIds = [patientIds];  # Single value, convert to a list of size 1
        formatter = None;
        if outputFile is not None:   # Stream output to formatter to avoid keepign all results in memory
            formatter = TextResultsFormatter(outputFile);

        # Query rapid when filter by lab result type, limited to X records.
        # Filtering by patient ID drags down substantially until preloaded table by doing a count on the SOR table?
        colNames = ["cast(pat_id as bigint)","base_name","ord_num_value","result_flag","result_in_range_yn","sor.result_time"];

        # Patient ID is miscast as str instead of int, must accomodate comparisons
        patientIdStrs = list();
        for patientId in patientIds:
            patientIdStrs.append( str(patientId) );

        query = SQLQuery();
        for col in colNames:
            query.addSelect(col);
        query.addFrom("stride_order_results as sor, stride_order_proc as sop");
        query.addWhere("sor.order_proc_id = sop.order_proc_id");
        query.addWhereIn("base_name", labBaseNames );
        query.addWhereIn("pat_id", patientIdStrs );
        query.addOrderBy("pat_id");
        query.addOrderBy("sor.result_time");

        results = DBUtil.execute( query, includeColumnNames=True, formatter=formatter );
        return results;

    def queryFlowsheet(self, flowsheetNames, patientIds, outputFile):
        """Query out flowsheet data values, directly analogous to lab results"""
        #log.info("Query out flowsheet, will take a while");

        if isinstance(patientIds,int):
            patientIds = [patientIds];  # Single value, convert to a list of size 1
        formatter = None;
        if outputFile is not None:   # Stream output to formatter to avoid keeping all results in memory
            formatter = TextResultsFormatter(outputFile);

        colNames = ["pat_anon_id","flo_meas_id","flowsheet_name","flowsheet_value","shifted_dt_tm"];

        patientIdStrs = list();
        for patientId in patientIds:
            patientIdStrs.append( str(patientId) );

        query = SQLQuery();
        for col in colNames:
            query.addSelect(col);
        query.addFrom("stride_flowsheet");
        query.addWhereIn("flowsheet_name", flowsheetNames );
        query.addWhereIn("pat_anon_id", patientIdStrs );
        query.addOrderBy("pat_anon_id");
        query.addOrderBy("shifted_dt_tm");

        return DBUtil.execute( query, includeColumnNames=True, formatter=formatter );

    def parseResultsFile(self, resultFile, patientIdCol, nameCol, valueCol, datetimeCol):
        """Generic function to parse real valued relational results data with different
        possible key column names (i.e., deriving from queryLabResults or queryFlowsheet).
        Have to specify the name of the key columns to look for.

        Could store entire file in memory, but may need a ton of RAM.

        Use streaming (generator) approach where it yields just one patient's data at a time.
        To do this safely, it must assume that the input result file is presorted by patient ID
        """
        resultRowIter = TabDictReader(resultFile);
        parsedResultRowIter = self.parseResultsDataGenerator(resultRowIter, patientIdCol, nameCol, valueCol, datetimeCol);
        for (patientId, resultsByName) in parsedResultRowIter:
            yield (patientId, resultsByName);

    def parseResultsDataGenerator(self, resultRowIter, patientIdCol, nameCol, valueCol, datetimeCol):
        """More general version of results data parser, does not necessarily come
        from a file stream, could be any reader / iterator over rows of item data.
        For example from a TabDictReader over the temp file or modelListFromTable from database query results.
        """
        lastPatientId = None;
        resultsByName = None;
        for result in resultRowIter:
            if result[valueCol] is not None and result[valueCol] != NULL_STRING:
                patientId = int(result[patientIdCol]);
                baseName = result[nameCol];
                resultValue = float(result[valueCol]);
                resultTime = DBUtil.parseDateValue(result[datetimeCol]);

                if resultValue < SENTINEL_RESULT_VALUE:    # Skip apparent placeholder values
                    result[patientIdCol] = result["patient_id"] = patientId;
                    result[valueCol] = resultValue;
                    result[datetimeCol] = resultTime;

                    if patientId != lastPatientId:
                        # Encountering a new patient ID. Yield the results from the prior one before preparing for next one
                        if lastPatientId is not None:
                            yield (lastPatientId, resultsByName);
                        lastPatientId = patientId;
                        resultsByName = dict();
                    if baseName not in resultsByName:
                        resultsByName[baseName] = list();
                    resultsByName[baseName].append( result );

        if lastPatientId is not None:   # Yield last result
            yield (lastPatientId, resultsByName);
        #return resultsByNameByPatientId; # Makes more sense to load generator results as key value pairs in dictionary, but requires exccessive in memory storage

    def parseResultsData(self, resultRowIter, patientIdCol, nameCol, valueCol, datetimeCol):
        """Wrapper for generator version to translate results into dictionary by patient ID
        for more consistent structure to parseClinicalItemData
        """
        resultsByNameByPatientId = dict();
        for (patientId, resultsByName) in self.parseResultsDataGenerator(resultRowIter, patientIdCol, nameCol, valueCol, datetimeCol):
            resultsByNameByPatientId[patientId] = resultsByName;
        return resultsByNameByPatientId;

    def parseResultsData_singlePatient(self, resultRowIter, patientIdCol, nameCol, valueCol, datetimeCol, patientId=None):
        """Parse out the data for a single patient. If none found, then return None
        """
        resultsByName = None;
        resultsByNameByPatientId = self.parseResultsData(resultRowIter, patientIdCol, nameCol, valueCol, datetimeCol);
        if patientId is None:   # Then assume first one encountered is the patient ID of interest
            patientIds = resultsByNameByPatientId.keys();
            if patientIds:
                patientId = patientIds[0];
        if patientId in resultsByNameByPatientId:
            resultsByName = resultsByNameByPatientId[patientId];
        return resultsByName;

    def addResultFeatures(self, patientEpisodeByIndexTimeById, patientIdResultsByNameGenerator, baseNames, valueCol, datetimeCol, preTimeDelta, postTimeDelta, colNames):
        """Add on summary features to the patient-time instances.
        With respect to each index time, look for results within [indexTime+preTimeDelta, indexTime+postTimeDelta) and
        generate summary features like count, mean, median, std, first, last, proximate.
        Generic function, so have to specify the names of the value and datetime columns to look for.

        Assume patientIdResultsByNameGenerator is actually a generator for each patient, so can only stream through results once
        """
        newColNames = list();   # Keep track of new columns of data added
        # Use results generator as outer loop as will not be able to random access index the contents
        for patientId, resultsByName in patientIdResultsByNameGenerator:
            if patientId in patientEpisodeByIndexTimeById: # Skip results if not in our list of patients of interest
                patientEpisodeByIndexTime = patientEpisodeByIndexTimeById[patientId];
                newColNames = self.addResultFeatures_singlePatient(patientEpisodeByIndexTime, resultsByName, baseNames, valueCol, datetimeCol, preTimeDelta, postTimeDelta);

        # Separate loop to verify all patient records addressed, even if no results available (like an outer join)
        resultsByName = None;
        for patientId, patientEpisodeByIndexTime in patientEpisodeByIndexTimeById.iteritems():
            newColNames = self.addResultFeatures_singlePatient(patientEpisodeByIndexTime, resultsByName, baseNames, valueCol, datetimeCol, preTimeDelta, postTimeDelta);

        colNames.extend(newColNames);

    def addResultFeatures_singlePatient(self, patientEpisodeByIndexTime, resultsByName, baseNames, valueCol, datetimeCol, preTimeDelta, postTimeDelta):
        """Add on summary features to the patient-time instances.
        With respect to each index time, look for results within [indexTime+preTimeDelta, indexTime+postTimeDelta) and
        generate summary features like count, mean, median, std, first, last, proximate.
        Generic function, so have to specify the names of the value and datetime columns to look for.

        If resultsByName is None, then no results to match.
        Just make sure default / zero value columns are populated if they are not already
        """
        preTimeDays = None;
        if preTimeDelta is not None:
            preTimeDays = preTimeDelta.days;
        postTimeDays = None;
        if postTimeDelta is not None:
            postTimeDays = postTimeDelta.days;

        # Init summary values to null for all results
        for indexTime, patient in patientEpisodeByIndexTime.iteritems():
            for baseName in baseNames:
                if resultsByName is not None or ("%s.%s_%s.count" % (baseName,preTimeDays,postTimeDays)) not in patient:
                    # Default to null for all values
                    patient["%s.%s_%s.count" % (baseName,preTimeDays,postTimeDays)] = 0;
                    patient["%s.%s_%s.countInRange" % (baseName,preTimeDays,postTimeDays)] = 0;
                    patient["%s.%s_%s.min" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.max" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.median" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.mean" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.std" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.first" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.last" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.diff" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.slope" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.proximate" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.firstTimeDays" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.lastTimeDays" % (baseName,preTimeDays,postTimeDays)] = None;
                    patient["%s.%s_%s.proximateTimeDays" % (baseName,preTimeDays,postTimeDays)] = None;

        if resultsByName is not None:   # Have results available for this patient
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():

                # Time range limits on labs to consider
                preTimeLimit = None;
                postTimeLimit = None;

                if preTimeDelta is not None:
                    preTimeLimit = indexTime+preTimeDelta;
                if postTimeDelta is not None:
                    postTimeLimit = indexTime+postTimeDelta;

                for baseName in baseNames:
                    proximateValue = None;
                    if resultsByName is not None and baseName in resultsByName:   # Not all patients will have all labs checked
                        firstItem = None;
                        lastItem = None;
                        proximateItem = None;   # Item closest to the index item in time
                        filteredResults = list();
                        for result in resultsByName[baseName]:
                            resultTime = result[datetimeCol];
                            if (preTimeLimit is None or preTimeLimit <= resultTime) and (postTimeLimit is None or resultTime < postTimeLimit):
                                # Occurs within time frame of interest, so record this value
                                filteredResults.append(result);

                                if firstItem is None or resultTime < firstItem[datetimeCol]:
                                    firstItem = result;
                                if lastItem is None or lastItem[datetimeCol] < resultTime:
                                    lastItem = result;
                                if proximateItem is None or (abs(resultTime-indexTime) < abs(proximateItem[datetimeCol]-indexTime)):
                                    proximateItem = result;

                        if len(filteredResults) > 0:
                            # Count up number of values specifically labeled as "in range"
                            valueList = columnFromModelList(filteredResults, valueCol);
                            patient["%s.%s_%s.count" % (baseName,preTimeDays,postTimeDays)] = len(valueList);
                            patient["%s.%s_%s.countInRange" % (baseName,preTimeDays,postTimeDays)] = self.countResultsInRange(filteredResults);
                            patient["%s.%s_%s.min" % (baseName,preTimeDays,postTimeDays)] = np.min(valueList);
                            patient["%s.%s_%s.max" % (baseName,preTimeDays,postTimeDays)] = np.max(valueList);
                            patient["%s.%s_%s.median" % (baseName,preTimeDays,postTimeDays)] = np.median(valueList);
                            patient["%s.%s_%s.mean" % (baseName,preTimeDays,postTimeDays)] = np.mean(valueList);
                            patient["%s.%s_%s.std" % (baseName,preTimeDays,postTimeDays)] = np.std(valueList);
                            patient["%s.%s_%s.first" % (baseName,preTimeDays,postTimeDays)] = firstItem[valueCol];
                            patient["%s.%s_%s.last" % (baseName,preTimeDays,postTimeDays)] = lastItem[valueCol];
                            patient["%s.%s_%s.diff" % (baseName,preTimeDays,postTimeDays)] = lastItem[valueCol] - firstItem[valueCol];
                            patient["%s.%s_%s.slope" % (baseName,preTimeDays,postTimeDays)] = 0.0;
                            timeDiffDays = ((lastItem[datetimeCol]-firstItem[datetimeCol]).total_seconds() / SECONDS_PER_DAY);
                            if timeDiffDays > 0.0:
                                patient["%s.%s_%s.slope" % (baseName,preTimeDays,postTimeDays)] = (lastItem[valueCol]-firstItem[valueCol]) / timeDiffDays;
                            patient["%s.%s_%s.proximate" % (baseName,preTimeDays,postTimeDays)] = proximateItem[valueCol];
                            patient["%s.%s_%s.firstTimeDays" % (baseName,preTimeDays,postTimeDays)] = (firstItem[datetimeCol]-indexTime).total_seconds() / SECONDS_PER_DAY;
                            patient["%s.%s_%s.lastTimeDays" % (baseName,preTimeDays,postTimeDays)] = (lastItem[datetimeCol]-indexTime).total_seconds() / SECONDS_PER_DAY;
                            patient["%s.%s_%s.proximateTimeDays" % (baseName,preTimeDays,postTimeDays)] = (proximateItem[datetimeCol]-indexTime).total_seconds() / SECONDS_PER_DAY;

        return self.colsFromBaseNames(baseNames,preTimeDays,postTimeDays);

    def countResultsInRange(self,resultList):
        """Return the number of result models in the given list that represent "normal" "in range" values."""
        countInRange = 0;
        for result in resultList:
            if "result_in_range_yn" in result and result["result_in_range_yn"] == "Y":
                countInRange += 1;
        return countInRange;

    def colsFromBaseNames(self, baseNames, preTimeDays, postTimeDays):
        """Enumerate derived column/feature names given a set of (lab) result base names"""
        suffixes = ["count","countInRange","min","max","median","mean","std","first","last","diff","slope","proximate","firstTimeDays","lastTimeDays","proximateTimeDays"];
        for baseName in baseNames:
            for suffix in suffixes:
                colName = "%s.%s_%s.%s" % (baseName, preTimeDays, postTimeDays, suffix);
                yield colName;

    def parseLabResultsFile(self, resultFile):
        for result in self.parseResultsFile(resultFile, "pat_id","base_name","ord_num_value","result_time"):
            yield result;

    def parseLabResultsData(self, resultRowIter):
        return self.parseResultsData(resultRowIter, "pat_id","base_name","ord_num_value","result_time");

    def parseLabResultsData_singlePatient(self, resultRowIter, patientId=None):
        return self.parseResultsData_singlePatient(resultRowIter, "pat_id","base_name","ord_num_value","result_time", patientId);

    def addLabFeatures(self, patientEpisodeByIndexTimeById, patientIdResultsByNameGenerator, labBaseNames, preTimeDelta, postTimeDelta, colNames):
        #log.info("Sort lab results by result time for each patient and find items within specified time period to aggregate");
        return self.addResultFeatures(patientEpisodeByIndexTimeById, patientIdResultsByNameGenerator, labBaseNames, "ord_num_value", "result_time",  preTimeDelta, postTimeDelta, colNames)

    def addLabFeatures_singlePatient(self, patientEpisodeByIndexTime, resultsByName, baseNames, preTimeDelta, postTimeDelta):
        return self.addResultFeatures_singlePatient(patientEpisodeByIndexTime, resultsByName, baseNames, "ord_num_value", "result_time", preTimeDelta, postTimeDelta);

    def parseFlowsheetFile(self, resultFile):
        for result in self.parseResultsFile(resultFile, "pat_anon_id","flowsheet_name","flowsheet_value","shifted_dt_tm"):
            yield result;

    def parseFlowsheetData(self, resultRowIter):
        return self.parseResultsData(resultRowIter, "pat_anon_id","flowsheet_name","flowsheet_value","shifted_dt_tm");

    def parseFlowsheetData_singlePatient(self, resultRowIter, patientId=None):
        return self.parseResultsData_singlePatient(resultRowIter, "pat_anon_id","flowsheet_name","flowsheet_value","shifted_dt_tm", patientId);

    def addFlowsheetFeatures(self, patientEpisodeByIndexTimeById, patientIdResultsByNameGenerator, baseNames, preTimeDelta, postTimeDelta, colNames):
        #log.info("Sort flowsheet by time for each patient and find items within specified time period to aggregate");
        return self.addResultFeatures(patientEpisodeByIndexTimeById, patientIdResultsByNameGenerator, baseNames, "flowsheet_value","shifted_dt_tm",  preTimeDelta, postTimeDelta, colNames)

    def addFlowsheetFeatures_singlePatient(self, patientEpisodeByIndexTime, resultsByName, baseNames, preTimeDelta, postTimeDelta):
        return self.addResultFeatures_singlePatient(patientEpisodeByIndexTime, resultsByName, baseNames, "flowsheet_value","shifted_dt_tm", preTimeDelta, postTimeDelta);

    def queryIVFluids(self, ivfMedIds, patientIds, outputFile):
        """Can get sets of IVFluid medication IDs from medinfo/dataconversion/mapdata/Medication.IVFluids.tab
        For example:
            ivfMedIds = set();
            for row in self.extractor.loadMapData("Medication.IVFluids"):
                if row["group"] == "isotonic":
                    ivfMedIds.add(row["medication_id"]);
        """
        log.info("Query out (presumably) IV Fluid Orders");

        formatter = None;    # Stream output to formatter to avoid keeping all results in memory
        if outputFile is not None:
            formatter = TextResultsFormatter(outputFile);

        colNames = ["pat_id","medication_id","start_taking_time","end_taking_time","freq_name","min_discrete_dose","min_rate"];

        patientIdStrs = list();
        for patientId in patientIds:
            patientIdStrs.append( str(patientId) );

        query = SQLQuery();
        for col in colNames:
            query.addSelect(col);
        query.addFrom("stride_order_med");
        query.addWhereIn("medication_id", ivfMedIds );
        query.addWhereIn("pat_id", patientIdStrs );
        query.addWhere("freq_name not like '%%PRN%%'"); # Ignore PRN and periprocedure orders?
        query.addWhere("freq_name not like '%%PACU%%'");
        query.addWhere("freq_name not like '%%ENDOSCOPY%%'");
        query.addWhere("end_taking_time is not null");  # If end time is null, indicates a cancelled order that didn't happen
        query.addOrderBy("pat_id");
        query.addOrderBy("start_taking_time");
        query.addOrderBy("end_taking_time");

        return DBUtil.execute( query, includeColumnNames=True, formatter=formatter );

    def parseIVFluidFile(self, ivfFile):
        ivFluidsByPatientId = dict();
        for row in TabDictReader(ivfFile):
            patientId = int(row["pat_id"]);
            row["pat_id"] = patientId;
            row["medication_id"] = int(row["medication_id"]);
            row["start_taking_time"] = DBUtil.parseDateValue(row["start_taking_time"]);
            row["end_taking_time"] = DBUtil.parseDateValue(row["end_taking_time"]);

            if row["min_discrete_dose"] and row["min_discrete_dose"] != NULL_STRING:
                row["min_discrete_dose"] = float(row["min_discrete_dose"]);
            else:
                row["min_discrete_dose"] = None;
            if row["min_rate"] and row["min_rate"] != NULL_STRING:
                row["min_rate"] = float(row["min_rate"]);
            else:
                row["min_rate"] = None;

            if patientId not in ivFluidsByPatientId:
                ivFluidsByPatientId[patientId] = list();
            ivFluidsByPatientId[patientId].append( row );

        return ivFluidsByPatientId;

    def addIVFluidFeatures(self, patientEpisodeByIndexTimeById, ivFluidsByPatientId, thresholdVolumes, checkpointTimes, colNames):
        """
        ivFluidsByPatient: IVFluid data as generated by queryIVFluids or loaded by parseIVFluidFile.
            Will assume fluid items area already chronologically sorted
        thresholdVolumes: List of volumes (in mL) to calculate how long (in seconds) it took for patient to see that much IVF volume.
            record as "ivf.secondsUntilCC.XXX" entries (replacing XXX with the specified thresholdVolume).
            If patient never encounters this much IVF volume, then record None/null.
        checkpointTimes: List of times (in seconds) to calculate how much IVFluid has been accumulated in the patient
            up to (but NOT including) the given checkpoint time.
        """
        log.info("Run though IV Fluid orders for each patient and calculate accumulate amounts  for different threshold volumes and checkpoint times");
        firstPass = True;
        for patientId, patientEpisodeByIndexTime in patientEpisodeByIndexTimeById.iteritems():

            # Custom rebuild IV fluid item list so infusion end times are their own (negative) events
            expandedIVFluidItems = list();
            if patientId in ivFluidsByPatientId:
                expandedIVFluidItems = self.expandIVFluidItems(ivFluidsByPatientId[patientId]);

            for indexTime, patient in patientEpisodeByIndexTime.iteritems():   # If have multiple index times per patient, will be repeated calculations here since restart volume accumulation counts for each index time
                # First build up accumulating fluid time point information
                timepoints = [0];   # Track time points (seconds relative to index time) evaluated
                preBolusVolumes = [0.0];  # Track total volume (mL) accumulated up to each time point, before any boluses that occur at this timepoint
                postBolusVolumes = [0.0];    # Total volume accumulated, just after any boluses (interpreted to occur in instantaneous time) at this timepoint
                infusionRates = [0.0]; # Track  accumulation rates (i.e., continuous IV fluid infusion). Expected units: mL per HOUR (not per second)

                for ivFluidItem in expandedIVFluidItems:
                    if ivFluidItem["start_taking_time"] >= indexTime:  # Found item occuring after index item
                        timepoint = (ivFluidItem["start_taking_time"] - indexTime).total_seconds();
                        if timepoint > timepoints[-1]:  # New time point, create another entry
                            timeDiff = (timepoint-timepoints[-1]);
                            newVolume = postBolusVolumes[-1] + infusionRates[-1]*timeDiff/60/60;    # Add up any accumulated infusions
                            timepoints.append(timepoint);
                            preBolusVolumes.append(newVolume);
                            postBolusVolumes.append(newVolume);
                            infusionRates.append(infusionRates[-1]);
                        if ivFluidItem["min_discrete_dose"] is not None:   # Looks like a bolus volume. Simplifying assumption, assume will always be "ONCE," realizing there may be some "DAILY or BID," etc. items that will be missed
                            postBolusVolumes[-1] += ivFluidItem["min_discrete_dose"];
                        elif ivFluidItem["min_rate"] is not None:  # Looks like a continuous infusion (rate change)
                            infusionRates[-1] += ivFluidItem["min_rate"];

                # Make sure result points of interest are in sorted order to facilitate parallel streaming
                checkpointTimes.sort();
                iTimepoint = 0; # Index of current fluid timepoint assessing
                nTimepoints = len(timepoints);
                for checkpointTime in checkpointTimes:
                    while iTimepoint+1 < nTimepoints and timepoints[iTimepoint+1] <= checkpointTime:
                        # Keep traversing timepoints until next one will meet or pass next checkpoint time
                        iTimepoint += 1;
                    # timepoints[iTimepoint] should now be the last one on or before the checkpointTime
                    # Since starting at time zero, should always be able to find a
                    #   pre-timepoint like this for any (non-negative) checkpoint time
                    timeDiff = (checkpointTime-timepoints[iTimepoint]);
                    checkpointVolume = postBolusVolumes[iTimepoint] + infusionRates[iTimepoint]*timeDiff/60/60;
                    col = "ivf.CCupToSec.%d" % checkpointTime;
                    patient[col] = checkpointVolume;
                    if firstPass:
                        colNames.append(col);

                # Make sure result points of interest are in sorted order to facilitate parallel streaming
                thresholdVolumes.sort();
                iTimepoint = 0; # Index of current fluid timepoint assessing
                nTimepoints = len(timepoints);
                for thresholdVolume in thresholdVolumes:
                    col = "ivf.secondsUntilCC.%d" % thresholdVolume;
                    while iTimepoint+1 < nTimepoints and thresholdVolume > preBolusVolumes[iTimepoint+1]:
                        # Keep traversing timepoints until next one will meet or pass threshold volume
                        iTimepoint += 1;
                    # preBolusVolumes[iTimepoint+1] should now be the first one to exceed the threshold volume,
                    if thresholdVolume <= postBolusVolumes[iTimepoint]:    # Threshold volume within current post bolus volumes, so happened at this timepoint
                        patient[col] = timepoints[iTimepoint];
                    elif iTimepoint+1 >= nTimepoints:   # Hit last time point and post-bolus volume still doesn't meet threshold. Means that volume was never reached
                        patient[col] = None;
                    else:   # General case, threshold volume was hit at some point during infusion ramp starting from this timepoint
                        # Do some algebra to interpolate the time from until infusion rate ramp will hit target threshold volume
                        timeUntilThreshold = (thresholdVolume - postBolusVolumes[iTimepoint]) * 60*60 / infusionRates[iTimepoint];   # Beware divide by zero, but if data constructed properly, shouldn't be possible
                        patient[col] = timepoints[iTimepoint] + timeUntilThreshold;
                    if firstPass:
                        colNames.append(col);

                firstPass = False;

    def expandIVFluidItems(self, ivFluidItems):
        """Return a copy of the ivFluidItems list, assumed to be in chronologically sorted order,
        but insert additional items to mark time points where IV infusions are noted to end.
        Signify with negative min_rate values, and using the "start_taking_time" to mark the time of these end events.
        """
        expandedIVFluidItems = list();
        infusionEndItemHeap = list();   # Interpret as heap (priority queue) of 2-ples keyed by end-date for infusion items, so know when to "turn off" their infusion rates
        for ivFluidItem in ivFluidItems:
            nextTime = ivFluidItem["start_taking_time"];
            while infusionEndItemHeap and infusionEndItemHeap[0][0] <= nextTime:    # See if passed any infusion end times, then record an entry for those
                (endTime, infusionEndItem) = heappop(infusionEndItemHeap);
                expandedIVFluidItems.append(infusionEndItem);
            expandedIVFluidItems.append(ivFluidItem);
            if ivFluidItem["min_rate"] is not None:  # Looks like a continuous infusion
                # Create an item copy to signify end of infusion, and keep track of when to add it later
                infusionEndItem = dict(ivFluidItem);
                infusionEndItem["start_taking_time"] = infusionEndItem["end_taking_time"];
                infusionEndItem["min_rate"] = -infusionEndItem["min_rate"];
                heappush(infusionEndItemHeap, (ivFluidItem["end_taking_time"], infusionEndItem) );  # Keep track of infusion end time
        # Final check if any end infusion items left to account for
        while infusionEndItemHeap:
            (endTime, infusionEndItem) = heappop(infusionEndItemHeap);
            expandedIVFluidItems.append(infusionEndItem);
        return expandedIVFluidItems;

    def filterPatients(patientById):
        #log.info("Deidentify patient IDs and build data list with adequate data");
        patientResults = list();
        for iPatient, patient in enumerate(patientById.itervalues()):
            # Further deidentify patients by applying sequential ID
            patient["pat_id"] = patient["patient_id"] = iPatient;
            # Only accept patients where an index item and times were found
            if "index_time" in patient:
                patientResults.append(patient);
        return patientResults;


    def main(argv):
        pass;

if __name__ == "__main__":
    instance = DataExtractor();
    instance.main(sys.argv)
