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

class Feature:
    def __init__(self):
        self.cursor = None


class ClinicalItemFeature(Feature):
    def __init__(self, prefix, col, operator, daysBins):
        Feature.__init__(self)
        self.prefix = prefix
        self.col = col
        self.operator = operator
        self.timeIntervals = daysBins
        if daysBins == None:
            self.timeIntervals = [1, 2, 4, 7, 14, 30, 90, 180, 365, 730, 1460]

    def getColNames(self):
        colNames = [".preTimeDays", ".postTimeDays", ".pre", ".post"]
        for interval in self.timeIntervals:
            colNames.append(".pre."+str(interval)+"d")
        for interval in self.timeIntervals:
            colNames.append(".post."+str(interval)+"d")
        return [self.prefix+col for col in colNames]

class ClinicalItemByNameFeature(ClinicalItemFeature):
    def __init__(self,clinicalItemNames, prefix, col, operator, daysBins):
        ClinicalItemFeature.__init__(self, prefix, col, operator, daysBins)
        self.clinicalItemNames = clinicalItemNames

class ClinicalItemByCategoryFeature(ClinicalItemFeature):
    def __init__(self,clinicalItemCategoryIds, prefix, col, operator, daysBins):
        ClinicalItemFeature.__init__(self, prefix, col, operator, daysBins)
        self.clinicalItemCategoryIds = clinicalItemCategoryIds

# this can be used for lab or flowsheet features
class ResultFeature(Feature):
    def __init__(self, itemNames, lookbackTime, lookaheadTime):
        Feature.__init__(self)
        self.itemNames = itemNames
        self.lookbackTime = lookbackTime
        self.lookaheadTime = lookaheadTime

    def getColNames(self):
        resultColNames = ["count","countInRange","min","max","median",\
        "mean","std","first","last","diff","slope","proximate",\
        "firstTimeDays","lastTimeDays","proximateTimeDays"]

        lookbackTimeString = 'None'
        if self.lookbackTime is not None:
            lookbackTimeString = str(self.lookbackTime.days)
        lookaheadTimeString = 'None'
        if self.lookaheadTime is not None:
            lookaheadTimeString = str(self.lookaheadTime.days)
        timeRangeString = lookbackTimeString+'_'+lookaheadTimeString
        newColNames = list()
        for itemName in self.itemNames:
            for col in resultColNames:
                newColNames.append("\t%s.%s.%s" % (itemName, timeRangeString, col))

        return newColNames

class IVFluidFeature(Feature):
    def __init__(self, medicationGroups, thresholdVolumes, checkpointTimes):
        Feature.__init__(self)
        self.medicationGroups = medicationGroups
        self.thresholdVolumes = thresholdVolumes
        self.checkpointTimes = checkpointTimes

    def getColNames(self):
        newColNames = list()
        for vol in self.thresholdVolumes:
            newColNames.append("ivf.secondsUntilCC.%s" % (str(vol)))
        for time in self.checkpointTimes:
            newColNames.append("ivf.CCupToSec.%s" % (str(int(time))))
        return newColNames

class TimeCycleFeature(Feature):
    def __init__(self, prefix="order_time"):
        Feature.__init__(self)
        self.timeAttributes = list()
        self.prefix = prefix

    def addTimeAttribute(self, timeAttr):
        self.timeAttributes.append(timeAttr)

    def getColNames(self):
        newColNames = list()
        for attr in self.timeAttributes:
            newColNames.append("%s.%s" % (self.prefix, attr))
            newColNames.append("%s.%s.sin" % (self.prefix, attr))
            newColNames.append("%s.%s.cos" % (self.prefix, attr))
        return newColNames

class DataExtractor:
    """
    Usage: extractor = DataExtractor(outputFilePath)

    Then use extractor to compute a set of features:
        1) extractor.addClinicalItemFeaturesByName(patientList, clinicalItemNames, prefix, timeIntervals=None)
            patientList - list of int-type patientIds
            clinicalItemNames - list of string-type clinicalItemNames
            prefix - string to be added to feature columns
            timeIntervals - list of int-type time intervals by day to use as features
                - if unspecified, defaults to timeIntervals = [1, 2, 4, 7, 14, 30, 90, 180, 365, 730, 1460]
        2) extractor.addClinicalItemFeaturesByCategory
            same as above, except
            clinicalItemCategoryIds - list of int-type clinicalItemCategoryIds
        3) extractor.addLabFeatures(patientList, baseNames,lookbackTime=None, lookaheadTime=None)
            baseNames - list of string-type base names
        4) extractor.addFlowsheetFeatures(patientList, flowsheetNames,lookbackTime=None, lookaheadTime=None)
            flowsheetNames - list of string-type flowsheet names
        5) extractor.addIVFluidFeatures(thresholdVolumes, checkpointTimes)
            thresholdVolumes - list of int-type thresholdVolumes
            checkpointTimes - list of int-type checkpointTimes
        6) extractor.addTimeCycleFeatures(patientList, timeAttributes=["month","day","hour","minute","second"])
            timeAttributes - can specify any subset of default shown in usage string above
    """
    def __init__(self, outputFileName=None, baseColNames=None):
        self.connFactory = DBUtil.ConnectionFactory()
        self.outputFileName = outputFileName
        self.dataCache = None
        self.patientList = list()
        self.patientTableString = ""
        self.featureIds = list()
        self.baseColNames = \
        ["patient_id", "encounter_id", "order_proc_id", "proc_code", "order_time",
        "abnormal", "result_normal_count", "result_total_count", "all_result_normal"];
        self.features = \
        {
        "clinicalItemByName": list(), "clinicalItemByCategory": list(),
        "lab": list(), "flowsheet": list(), "ivFluid": list(),
        "timeCycle": TimeCycleFeature()
        }

        self.cursors = \
        {
        "clinicalItemByName": list(), "clinicalItemByCategory": list(),
        "lab": list(), "flowsheet": list(), "ivFluid": list(),
        "timeCycle": None
        }


    # ------------- Wrapper Functions Used By extractData.py --------------- #
    def queryClinicalItemsByName(self,clinicalItemNames,patientIds,outputFile=None, col=None, operator=None, prefix=None, daysBins=None):
        # add feature data to self.features
        featureId = "clinicalByName_"+prefix
        if featureId in self.featureIds:
            return []
        self.featureIds.append(featureId)
        feature = ClinicalItemByNameFeature(clinicalItemNames, prefix, col, operator,daysBins)
        self.features["clinicalItemByName"].append(feature)
        return []

    def queryClinicalItemsByCategory(self, clinicalItemCategoryIds, patientIds, outputFile=None, col=None, operator=None, prefix=None, daysBins=None):
        featureId = "clinicalByCategory_"+prefix
        if featureId in self.featureIds:
            return []
        self.featureIds.append(featureId)
        feature = ClinicalItemByCategoryFeature(clinicalItemCategoryIds, prefix, col, operator,daysBins)
        self.features["clinicalItemByCategory"].append(feature)
        return []

    def parseClinicalItemData_singlePatient(self, items):
        # dummy method
        return None

    def addClinicalItemFeatures_singlePatient(self, eventTimes, patientEpisodeByIndexTime, label, daysBins=None):
        patientId = None
        for index_time, patientEpisode in patientEpisodeByIndexTime.iteritems():
            patientId = patientEpisode["patient_id"]
            break
        if patientId in self.patientList:
            return []

        self.patientList.append(patientId)
        for index_time, patientEpisode in patientEpisodeByIndexTime.iteritems():
            self.patientTableString += "\n%s\t%s" % (patientId, index_time)

        return []
    def addTimeCycleFeatures_singlePatient(self, patientEpisodeByIndexTime, prefix, timeAttr):
        featureId = "timeCycle_"+timeAttr
        if featureId in self.featureIds:
            return []
        self.featureIds.append(featureId)
        self.features["timeCycle"].addTimeAttribute(timeAttr)
        return []

    def queryLabResults(self, resultBaseNames, patientIds):
        return []

    def parseLabResultsData_singlePatient(self, tableRows):
        return None

    def addLabFeatures_singlePatient(self, patientEpisodeByIndexTime, labsByBaseName, resultBaseNames, preTimeDelta, postTimeDelta):
        featureId = "lab_"+list(resultBaseNames)[0]+"_"+str(preTimeDelta)
        if featureId in self.featureIds:
            return []
        self.featureIds.append(featureId)
        feature = ResultFeature(resultBaseNames, preTimeDelta, postTimeDelta)
        self.features["lab"].append(feature)
        return []

    def queryFlowsheetResults(self, resultBaseNames, patientIds):
        return []

    def parseFlowsheetResultsData_singlePatient(self, tableRows):
        return None

    def addFlowsheetFeatures_singlePatient(self, patientEpisodeByIndexTime, labsByBaseName, resultBaseNames, preTimeDelta, postTimeDelta):
        featureId = "flowsheet_"+prefix+"_"+str(preTimeDelta)
        if featureId in self.featureIds:
            return []
        self.featureIds.append(featureId)
        feature = ResultFeature(resultBaseNames, preTimeDelta, postTimeDelta)
        self.features["flowsheet"].append(feature)
        return []

    def writeMatrixFile(self, formatter):
        """
        #features ==> dict with feature type keys and dict values containing
        #    feature target data:
        #    featureType     keys/values
        #    ________________________________
        #    "clinicalByName"    {"clinicalItemNames": list, "prefix": <features' col name prefix>, }
        """
        # Initiate cursors and write header row to output
        self.initiateCursors()
        self.writeHeaderRow(formatter)


        # Advance cursors by episode


        #formatter.formatResultDicts(patientEpisodeByIndexTime.values(), colNames);

    def initiateCursors(self):
        if self.features["clinicalItemByName"]:
            for feature in self.features["clinicalItemByName"]:
                prelimQuery = ClinicalPreliminaryQueryByName(self.patientList, feature.clinicalItemNames)
                conn = self.connFactory.connection()
                feature.cursor = conn.cursor()
                feature.cursor.execute(prelimQuery.writeQuery())
                self.baseColNames.extend(feature.getColNames())

        if self.features["clinicalItemByCategory"]:
            for feature in self.features["clinicalItemByCategory"]:
                prelimQuery = ClinicalPreliminaryQueryByCategory(self.patientList, feature.clinicalItemCategoryIds)
                feature.cursor = self.connFactory.connection().cursor().execute(prelimQuery.writeQuery())
                self.baseColNames.extend(feature.getColNames())

        if self.features["timeCycle"].timeAttributes:
            feature = self.features["timeCycle"]
            prelimQuery = TimeCyclePreliminaryQuery(self.patientList)
            feature.cursor = self.connFactory.connection().cursor().execute(prelimQuery.writeQuery())
            self.baseColNames.extend(feature.getColNames())

        if self.features["lab"]:
            for feature in self.features["lab"]:
                prelimQuery = LabPreliminaryQuery(self.patientList, feature.itemNames)
                feature.cursor = self.connFactory.connection().cursor().execute(prelimQuery.writeQuery())
                self.baseColNames.extend(feature.getColNames())

        if self.features["flowsheet"]:
            for feature in self.features["flowsheet"]:
                prelimQuery = FlowsheetPreliminaryQuery(self.patientList, feature.itemNames)
                feature.cursor = self.connFactory.connection().cursor().execute(prelimQuery.writeQuery())
                self.baseColNames.extend(feature.getColNames())

        if self.features["ivFluid"]:
            for feature in self.features["ivFluid"]:
                prelimQuery = IVFluidPreliminaryQuery(self.patientList, feature.medicationGroups)
                feature.cursor = self.connFactory.connection().cursor().execute(prelimQuery.writeQuery())
                self.baseColNames.extend(feature.getColNames())

    def writeHeaderRow(self, formatter):
        formatter.formatTuple(self.baseColNames) 

    def loadPatientEpisodes(self, patientEpisodes):
        # loads patientEpisode data into SQL db table patient_item
        # and returns list of every unique patientId that appears
        patientList = list()
        patientTableString = ""
        for patientEpisode in patientEpisodes:
            if patientEpisode["patient_id"] not in patientList:
                patientList.append(patientEpisode["patient_id"])
            if patientEpisode == patientEpisodes[0]:
                patientTableString += "%s\t%s" % (patientEpisode["patient_id"], patientEpisode("order_time"))
                continue
            patientTableData += "\n%s\t%s" % (patientEpisode["patient_id"], patientEpisode("order_time"))
        patientColString = "patient_id\titem_date"
        columns = [col for col in patientColString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile(StringIO(patientTableString), "patient_item")

        return patientList

    # QUESTION: Add time intervals? -- used for Clinical item features
    def addInitPatientData(self, patientList):
        """
        No longer used.
        Writes first two rows of transposed feature table.
        Row 1 - "patient_id\t<tab-delimited patient_id's, which can be repeated for multiple episodes>"
        Row 2 - "index_time\t<tab-delimited index_time's>"
        """

        # Query for target data
        query = SQLQuery()
        query.addSelect("patient_id, item_date")
        query.addFrom("patient_item")
        patientIdString = str.join(", ", ["\'%s\'" % str(pid) for pid in patientList])
        query.addWhere("patient_id IN (%s)" % (patientIdString))

        # Initialize cursor and query string
        conn = self.connFactory.connection()
        cursor = conn.cursor()
        queryString = DBUtil.parameterizeQueryString(query)

        # Write patient row to text file
        cursor.execute(queryString)
        outputFile = open(self.outputFileName, 'w')
        outputFile.write("patient_id")
        # Iterate over result rows and write data
        row = DBUtil.nextRowModel(cursor)
        while row is not None:
            outputFile.write("\t"+str(row["patient_id"]))
            row = DBUtil.nextRowModel(cursor)

        # Write index_time row to text file
        outputFile.write("\nindex_time")
        cursor.execute(queryString)
        row = DBUtil.nextRowModel(cursor)
        while row is not None:
            outputFile.write("\t"+str(row["index_time"]))
            row = DBUtil.nextRowModel(cursor)

        outputFile.write("\n")

        conn.close()
        outputFile.close()

    def addInitRow(self, prefixes, cols, timeRangeString):
        """
        Writes header column row to output file.
        Used by methods for lab and flowsheet features.
        """
        with open(self.outputFileName,'w') as outputFile:
            outputFile.write("patient_id\tindex_time")
            for prefix in prefixes:
                for col in cols:
                    outputFile.write("\t%s.%s.%s" % (prefix, timeRangeString, col))

    def addInitClinicalRow(self,prefix, timeIntervals):
        """
        Writes header column row to output file.
        Used by methods for clinical item features.
        """
        with open(self.outputFileName,'w') as outputFile:
            outputFile.write("patient_id\tindex_time\tdays_until_end")
            outputFile.write("\t%(prefix)s.preTimeDays\t%(prefix)s.postTimeDays\t%(prefix)s.pre" % {"prefix": prefix})
            for i in timeIntervals:
                colString = "\t%s.pre.%sd" % (prefix, str(i))
                outputFile.write(colString)
            outputFile.write("\t%s.post"%(prefix))
            for i in timeIntervals:
                outputFile.write("\t%s.post.%sd" % (prefix, str(i)))

    def reinitializeEpisodeClinicalData(self, timeIntervals):
        """
        Returns initialized dict of values to be updated for
        clinical item feature computations.
        """
        data = dict()

        for interval in timeIntervals:
            data[("pre", interval)] = 0
            data[("post", interval)] = 0
        data[("pre", None)] = 0
        data[("post", None)] = 0
        data[("pre","timeDays")] = None
        data[("post","timeDays")] = None

        return data

    def updateClinicalDataTracker(self, dataTracker, timeIntervals, episode, item):
        """
        Given an episode and clinical item, updates episode data in
        dataTracker.
        """
        if item["item_date"] is None:
            return

        itemDate = DBUtil.parseDateValue(item["item_date"])
        curPatientDate = DBUtil.parseDateValue(episode["index_time"])
        timeDelta = itemDate - curPatientDate

        # determine if item occurred before or after index_time
        timeKey = "post"
        if itemDate <= curPatientDate:
            timeDelta = curPatientDate - itemDate
            timeKey = "pre"

        # update TimeDays features
        timeDaystimeKey = (timeKey,"timeDays")
        if dataTracker[timeDaystimeKey] == None:
            dataTracker[timeDaystimeKey] = abs(timeDelta)
        elif abs(timeDelta) < dataTracker[timeDaystimeKey]:
            dataTracker[timeDaystimeKey] = abs(timeDelta)

        # update time interval features
        key = None
        if timeKey == "pre":
            dataTracker[("pre",None)] += 1
            deltas = [1 if timeDelta.total_seconds()-float(x)*SECONDS_PER_DAY <= 0 else 0 for x in timeIntervals]
            minIdx = None
            if 1 in deltas:
                minIdx = deltas.index(1)
            if minIdx is not None:
                key = (timeKey,timeIntervals[minIdx])
        else:
            timeDelta = itemDate-curPatientDate
            dataTracker[("post",None)] += 1
            deltas = [1 if timeDelta.total_seconds()-float(x)*SECONDS_PER_DAY <= 0 else 0 for x in timeIntervals]
            minIdx = None
            if 1 in deltas:
                minIdx = deltas.index(1)
            if minIdx is not None:
                key = (timeKey,timeIntervals[minIdx])
        if key is not None:
            dataTracker[key] += 1

    def writeEpisodeClinicalData(self, dataTracker, timeIntervals, episode):
        """
        Given a patient episode and corresponding clinical item data
        stored in dataTracker dict, performs final data computations
        and writes to outputFile
        """
        # aggregate bucket values
        prevInterval = None
        for interval in timeIntervals:
            if interval == 1:
                prevInterval = 1
                continue
            prevtimeKey = ("pre",prevInterval)
            curtimeKey = ("pre",interval)
            dataTracker[curtimeKey] += dataTracker[prevtimeKey]
            prevtimeKey = ("post",prevInterval)
            curtimeKey = ("post",interval)
            dataTracker[curtimeKey] += dataTracker[prevtimeKey]
            prevInterval = interval

        # Print computations to output file
        outputFile = open(self.outputFileName, "a")
        outputFile.write("\n%s\t%s\t0" % (episode["patient_id"], episode["index_time"]))

        # write TimeDays feature
        timeDaysStr = "None"
        if dataTracker["pre","timeDays"] is not None:
            timeDaysStr = "-"+str(dataTracker["pre","timeDays"].total_seconds() / SECONDS_PER_DAY)
        outputFile.write("\t%s" % timeDaysStr)

        timeDaysStr = "None"
        if dataTracker["post","timeDays"] is not None:
            timeDaysStr = str(dataTracker["post","timeDays"].total_seconds() / SECONDS_PER_DAY)
        outputFile.write("\t%s" % timeDaysStr)

        # write pre interval features
        outputFile.write("\t%s" % str(dataTracker[("pre",None)]))
        for interval in timeIntervals:
            outputFile.write("\t%s" % str(dataTracker[("pre",interval)]))
        # write post interval features
        outputFile.write("\t%s" % str(dataTracker[("post",None)]))
        for interval in timeIntervals:
            outputFile.write("\t%s" % str(dataTracker[("post",interval)]))

        outputFile.close()

    def addClinicalItemFeatures(self, patientList, prelimQuery, feature):
        """
        Returns tab-delimited text file containing clinical item features based
        on specified patientList and timeIntervals.
        First performs preliminary query and iterates through cursor to compute
        features and write them to outputFile one patient episode at a time.
        """
        if feature.timeIntervals == None:
            timeIntervals = [1, 2, 4, 7, 14, 30, 90, 180, 365, 730, 1460]

        self.addInitClinicalRow(prefix,timeIntervals)

        conn = self.connFactory.connection()
        cursor = conn.execute(prelimQuery.writeQuery())
        item = DBUtil.nextRowModel(cursor)
        curEpisode = {"patient_id": item["patient_id"], "index_time": item["index_time"]}
        dataTracker = self.reinitializeEpisodeClinicalData(timeIntervals)
        while item is not None:
            episode = {"patient_id": item["patient_id"], "index_time": item["index_time"]}
            if episode != curEpisode:
                if int(curEpisode["patient_id"]) in patientList:
                    self.writeEpisodeClinicalData(dataTracker, timeIntervals, curEpisode)
                    dataTracker = self.reinitializeEpisodeClinicalData(timeIntervals)
                curEpisode = episode
            if int(curEpisode["patient_id"]) in patientList:
                self.updateClinicalDataTracker(dataTracker, timeIntervals, curEpisode, item)

            item = DBUtil.nextRowModel(cursor)
        if int(curEpisode["patient_id"]) in patientList:
            self.writeEpisodeClinicalData(dataTracker, timeIntervals, curEpisode)

        cursor.close()

    def addClinicalItemFeaturesByName(self, patientList, feature):
        prelimQuery = ClinicalPreliminaryQueryByName(patientList, feature)
        self.addClinicalItemFeatures(patientList, prelimQuery, feature)

    def addClinicalItemFeaturesByCategory(self, patientList, feature):
        prelimQuery = ClinicalPreliminaryQueryByCategory(self.patientList, feature)
        self.addClinicalItemFeatures(prelimQuery, feature)

    def itemInRange(self, itemTime, indexTime, lookbackTime, lookaheadTime):
        timeDelta = itemTime-indexTime

        # lookbackTime comparison
        if timeDelta <= timedelta(0):
            if lookbackTime == None or lookbackTime <= timeDelta:
                return True

        # lookaheadTime comparison
        if timeDelta > timedelta(0):
            if lookaheadTime == None or lookaheadTime >= timeDelta:
                return True
        return False

    def reinitializeEpisodeData(self, prefixes):
        """
        Returns initialized dict of values to be updated for
        lab and flowsheet feature computations.
        """
        data = dict()
        for prefix in prefixes:
            data[(prefix, "count")] = 0
            data[(prefix, "countInRange")] = 0
            data[(prefix, "valueList")] = []
            data[(prefix, "first")] = None
            data[(prefix, "last")] = None
            data[(prefix, "proximate")] = None
            data[(prefix, "firstTimeDays")] = None
            data[(prefix, "lastTimeDays")] = None
            data[(prefix, "proximateTimeDays")] = None
        return data

    def addResultFeatures(self,patientList, prelimQuery, feature):
        """
        Returns tab-delimited text file containing lab or flowsheeet features based
        on specified patientList and provided criteria:
            patientList - list of patientIds of interest
            prefixes - either list of lab or flowsheet names of interest
            lookbackTime - how far back to look for items
                - None value indicates no lookback limit, 0 value indicates
                    to not look before episode index_time at all
            lookaheadTime - how far out to look for items
                - None value indicates no lookahead limit, 0 value indicates
                    to not look past episode index time at all
        First performs preliminary query and iterates through cursor to compute
        features and write them to outputFile one patient episode at a time.
        """
        #self.addInitPatientData(patientList)
        cols = ["count","countInRange","min","max","median",\
        "mean","std","first","last","diff","slope","proximate",\
        "firstTimeDays","lastTimeDays","proximateTimeDays"]

        lookbackTimeString = 'None'
        if lookbackTime is not None:
            lookbackTimeString = str(lookbackTime.days)
        lookaheadTimeString = 'None'
        if lookaheadTime is not None:
            lookaheadTimeString = str(lookaheadTime.days)
        timeRangeString = lookbackTimeString+'_'+lookaheadTimeString
        self.addInitRow(prefixes, cols, timeRangeString)

        conn = self.connFactory.connection()
        cursor = conn.execute(prelimQuery.writeQuery())
        item = DBUtil.nextRowModel(cursor)
        curEpisode = {"patient_id": item["patient_id"], "index_time": item["index_time"]}
        dataTracker = self.reinitializeEpisodeData(prefixes)
        while item is not None:
            episode = {"patient_id": item["patient_id"], "index_time": item["index_time"]}
            if episode != curEpisode:
                if int(curEpisode["patient_id"]) in patientList:
                    self.writeEpisodeData(dataTracker, curEpisode, prefixes)
                    dataTracker = self.reinitializeEpisodeData(prefixes)
                curEpisode = episode
            if int(curEpisode["patient_id"]) in patientList:
                self.updateDataTracker(dataTracker, curEpisode, item, lookbackTime, lookaheadTime)

            item = DBUtil.nextRowModel(cursor)
        if int(curEpisode["patient_id"]) in patientList:
            self.writeEpisodeData(dataTracker, curEpisode, prefixes)

        cursor.close()

    def updateDataTracker(self, dataTracker, episode, item, lookbackTime, lookaheadTime):
        """
        Given an episode and lab or flowsheet item, updates episode data in
        dataTracker.
        """

        if item["item_name"] is None:
            return
        itemDate = DBUtil.parseDateValue(item["item_date"])
        curPatientDate = DBUtil.parseDateValue(episode["index_time"])
        timeDelta = itemDate - curPatientDate
        value = item["value"]
        if value is None:
            return
        value = float(value)

        # check if value within range and within date range
        if abs(value) < SENTINEL_RESULT_VALUE and self.itemInRange(itemDate, curPatientDate, lookbackTime, lookaheadTime):
            prefix = item["item_name"]
            # update dataTracker
            dataTracker[(prefix, "count")] += 1
            if "result_in_range_yn" in item:
                if item["result_in_range_yn"] == 'Y':
                    dataTracker[(prefix, "countInRange")] += 1
            dataTracker[(prefix, "valueList")] = dataTracker[(prefix, "valueList")]+[value]

            if dataTracker[(prefix, "first")] is None:
                dataTracker[(prefix, "first")] = value
                dataTracker[(prefix, "firstTimeDays")] = itemDate
            elif dataTracker[(prefix, "firstTimeDays")] > itemDate:
                dataTracker[(prefix, "first")] = value
                dataTracker[(prefix, "firstTimeDays")] = itemDate
            if dataTracker[(prefix, "last")] is None:
                dataTracker[(prefix, "last")] = value
                dataTracker[(prefix, "lastTimeDays")] = itemDate
            elif dataTracker[(prefix, "lastTimeDays")] < itemDate:
                dataTracker[(prefix, "last")] = value
                dataTracker[(prefix, "lastTimeDays")] = itemDate
            if dataTracker[(prefix, "proximate")] is None:
                dataTracker[(prefix, "proximate")] = value
                dataTracker[(prefix, "proximateTimeDays")] = timeDelta
            elif abs(dataTracker[(prefix, "proximateTimeDays")]) > abs(timeDelta):
                dataTracker[(prefix, "proximate")] = value
                dataTracker[(prefix, "proximateTimeDays")] = timeDelta

    def writeEpisodeData(self, dataTracker, episode, prefixes):
        """
        Given a patient episode and corresponding lab or flowsheet item data
        stored in dataTracker dict, performs final data computations
        and writes to outputFile
        """
        # write output
        outputFile = open(self.outputFileName, "a")
        outputFile.write("\n%s\t%s" % (episode["patient_id"], episode["index_time"]))

        for prefix in prefixes:
            valString = str(dataTracker[(prefix, "count")])
            outputFile.write('\t'+valString)

            valString = str(dataTracker[(prefix, "countInRange")])
            outputFile.write('\t'+valString)

            valString = "None"
            if dataTracker[(prefix, "valueList")]:
                valString = str(np.min([float(val) for val in dataTracker[(prefix, "valueList")]]))
            outputFile.write('\t'+valString)

            valString = "None"
            if dataTracker[(prefix, "valueList")]:
                valString = str(np.max([float(val) for val in dataTracker[(prefix, "valueList")]]))
            outputFile.write('\t'+valString)

            valString = "None"
            if dataTracker[(prefix, "valueList")]:
                valString = str(np.median([float(val) for val in dataTracker[(prefix, "valueList")]]))
            outputFile.write('\t'+valString)

            valString = "None"
            if dataTracker[(prefix, "valueList")]:
                valString = str(np.mean([float(val) for val in dataTracker[(prefix, "valueList")]]))
            outputFile.write('\t'+valString)

            valString = "None"
            if dataTracker[(prefix, "valueList")]:
                valString = str(np.std([float(val) for val in dataTracker[(prefix, "valueList")]]))
            outputFile.write('\t'+valString)

            valString = str(dataTracker[(prefix, "first")])
            outputFile.write('\t'+valString)

            valString = str(dataTracker[(prefix, "last")])
            outputFile.write('\t'+valString)

            diff = "None"
            diffTime = None
            if dataTracker[(prefix,"last")] is not None:
                diff = str(float(dataTracker[(prefix, "last")])-dataTracker[(prefix, "first")])
                diffTime = dataTracker[(prefix,"lastTimeDays")]-dataTracker[(prefix,"firstTimeDays")]
            outputFile.write('\t'+diff)

            slope = "None"
            if diff != "None":
                timeDiffDays = (diffTime.total_seconds())/SECONDS_PER_DAY
                if timeDiffDays == 0:
                    slope = "0.0"
                else:
                    slope = str(float(diff)/timeDiffDays)
            outputFile.write('\t'+slope)

            valString = str(dataTracker[(prefix, "proximate")])
            outputFile.write('\t'+valString)

            firstTimeDays = "None"
            if dataTracker[(prefix, "firstTimeDays")] is not None:
                firstTimeDays = str((dataTracker[(prefix, "firstTimeDays")]-DBUtil.parseDateValue(episode["index_time"])).total_seconds()/SECONDS_PER_DAY)
            outputFile.write('\t'+firstTimeDays)

            lastTimeDays = "None"
            if dataTracker[(prefix, "lastTimeDays")] is not None:
                lastTimeDays = str((dataTracker[(prefix, "lastTimeDays")]-DBUtil.parseDateValue(episode["index_time"])).total_seconds()/SECONDS_PER_DAY)
            outputFile.write('\t'+lastTimeDays)

            valString = "None"
            if dataTracker[(prefix, "proximateTimeDays")]:
                valString = str(dataTracker[(prefix, "proximateTimeDays")].total_seconds()/SECONDS_PER_DAY)
            outputFile.write('\t'+valString)

        outputFile.close()

    def addLabFeatures(self, patientList, feature):
        prelimQuery = LabPreliminaryQuery(patientList, feature)
        self.addResultFeatures(patientList, prelimQuery, feature)

    def addFlowsheetFeatures(self, patientList, feature):
        prelimQuery = FlowsheetPreliminaryQuery(patientList, feature)
        self.addResultFeatures(patientList, prelimQuery, feature)

    def reinitializeEpisodeIVFluidData(self):
        """
        Returns initialized dict of values to be updated for
        IV fluid feature computations.
        """
        dataTracker = {\
        "ivFluidItems": list(),
        "timepoints": [0],
        "preBolusVolumes": [0.0],
        "postBolusVolumes": [0.0],
        "infusionRates": [0.0]
        }
        return dataTracker

    def addInitIVFluidRow(self, thresholdVolumes, checkpointTimes):
        with open(self.outputFileName,'w') as outputFile:
            outputFile.write("patient_id\tindex_time")
            for vol in thresholdVolumes:
                colString = "\tivf.secondsUntilCC.%s" % (str(vol))
                outputFile.write(colString)
            for time in checkpointTimes:
                outputFile.write("\tivf.CCupToSec.%s" % (str(int(time))))

    def updateIVFluidDataTracker(self, dataTracker, episode, thresholdVolumes, checkpointTimes):
        """
        Given an episode and IV fluid item, updates episode data in
        dataTracker.
        """
        for item in dataTracker["ivFluidItems"]:
            if item["item_date"] is None:
                return

            itemDate = DBUtil.parseDateValue(item["item_date"])
            curPatientDate = DBUtil.parseDateValue(episode["index_time"])
            timeDelta = itemDate - curPatientDate

            if itemDate >= curPatientDate:  # Found item occuring after index item
                timepoint = (itemDate - curPatientDate).total_seconds();
                if timepoint > dataTracker["timepoints"][-1]:  # New time point, create another entry
                    timeDiff = (timepoint-dataTracker["timepoints"][-1]);
                    newVolume = dataTracker["postBolusVolumes"][-1] + dataTracker["infusionRates"][-1]*timeDiff/60/60;    # Add up any accumulated infusions
                    dataTracker["timepoints"] = dataTracker["timepoints"] + [timepoint];
                    dataTracker["preBolusVolumes"] = dataTracker["preBolusVolumes"] + [newVolume];
                    dataTracker["postBolusVolumes"] = dataTracker["postBolusVolumes"] + [newVolume];
                    dataTracker["infusionRates"] = dataTracker["infusionRates"] + [dataTracker["infusionRates"][-1]];
                if item["min_discrete_dose"] is not None:   # Looks like a bolus volume. Simplifying assumption, assume will always be "ONCE," realizing there may be some "DAILY or BID," etc. items that will be missed
                    dataTracker["postBolusVolumes"][-1] += float(item["min_discrete_dose"]);
                elif item["min_rate"] is not None:  # Looks like a continuous infusion (rate change)
                    dataTracker["infusionRates"][-1] += float(item["min_rate"]);

    def writeEpisodeIVFluidData(self, dataTracker, episode, thresholdVolumes, checkpointTimes):
        """
        Given a patient episode and corresponding IV fluid data
        stored in dataTracker dict, performs final data computations
        and writes to outputFile
        """
        # Print computations to output file
        outputFile = open(self.outputFileName, "a")
        outputFile.write("\n%s\t%s" % (episode["patient_id"], episode["index_time"]))

        # Write thresholdVolume features
        thresholdVolumes.sort();
        for thresholdVolume in thresholdVolumes:
            # find index of first preBolusVolume to exceed the current thresholdVolume
            iTimepoint = None
            volsGreaterThanThresh = [0 if thresholdVolume > preBolusVol else 1 for preBolusVol in dataTracker["preBolusVolumes"]]
            if 1 in volsGreaterThanThresh:
                iTimepoint = volsGreaterThanThresh.index(1)-1

            # write feature to outputFile
            outputString = "\tNone"
            if iTimepoint is not None:
                if thresholdVolume <= dataTracker["postBolusVolumes"][iTimepoint]:    # Threshold volume within current post bolus volumes, so happened at this timepoint
                    outputString = "\t"+str(dataTracker["timepoints"][iTimepoint])
                else:   # General case, threshold volume was hit at some point during infusion ramp starting from this timepoint
                    # Do some algebra to interpolate the time from until infusion rate ramp will hit target threshold volume
                    timeUntilThreshold = (thresholdVolume - dataTracker["postBolusVolumes"][iTimepoint]) * 60*60 / dataTracker["infusionRates"][iTimepoint];   # Beware divide by zero, but if data constructed properly, shouldn't be possible
                    outputString = "\t" + str(dataTracker["timepoints"][iTimepoint] + timeUntilThreshold);

            outputFile.write(outputString)

        # Write checkpointTimes features
        checkpointTimes.sort();
        for checkpointTime in checkpointTimes:
            # find index of first timepoint that exceeds the current checkpointTime
            iTimepoint = len(dataTracker["timepoints"])-1

            timesGreaterThanCheckpointTime = [0 if checkpointTime >= timepoint else 1 for timepoint in dataTracker["timepoints"]]
            if 1 in timesGreaterThanCheckpointTime:
                iTimepoint = timesGreaterThanCheckpointTime.index(1)-1

            # dataTracker["timepoints"][iTimepoint] should now be the last one on or before the checkpointTime
            # Since starting at time zero, should always be able to find a
            #   pre-timepoint like this for any (non-negative) checkpoint time
            timeDiff = (checkpointTime-dataTracker["timepoints"][iTimepoint]);
            checkpointVolume = dataTracker["postBolusVolumes"][iTimepoint] + dataTracker["infusionRates"][iTimepoint]*timeDiff/60/60;
            outputFile.write("\t%s" % str(checkpointVolume))

        outputFile.close()

    def expandIVFluidItems(self, ivFluidItems):
        """Return a copy of the ivFluidItems list, assumed to be in chronologically sorted order,
        but insert additional items to mark time points where IV infusions are noted to end.
        Signify with negative min_rate values, and using the "start_taking_time" to mark the time of these end events.
        """
        expandedIVFluidItems = list();
        infusionEndItemHeap = list();   # Interpret as heap (priority queue) of 2-ples keyed by end-date for infusion items, so know when to "turn off" their infusion rates
        for ivFluidItem in ivFluidItems:
            nextTime = ivFluidItem["item_date"];
            while infusionEndItemHeap and infusionEndItemHeap[0][0] <= nextTime:    # See if passed any infusion end times, then record an entry for those
                (endTime, infusionEndItem) = heappop(infusionEndItemHeap);
                expandedIVFluidItems.append(infusionEndItem);
            expandedIVFluidItems.append(ivFluidItem);
            if ivFluidItem["min_rate"] is not None:  # Looks like a continuous infusion
                # Create an item copy to signify end of infusion, and keep track of when to add it later
                infusionEndItem = dict(ivFluidItem);
                infusionEndItem["item_date"] = infusionEndItem["item_end_date"];
                infusionEndItem["min_rate"] = str(-float(infusionEndItem["min_rate"]));
                heappush(infusionEndItemHeap, (ivFluidItem["item_end_date"], infusionEndItem) );  # Keep track of infusion end time
        # Final check if any end infusion items left to account for
        while infusionEndItemHeap:
            (endTime, infusionEndItem) = heappop(infusionEndItemHeap);
            expandedIVFluidItems.append(infusionEndItem);
        return expandedIVFluidItems;

    def createIVFluidCursor(self, patientList, feature):
        prelimQuery = IVFluidPreliminaryQuery(patientList, feature.medicationGroups)

        conn = self.connFactory.connection()
        return conn.execute(prelimQuery.writeQuery())

    def addIVFluidFeatures(self,patientList, feature):
        """
        Returns tab-delimited text file containing IVFluid features based
        on specified patientList, thresholdVolumes, and checkpointTimes.
        First performs preliminary query and iterates through cursor to compute
        features and write them to outputFile one patient episode at a time.
        """

        #self.addInitIVFluidRow(thresholdVolumes, checkpointTimes)

        conn = self.connFactory.connection()
        cursor = conn.execute(prelimQuery.writeQuery())
        item = DBUtil.nextRowModel(cursor)
        curEpisode = {"patient_id": item["patient_id"], "index_time": item["index_time"]}
        dataTracker = self.reinitializeEpisodeIVFluidData()
        while item is not None:
            episode = {"patient_id": item["patient_id"], "index_time": item["index_time"]}
            if episode != curEpisode:
                if int(curEpisode["patient_id"]) in patientList:
                    dataTracker["ivFluidItems"] = self.expandIVFluidItems(dataTracker["ivFluidItems"])
                    self.updateIVFluidDataTracker(dataTracker, curEpisode, thresholdVolumes, checkpointTimes)
                    self.writeEpisodeIVFluidData(dataTracker, curEpisode, thresholdVolumes, checkpointTimes)
                    dataTracker = self.reinitializeEpisodeIVFluidData()
                curEpisode = episode
            elif int(curEpisode["patient_id"]) in patientList:
                dataTracker["ivFluidItems"] += [item]

            item = DBUtil.nextRowModel(cursor)
        if int(curEpisode["patient_id"]) in patientList:
            dataTracker["ivFluidItems"] = self.expandIVFluidItems(dataTracker["ivFluidItems"])
            self.updateIVFluidDataTracker(dataTracker, curEpisode, thresholdVolumes, checkpointTimes)
            self.writeEpisodeIVFluidData(dataTracker, curEpisode, thresholdVolumes, checkpointTimes)

        cursor.close()

    def addInitTimeCycleRow(self,timeAttributes,prefix):
        with open(self.outputFileName,'w') as outputFile:
            outputFile.write("patient_id\tindex_time")
            for attr in timeAttributes:
                outputFile.write("\t%s.%s" % (prefix, attr))
                outputFile.write("\t%s.%s.sin" % (prefix, attr))
                outputFile.write("\t%s.%s.cos" % (prefix, attr))

    def writeTimeCycleFeature(self, episode, timeAttributes):
        """
        Given a patient episode, performs feature computations on
        episdoe["index_time"] based on specified timeAttributes and
        writes to outputFile.
        """
        with open(self.outputFileName,'a') as outputFile:
            outputFile.write("\n%s\t%s" % (episode["patient_id"], episode["index_time"]))

            for timeAttr in timeAttributes:
                timeObj = DBUtil.parseDateValue(episode["index_time"])
                # Use introspection (getattr) to extract some time feature from the time object,
                #   as well as the maximum and minimum possible values to set the cycle range
                maxValue = getattr(timeObj.max, timeAttr);
                thisValue = getattr(timeObj, timeAttr);
                minValue = getattr(timeObj.min, timeAttr);
                radians = 2*np.pi * (thisValue-minValue) / (maxValue+1-minValue);

                outputFile.write("\t%s" % (thisValue))
                outputFile.write("\t%s" % (np.sin(radians)))
                outputFile.write("\t%s" % (np.cos(radians)))

    def createTimeCycleCursor(self, patientList, feature):
        prelimQuery = TimeCyclePreliminaryQuery(patientList)

        conn = self.connFactory.connection()
        return conn.execute(prelimQuery.writeQuery())

    def addTimeCycleFeatures_temp(self, patientList, feature):
        """
        Add features for all patient episodes of patientList based on the timeAttr strings
        in timeAttributes. Default is to include all possible time attributes
        ("month","day","hour","minute","second"), including the sine and cosine
        of the time attribute value relative to the maximum possible value to reflect
        cyclical time patterns (e.g., seasonal patterns over months in a year,
        or daily cycle patterns over hours in a day).
        """

        #self.addInitTimeCycleRow(timeAttributes, prefix)
        """
        episode = DBUtil.nextRowModel(cursor)
        while episode is not None:
            self.writeTimeCycleFeature(episode, timeAttributes)
            episode = DBUtil.nextRowModel(cursor)

        conn.close()
        """

    def transposeMatrixFile(self):
        """
        Transposes tab-delimited file.
        Currently unused method.
        """
        transposedLines = [[]]*(len(self.patientRow)+1)
        with open(self.outputFileName) as infile:
            for line in infile:
                items = str.split(line.strip(),'\t')
                for i,item in enumerate(items):
                    transposedLines[i] = transposedLines[i] +[item]
        # write to new file
        f = open(self.outputFileName+".transpose", "w")
        for line in transposedLines:
            f.write(str.join('\t',line)+'\n')
        f.close()

    def loadMapData(self,filename):
        """#Read the named file's contents through a TabDictReader to enable data extraction.
        #If cannot find file by absolute filename, then look under default mapdata directory.
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

# TODO: comment PreliminaryQuery classes
class PreliminaryQuery:
    def __init__(self, patientIds):
        self.mainSelectClause = ""
        self.mainOrderByClause = ""
        self.subSelectClause = ""
        self.subFromClause = ""
        self.subWhereClause = ""
        self.subOrderByClause = ""
        self.patientIds = patientIds

    def writeQuery(self):
        query = SQLQuery()
        query.addSelect(self.mainSelectClause)

        mainFromClause = "(\n"
        subquery1 = SQLQuery()
        subquery1.addSelect("patient_id, item_date")
        subquery1.addFrom("patient_item")
        patientListString = str.join(", ", ["\'%s\'" % str(patId) for patId in self.patientIds])
        subquery1.addWhere("patient_id IN (%s)" % patientListString)
        subquery1String = DBUtil.parameterizeQueryString(subquery1)
        mainFromClause += subquery1String+'\n) AS pat'
        query.addFrom(mainFromClause)

        subquery2 = SQLQuery()
        subquery2.addSelect(self.subSelectClause)
        subquery2.addFrom(self.subFromClause)
        subquery2.addWhere(self.subWhereClause)
        subquery2.addOrderBy(self.subOrderByClause)
        subquery2String = DBUtil.parameterizeQueryString(subquery2)
        mainJoinClause = "(\n" +subquery2String+"\n) AS item\n"
        query.addJoin(mainJoinClause, self.mainJoinCriteria, "LEFT")

        query.addOrderBy(self.mainOrderByClause)

        return DBUtil.parameterizeQueryString(query)

    def loadMapData(self,filename):
        """#Read the named file's contents through a TabDictReader to enable data extraction.
        #If cannot find file by absolute filename, then look under default mapdata directory.
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

class ClinicalPreliminaryQuery(PreliminaryQuery):
    def __init__(self, patientIds, clinicalItemIds):
        PreliminaryQuery.__init__(self, patientIds)
        self.mainSelectClause = "pat.patient_id as patient_id, pat.item_date as index_time, item.item_date"
        self.mainOrderByClause = "pat.patient_id, pat.item_date, item.item_date"
        self.subSelectClause = "patient_id, item_date"
        self.subFromClause = "patient_item"
        clinicalItemIdsString = str.join(", ", [str(itemId) for itemId in clinicalItemIds])
        patientIdString = str.join(', ', [str(patId) for patId in patientIds])
        self.subWhereClause = "clinical_item_id IN (%s)\nAND patient_id IN (%s)" % (clinicalItemIdsString, patientIdString)
        self.subOrderByClause = "patient_id, item_date"
        self.mainJoinCriteria = "pat.patient_id=item.patient_id"

    def extractClinicalItemIds(self, whereClause):
        query = SQLQuery()
        query.addSelect("clinical_item_id")
        query.addFrom("clinical_item")
        query.addWhere(whereClause)
        results = DBUtil.execute(query)
        return [row[0] for row in results]

class ClinicalPreliminaryQueryByName(ClinicalPreliminaryQuery):
    def __init__(self, patientIds, clinicalItemNames):
        whereClause = str.join(" or ", ["name like \'%s\'" % n for n in clinicalItemNames])
        ClinicalPreliminaryQuery.__init__(self, patientIds, self.extractClinicalItemIds(whereClause))

class ClinicalPreliminaryQueryByCategory(ClinicalPreliminaryQuery):
    def __init__(self, patientIds, clinicalItemCategoryIds):
        whereClause = "clinical_item_category_id IN (%s)" % str.join(", ", [str(x) for x in clinicalItemCategoryIds])
        ClinicalPreliminaryQuery.__init__(self, patientIds, self.extractClinicalItemIds(whereClause))

class LabPreliminaryQuery(PreliminaryQuery):
    def __init__(self, patientIds, baseNames):
        PreliminaryQuery.__init__(self, patientIds)
        self.mainSelectClause = "patient_id, pat.item_date as index_time, item.base_name as item_name, item.ord_num_value as value, result_flag, result_in_range_yn, result_time as item_date"
        self.mainOrderByClause = "pat.patient_id, pat.item_date, item_name, item.result_time"
        self.subSelectClause = "pat_id, base_name, ord_num_value, result_flag, result_in_range_yn, sor.result_time"
        self.subFromClause = "stride_order_results as sor, stride_order_proc as sop"
        baseNameString = str.join(", ", ["\'%s\'" % baseName for baseName in baseNames])
        patientIdString = str.join(", ", ["\'%s\'" % str(pid) for pid in patientIds])
        self.subWhereClause = "sor.order_proc_id = sop.order_proc_id\nAND base_name IN (%s)\nAND pat_id IN (%s)" % (baseNameString, patientIdString)
        self.subOrderByClause = "pat_id, base_name, sor.result_time"
        self.mainJoinCriteria = "pat.patient_id=cast(item.pat_id AS INT)"

class FlowsheetPreliminaryQuery(PreliminaryQuery):
    def __init__(self, patientIds, flowsheetNames):
        PreliminaryQuery.__init__(self, [int(pid) for pid in patientIds])
        self.mainSelectClause = "patient_id, pat.item_date as index_time, item.flowsheet_name as item_name, item.flowsheet_value as value, shifted_record_dt_tm as item_date"
        self.mainOrderByClause = "pat.patient_id, pat.item_date, item_name, item_date"
        self.subSelectClause = "pat_anon_id , flo_meas_id , flowsheet_name , flowsheet_value , shifted_record_dt_tm"
        self.subFromClause = "stride_flowsheet"
        flowsheetNameString = str.join(", ", ["\'%s\'" % name for name in flowsheetNames])
        patientIdString = str.join(", ", ["\'%s\'" % str(pid) for pid in patientIds])
        self.subWhereClause = "flowsheet_name IN (%s)\n AND pat_anon_id IN (%s)" %(flowsheetNameString, patientIdString)
        self.subOrderByClause = "pat_anon_id , flowsheet_name, shifted_record_dt_tm"
        self.mainJoinCriteria = "pat.patient_id==item.pat_anon_id"

class IVFluidPreliminaryQuery(PreliminaryQuery):
    def __init__(self, patientIds, medicationGroups):
        PreliminaryQuery.__init__(self, patientIds)
        medicationIds = self.extractMedicationIds(medicationGroups)
        self.mainSelectClause = "pat.patient_id as patient_id, pat.item_date as index_time, start_taking_time as item_date, end_taking_time as item_end_date, freq_name , min_discrete_dose , min_rate"
        self.mainOrderByClause = "pat.patient_id, pat.item_date, item.item_date, item_end_date"
        self.subSelectClause = "pat_id, medication_id, start_taking_time, end_taking_time, freq_name, min_discrete_dose, min_rate"
        self.subFromClause = "stride_order_med"
        patientIdString = str.join(", ", ["\'%s\'" % str(pid) for pid in patientIds])
        freqClauses = ["freq_name not like \'%%%s%%\'" % freq for freq in ["PRN", "PACU", "ENDOSCOPY"]]
        ignoredFreqString = str.join(" AND ", freqClauses)
        tempWhereClause = "medication_id IN (%s)\n" % str.join(", ", ["\'%s\'" % med for med in medicationIds])
        tempWhereClause += "AND pat_id IN (%s)\n" % patientIdString
        tempWhereClause += "AND %s\n" % ignoredFreqString
        tempWhereClause += "AND end_taking_time is not null"
        self.subWhereClause = tempWhereClause
        self.subOrderByClause = "pat_id , start_taking_time , end_taking_time"
        self.mainJoinCriteria = "pat.patient_id=item.pat_id"

    def extractMedicationIds(self, medicationGroups):
        ivfMedIds = set();
        for row in loadMapData("Medication.IVFluids"):
            if row["group"] in medicationGroups:
                ivfMedIds.add(row["medication_id"]);
        return list(ivfMedIds)

class TimeCyclePreliminaryQuery(PreliminaryQuery):

    def __init__(self, patientList):
        self.patientIds = patientList

    def writeQuery(self):
        query = SQLQuery()
        query.addSelect("patient_id, item_date")
        query.addFrom("patient_item")
        patientListString = str.join(", ", ["\'%s\'" % str(patId) for patId in self.patientIds])
        query.addWhere("patient_id IN (%s)" % patientListString)
        return DBUtil.parameterizeQueryString(query)


if __name__ == "__main__":
    extractor = DataExtractor("medinfo/dataconversion/test/dataExtraction_test.out")
    patientList = list() # to input target patients
    targetData = dict() # to input target tables and columns
    targetData["patientList"] = []
    extractor.createMatrixFile(patientList, targetData)
