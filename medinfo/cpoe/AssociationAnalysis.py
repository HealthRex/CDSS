#!/usr/bin/env python
import sys, os
import json
import time;
import math;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.DBUtil import DB_CONNECTOR_MODULE;
IntegrityError = DB_CONNECTOR_MODULE.IntegrityError;
from medinfo.db.Model import SQLQuery, generatePlaceholders;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;
from Env import DATE_FORMAT;

from DataManager import DataManager;

from Const import DELTA_NAME_BY_SECONDS, SECONDS_PER_DAY;

from Util import log;


class AnalysisOptions:
    """Simple struct to pass filter parameters on which records to do analysis on"""
    def __init__(self):
        self.patientIds = None;
        self.startDate = None;
        self.endDate = None;
        self.bufferFile = None;
        self.deltaSecondsOptions = None;    # Seconds values / suffixes to look for count fields to update

class AssociationAnalysis:
    """Pre-Computation module to sort through data on patient clinical items
    (orders, lab results, problem list entries, etc.) and aggregate
    statistics on item associations.

    Can effectively parallelize this process by working on different patient ID subsets, but beware that
    subsequent persistence into database can be even more costly.
    If building model buffers into temporary files, then likely want to merge buffers in application memory
    before persisting into database. Requires a lot of RAM available, but should not be much more than
    2x one buffer size (keeping two in memory as prepare to merge), as the keys/indexes of the buffers should
    be largely similar (one per association count recorded), it is just the counts that need updating.

    Benchmark numbers: ~3300 patients across 4 years of data
    Association Analysis
        0.2 hours - Patient data query
        7   hours - Calculate patient data associations in memory
        1.5 hours - Save association data buffer to disk as compressed JSON object
    Persist    / Update Database with Association Data
        0.2 hours - Load association data buffer back from disk (compressed JSON object)
        2   hours - Prepare baseline (zero) records in database in preparation for increments
       12   hours - Increment values in database based on association data
        1.5 hours - Record patient_item records as "analyzed"

    Running batches of 3,000-5,000 patients with ~3,000 possible clinical items yields ~6M associations,
     requiring ~25GB memory for learning then ~45GB memory to reload and commit as a buffer file.

    Suggestion: Break up input patientID list into discrete subsets and run AssociationAnalysis on each with -b
    option to do parallel association counting (on a server with enough RAM to do all in memory),
    storing results in buffer files with a common name prefix.
    Run a single AssociationAnalysis with -b option on the buffer file name prefix
    (and -u to limit number of patient item updates per query), to sequentially load and merge all buffer files
    into one aggregate buffer file to commit to database in one pass.
    """
    connFactory = None; # Allow specification of alternative DB connection source
    patientsPerCommit = None; # Commit any bufferred analysis results to the database after analyzing this many patients.  If None, will wait until the end before committing, so less DB hits, but will lose  progress if script cancelled midway
    associationsPerCommit = None;   # Commit buffered analysis results if accrue this many association results to avoid risk of running over runtime memory limitations
    itemsPerUpdate = None;  # When updating analyze_dates for patient_items, do so for this many blocks at a time to avoid avoid loading MySQL query time
    
    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source
        self.dataManager = DataManager();
        self.patientsPerCommit = None;
        self.associationsPerCommit = None;
        self.itemsPerUpdate = None;

    def makeUpdateBuffer(self, existingBuffer=None):
        """Factory method to prepare a blank "updateBuffer" to store association increment data.
        Is really just a dictionary for simple JSON conversion, but instantiate here to control
        expected attributes / keys;
        If exitingBuffer is not None, assume that is a previous one that we wish to
        clear / blank out.
        """
        updateBuffer = existingBuffer;
        if updateBuffer is None:
            updateBuffer = dict();
        updateBuffer.clear();
        updateBuffer["nAssociations"] = 0;
        updateBuffer["analyzedPatientItemIds"] = set();
        updateBuffer["incrementDataByItemIdPair"] = dict();
        return updateBuffer;

    def analyzePatientItems(self, analysisOptions):
        """Primary run function to analyze patient clinical item data and 
        record updated stats to the respective database tables.
        
        Does the analysis only for records pertaining to the given patient IDs
        (provides a way to limit the extent of analysis depending on params).
        
        Will also record analyze_date timestamp on any records analyzed,
        so that analysis will not be repeated if called again on the same records.
        """
        progress = ProgressDots();
        conn = self.connFactory.connection();

        try:
            # Preload lookup data to facilitate rapid checks and filters later
            linkedItemIdsByBaseId = self.dataManager.loadLinkedItemIdsByBaseId(conn=conn);
        
            # Keep an in memory buffer of the updates to be done so can stall and submit them
            #   to the database in batch to minimize inefficient DB hits
            updateBuffer = self.makeUpdateBuffer();
            log.info("Main patient item query...")
            for iPatient, patientItemList in enumerate(self.queryPatientItemsPerPatient(analysisOptions, progress=progress, conn=conn)):
                log.debug("Calculate associations for Patient %d's %d patient items. %d associations in buffer." % (iPatient, len(patientItemList), updateBuffer["nAssociations"]) );
                self.updateItemAssociationsBuffer(patientItemList, updateBuffer, analysisOptions, linkedItemIdsByBaseId, progress=progress);
                if self.readyForIntervalCommit(iPatient, updateBuffer, analysisOptions):
                    log.info("Commit after %s patients" % (iPatient+1) );
                    self.persistUpdateBuffer(updateBuffer, linkedItemIdsByBaseId, analysisOptions, iPatient, conn=conn);  # Periodically commit update buffer
                else:   # If not committing, still send a quick arbitrary query to DB, 
                        # otherwise connection may get recycled because DB thinks timeout with no interaction
                    DBUtil.execute("select 1+1", conn=conn);
            log.info("Final commit / persist");
            self.persistUpdateBuffer(updateBuffer, linkedItemIdsByBaseId, analysisOptions, -1, conn=conn);  # Final update buffer commit. Don't use iPatient here, as may collide if interval commit happened to land on last patient
        finally:
            conn.close();
        progress.PrintStatus();

    def queryPatientItemsPerPatient(self, analysisOptions, progress=None, conn=None):
        """Query the database for an ordered list of patient clinical items, 
        in the order in which they occurred.
        This could be a large amount of data, so option to provide
        list of specific patientIds or date ranges to query for.  In either case,
        results will be returned as an iterator over individual lists
        for each patient.  Lists will contain RowItemModels, each with data:
            * patient_id
            * encounter_id
            * clinical_item_id
            * item_date
            * analyze_date
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        
        # Reset for actual data selects
        query= SQLQuery(); 
        query.addSelect("pi.patient_item_id");
        query.addSelect("pi.patient_id");
        query.addSelect("pi.encounter_id");
        query.addSelect("pi.clinical_item_id");
        query.addSelect("pi.item_date");
        query.addSelect("pi.analyze_date");
        query.addFrom("patient_item as pi");
        query.addFrom("clinical_item as ci");
        query.addWhere("pi.clinical_item_id = ci.clinical_item_id");
        query.addWhere("ci.analysis_status <> 0");  # Skip steps designated to be ignored
        if analysisOptions.patientIds is not None:
            query.addWhereIn("patient_id", analysisOptions.patientIds );
        if analysisOptions.startDate is not None:
            query.addWhereOp("pi.item_date",">=", analysisOptions.startDate);
        if analysisOptions.endDate is not None:
            query.addWhereOp("pi.item_date","<", analysisOptions.endDate);
        query.addOrderBy("pi.patient_id");
        query.addOrderBy("pi.item_date");
        query.addOrderBy("pi.clinical_item_id");

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();

        # Do one massive query, but yield data for one patient at a time.
        # This should minimize the number of DB queries and the amount of
        #   data that must be kept in memory at any one time.
        cursor.execute( str(query), tuple(query.params) );

        currentPatientId = None;
        currentPatientData = list();

        headers = ["patient_item_id","patient_id","encounter_id","clinical_item_id","item_date","analyze_date"];

        row = cursor.fetchone();
        while row is not None:
            (patient_item_id, patientId, encounter_id, clinicalItemId, itemDate, analyzeDate) = row;
            if currentPatientId is None:
                currentPatientId = patientId;

            if patientId != currentPatientId:
                # Changed user, yield the existing data for the previous user
                yield currentPatientData;
                # Update our data tracking for the current user
                currentPatientId = patientId;
                currentPatientData = list();

            rowModel = RowItemModel( row, headers );
            currentPatientData.append( rowModel );
            
            row = cursor.fetchone();

        # Yield the final user's data
        yield currentPatientData;

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();
    
    def updateItemAssociationsBuffer(self, patientItemList, updateBuffer, analysisOptions, linkedItemIdsByBaseId=None,  progress=None):
        """Given a list of data on patient clinical items, 
        ordered by item event date, increment information in the 
        updateBuffer to inform subsequent updates to the clinical_item_association
        stats based on all item pairs observed.
        
        Will discount item pairs where both have their analyze_date already recorded.
        After done, also provide updateBuffer info for subsequent setting the analyze_date 
        for all (completed) patient_items from this patient to the current time so that 
        subsequent queries will know they have already been accounted for.
        """
        # Keep track of which items to mark as newly analyzed
        newlyAnalyzedPatientItemIdSet = set();

        # Keep track of which subsequent items have been analyzed, so we don't count further duplicates (just the first ones found)
        subsequentItemIds = set();
        # Keep track of all item pairs encountered to avoid counting patient level duplicates
        encounterIdPairsByItemIdPair = dict();

        patientId = None;
        for iItem1, patientItem1 in enumerate(patientItemList):
            if patientId is None:
                patientId = patientItem1["patient_id"];

            subsequentItemIds.clear();

            for iItem2, patientItem2 in enumerate(patientItemList):
                itemIdPair = (patientItem1["clinical_item_id"], patientItem2["clinical_item_id"]);
                encounterIdPair = (patientItem1["encounter_id"], patientItem2["encounter_id"]);

                # Verify is not a previously composite linked item pair, in which case no meaningful asssociation stats to calculate
                #   and that the item dates are in non-negative direction
                isPairToAnalyze = self.acceptableClinicalItemPair(patientItem1, patientItem2, linkedItemIdsByBaseId );
                if isPairToAnalyze:
                    if (patientItem1["analyze_date"] is None or patientItem2["analyze_date"] is None):
                        # Record the stat update if this pair has not already been analyzed/recorded before
                        isNewSubsequentItem = patientItem2["clinical_item_id"] not in subsequentItemIds;   # Track repeats
                        isNewPair = itemIdPair not in encounterIdPairsByItemIdPair; # Pair ever seen for this patient
                        isNewPairWithinEncounter = (encounterIdPair[0]==encounterIdPair[-1]) and (isNewPair or encounterIdPair not in encounterIdPairsByItemIdPair[itemIdPair]);    # Pair ever seen for a common encounter combination

                        self.updateClinicalItemAssociationBuffer( patientItem1, patientItem2, isNewSubsequentItem, isNewPair, isNewPairWithinEncounter, updateBuffer, analysisOptions );
                    
                        if patientItem1["analyze_date"] is None:
                            newlyAnalyzedPatientItemIdSet.add(patientItem1["patient_item_id"]);
                        if patientItem2["analyze_date"] is None:
                            newlyAnalyzedPatientItemIdSet.add(patientItem2["patient_item_id"]);
                    subsequentItemIds.add(patientItem2["clinical_item_id"]);

                    if itemIdPair not in encounterIdPairsByItemIdPair:
                        encounterIdPairsByItemIdPair[itemIdPair] = set();
                    encounterIdPairsByItemIdPair[itemIdPair].add(encounterIdPair);

            # Update progress meter if available
            if progress is not None:
                progress.Update();

        # Record this analysis date to any unmarked records
        if "analyzedPatientItemIds" not in updateBuffer:
            updateBuffer["analyzedPatientItemIds"] = set();
        updateBuffer["analyzedPatientItemIds"].update(newlyAnalyzedPatientItemIdSet);

    def updateClinicalItemAssociationBuffer(self, patientItem1, patientItem2, isNewSubsequentItem, isNewPair, isNewPairWithinEncounter, updateBuffer, analysisOptions, itemIdPair=None):
        """Identify and record in the updateBuffer which statistics on associations 
        between the two clinical items based on the new piece of observed item pair evidence given.  
        Use isNew parameters to delineate uniqueness parameters to determine whether to count this pair for different metrics.
        
        Default to recording increments for pair (patientItem1["clinical_item_id"],patientItem2["clinical_item_id"]).
        If itemIdPair explicitly specified, then use that instead.
        """
        # Determine which time threshold count windows to update
        deltaSecondsOptions = analysisOptions.deltaSecondsOptions;
        if deltaSecondsOptions is None:
            deltaSecondsOptions = DELTA_NAME_BY_SECONDS.keys();

        # Convert timeDelta object into simple numerical representation (seconds as a real number) to facilitate some arithmetic
        timeDelta = patientItem2["item_date"] - patientItem1["item_date"];
        secondsDelta = (timeDelta.days*SECONDS_PER_DAY + timeDelta.seconds);

        if secondsDelta < 0:
            # Shouldn't have been called in the first place. Extra check to only record forward / non-negative associations
            return;
        
        if itemIdPair is None:
            clinicalItemId1 = patientItem1["clinical_item_id"];
            clinicalItemId2 = patientItem2["clinical_item_id"];
            itemIdPair = (clinicalItemId1, clinicalItemId2);

        # Count variant prefixes to use based on classifications of new items
        countPrefixes = [""];   # Always do at least the base item count
        if isNewPair:
            countPrefixes.append("patient_");
        if isNewPairWithinEncounter:
            countPrefixes.append("encounter_");
        
        if "incrementDataByItemIdPair" not in updateBuffer:
            updateBuffer["incrementDataByItemIdPair"] = dict();
            updateBuffer["nAssociations"] = 0;
        if str(itemIdPair) not in updateBuffer["incrementDataByItemIdPair"]:
            updateBuffer["incrementDataByItemIdPair"][str(itemIdPair)] = dict();
            updateBuffer["nAssociations"] += 1;
        incrementData = updateBuffer["incrementDataByItemIdPair"][str(itemIdPair)];
        
        # Decide on columns to increment pair association with time dependency
        for countPrefix in countPrefixes:
            countField = countPrefix+"count_any";
            if countField not in incrementData:
                incrementData[countField] = 0;
            incrementData[countField] += 1;

            for secondsOption in deltaSecondsOptions:
                if secondsDelta <= secondsOption:
                    countField = countPrefix+"count_%d" % secondsOption;
                    if countField not in incrementData:
                        incrementData[countField] = 0;
                    incrementData[countField] += 1;

            sumField = countPrefix+"time_diff_sum";
            if sumField not in incrementData:
                incrementData[sumField] = 0;
            incrementData[sumField] += secondsDelta;

            sumField = countPrefix+"time_diff_sum_squares";
            if sumField not in incrementData:
                incrementData[sumField] = 0;
            incrementData[sumField] += secondsDelta**2;

    def readyForIntervalCommit(self, iPatient, updateBuffer, analysisOptions):
        isReady = False;
        isReady = isReady or (self.patientsPerCommit is not None and (iPatient % self.patientsPerCommit) == 0);
        isReady = isReady or (self.associationsPerCommit is not None and "nAssociations" in updateBuffer and updateBuffer["nAssociations"] > self.associationsPerCommit);
        return isReady;
    
    
    def mergeBuffers(self, bufferOne, bufferTwo):
        if "analyzedPatientItemIds" not in bufferOne: 
            bufferOne["analyzedPatientItemIds"] = set();
        else:
            bufferOne["analyzedPatientItemIds"].update(bufferTwo["analyzedPatientItemIds"]);

        if "nAssociations" not in bufferOne:
            bufferOne["nAssociations"] = 0
        else:
             bufferOne["nAssociations"] = bufferOne["nAssociations"] + bufferTwo["nAssociations"]

        if "incrementDataByItemIdPair" not in bufferOne:
            bufferOne["incrementDataByItemIdPair"] = dict()
        if "incrementDataByItemIdPair" not in bufferTwo:
            bufferTwo["incrementDataByItemIdPair"] = dict()

        # then fill up any remaining id pairs from buffer two. if you have some in buffer two that are also in buffer one, then add those specific ones together
        for key, value in bufferTwo["incrementDataByItemIdPair"].iteritems():
            if key not in bufferOne["incrementDataByItemIdPair"]:
                bufferOne["incrementDataByItemIdPair"][key] = bufferTwo["incrementDataByItemIdPair"][key]
            else:
                for key2, value2 in bufferTwo["incrementDataByItemIdPair"][key].iteritems():
                    if key2 not in bufferOne["incrementDataByItemIdPair"][key]:
                        bufferOne["incrementDataByItemIdPair"][key][key2]=bufferTwo["incrementDataByItemIdPair"][key][key2]
                    else: 
                        bufferOne["incrementDataByItemIdPair"][key][key2]+=bufferTwo["incrementDataByItemIdPair"][key][key2]

        return bufferOne

    def bufferDecay (self, bufferDecay, decayValue):
        if "incrementDataByItemIdPair" in bufferDecay:
            for key, value in bufferDecay["incrementDataByItemIdPair"].iteritems():
                for key2, value2 in bufferDecay["incrementDataByItemIdPair"][key].iteritems():
                    bufferDecay["incrementDataByItemIdPair"][key][key2] *= decayValue
        return bufferDecay    
    

    def persistUpdateBuffer(self, updateBuffer, linkedItemIdsByBaseId, analysisOptions, iPatient=None, conn=None):
        if analysisOptions.bufferFile is None:
            linkedItemIdsByBaseId = self.dataManager.loadLinkedItemIdsByBaseId(conn=conn);
            self.commitUpdateBuffer(updateBuffer, linkedItemIdsByBaseId, conn=conn)
        else:
            bufferFilename = "%s.%s.json.gz" % (analysisOptions.bufferFile, iPatient);    # Modify filename with which patient done so far, in case saving several sequential results
            self.saveBufferToFile(bufferFilename, updateBuffer);
    
    def saveBufferToFile (self, filename, updateBuffer):
        ofs = stdOpen (filename, "w");
        updateBuffer["analyzedPatientItemIds"] = list(updateBuffer["analyzedPatientItemIds"]);
        json.dump(updateBuffer, ofs);
        ofs.close();

        # Wipe out buffer to reflect incremental changes done, so any new ones should be recorded fresh
        updateBuffer = self.makeUpdateBuffer(updateBuffer);

    def loadUpdateBufferFromFile(self, filename):
        updateBuffer = None;
        try:
            log.info("Loading: %s" % filename);
            ifs = stdOpen(filename, "r")
            updateBuffer = json.load(ifs)
            updateBuffer["analyzedPatientItemIds"] = set(updateBuffer["analyzedPatientItemIds"])
            ifs.close()
        except IOError, exc:
            # Apparently could not find the named filename. See if instead it's a prefix
            #    for a series of enumerated files and then merge them into one mass buffer
            dirname = os.path.dirname(filename);
            if dirname == "": dirname = ".";    # Implicitly the current working directory
            basename = os.path.basename(filename);
            for nextFilename in os.listdir(dirname):
                if nextFilename.startswith(basename):
                    nextFilepath = os.path.join(dirname, nextFilename);
                    nextUpdateBuffer = self.loadUpdateBufferFromFile(nextFilepath);
                    if updateBuffer is None:    # First update buffer, use it as base
                        updateBuffer = nextUpdateBuffer;
                    else:    # Have existing update buffer. Just update it's contents with the next one
                        updateBuffer = self.mergeBuffers(updateBuffer, nextUpdateBuffer);
                        del nextUpdateBuffer;	# Make sure memory gets reclaimed
                        
        return updateBuffer;

    def commitUpdateBufferFromFile(self, filename):
        conn = self.connFactory.connection();
        updateBuffer = self.loadUpdateBufferFromFile(filename);
        linkedItemIdsByBaseId = self.dataManager.loadLinkedItemIdsByBaseId(conn=conn);
        self.commitUpdateBuffer(updateBuffer,linkedItemIdsByBaseId, conn=conn);
    

    def commitUpdateBuffer(self, updateBuffer, linkedItemIdsByBaseId, conn=None):
        """Take data accumulated in updateBuffer from prior update methods and 
        commit them as incremental changes to the database.
        Clear buffer thereafter.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        try:
            if "incrementDataByItemIdPair" in updateBuffer:
                # Ensure baseline records exist to facilitate subsequent incremental update queries
                itemIdPairs = updateBuffer["incrementDataByItemIdPair"].keys();
                self.prepareItemAssociations(itemIdPairs, linkedItemIdsByBaseId, conn);

                # Construct incremental update queries based on each item pair's incremental counts/sums
                nItemPairs = len(itemIdPairs);
                log.debug("Primary increment updates for %d item pairs" % nItemPairs );
                incrementProg = ProgressDots(name="Increments");
                incrementProg.total = nItemPairs;
                cursor = conn.cursor();
                try:
                    for (itemIdPair, incrementData) in updateBuffer["incrementDataByItemIdPair"].iteritems():
                        query = ["UPDATE clinical_item_association SET"];
                        for col, increment in incrementData.iteritems():
                            query.append("%(col)s=%(col)s+%(increment)s" % {"col":col,"increment":increment});
                            query.append(",");
                        query.pop();    # Drop extra comma at end of list
                        query.append("WHERE clinical_item_id=%(p)s AND subsequent_item_id=%(p)s" % {"p":DBUtil.SQL_PLACEHOLDER} );
                        query = str.join(" ", query);
                        itemIdPair = eval(itemIdPair)
                        cursor.execute(query, itemIdPair);
                        incrementProg.update();
                    incrementProg.printStatus();
                finally:
                    cursor.close();

            if "analyzedPatientItemIds" in updateBuffer:
                # Record analysis date for the given patient items
                patientItemIdSet = updateBuffer["analyzedPatientItemIds"];
                nItems = len(patientItemIdSet);
                log.debug("Record %d analyzed items" % nItems );
                if nItems > 0:
                    paramList = [datetime.now()];
                    updateSize = 0;
                    for itemId in patientItemIdSet:
                        paramList.append(itemId);
                        updateSize += 1;
                    
                        if self.itemsPerUpdate is not None and updateSize > self.itemsPerUpdate:
                            # Update what we have so far to avoid excessive single mass query that may overwhelm database timeout
                            DBUtil.execute \
                            (   """update patient_item
                                set analyze_date = %(p)s
                                where patient_item_id in (%(pList)s)
                                and analyze_date is null
                                """ % {"p": DBUtil.SQL_PLACEHOLDER, "pList":generatePlaceholders(updateSize)},
                                tuple(paramList),
                                conn=conn
                            );
                            # Reset item list parameters
                            paramList = [datetime.now()];
                            updateSize = 0;
                    # Final Update
                    DBUtil.execute \
                    (   """update patient_item
                        set analyze_date = %(p)s
                        where patient_item_id in (%(pList)s)
                        and analyze_date is null
                        """ % {"p": DBUtil.SQL_PLACEHOLDER, "pList":generatePlaceholders(updateSize)},
                        tuple(paramList),
                        conn=conn
                    );

            # Flag that any cached association metrics will be out of date
            self.dataManager.clearCacheData("analyzedPatientCount");
            self.dataManager.clearCacheData("clinicalItemCountsUpdated");
            
            # Database commit
            conn.commit();
    
            # Wipe out buffer to reflect incremental changes done, so any new ones should be recorded fresh
            updateBuffer.clear();
            updateBuffer["nAssociations"] = 0;
        finally:
            if not extConn:
                conn.close();

    def prepareItemAssociations(self, itemIdPairs, linkedItemIdsByBaseId, conn):
        """Make sure all pair-wise item association records are ready / initialized
        so that subsequent queries don't have to pause to check for their existence.
        Should help greatly to reduce number of queries and execution time.
        """
        clinicalItemIdSet = set();
        #Do the below to convert the list of strings into a list of pairs, which is needed for the rest of this function
        for index, pair in enumerate(itemIdPairs):
            itemIdPairs[index]=eval(pair)

        for (itemId1, itemId2) in itemIdPairs:
            clinicalItemIdSet.add(itemId1);
            clinicalItemIdSet.add(itemId2);
        nItems = len(clinicalItemIdSet);
        
        # Now go through all needed item pairs and create default records as needed
        log.debug("Ensure %d baseline records ready" % (nItems*nItems) );
        for itemId1 in clinicalItemIdSet:
            # Query to see which ones already exist in the database
            # Do this for each source clinical item instead of all combinations to avoid excessive in memory tracking
            query = SQLQuery();
            query.addSelect("clinical_item_id");
            query.addSelect("subsequent_item_id");
            query.addFrom("clinical_item_association");
            query.addWhereEqual("clinical_item_id", itemId1 );
            query.addWhereIn("subsequent_item_id", clinicalItemIdSet );
            associationTable = DBUtil.execute( query, conn=conn );

            # Keep track in memory temporarily for rapid lookup
            existingItemIdPairs = set();
            for row in associationTable:
                existingItemIdPairs.add( tuple(row) );

            for itemId2 in clinicalItemIdSet:
                itemIdPair = (itemId1,itemId2);
                if itemIdPair not in existingItemIdPairs and self.acceptableClinicalItemIdPair(itemId1, itemId2, linkedItemIdsByBaseId):
                    defaultAssociation = RowItemModel( itemIdPair, ("clinical_item_id","subsequent_item_id") );
                    try:    # Optimistic insert of a new item pair, should be safe since just checked above, but parallel processes may collide
                        DBUtil.insertRow("clinical_item_association", defaultAssociation, conn=conn);
                    except IntegrityError, err:
                        log.warning(err);
                        pass;

    def acceptableClinicalItemPair(self, patientItem1, patientItem2, linkedItemIdsByBaseId ):
        """Verify is not a previously composite linked item pair, in which case no meaningful asssociation stats to calculate
        Also verify item dates occur in ordered non-negative relationship from item1 to item2
        """
        itemId1 = patientItem1["clinical_item_id"]
        itemId2 = patientItem2["clinical_item_id"]
        timeDelta = patientItem2["item_date"] - patientItem1["item_date"];
        timeDeltaSeconds = (timeDelta.days*SECONDS_PER_DAY) + timeDelta.seconds;

        isAcceptable = True;
        isAcceptable = isAcceptable and timeDeltaSeconds >= 0; # Only record forward / non-negative associations
        isAcceptable = isAcceptable and self.acceptableClinicalItemIdPair(itemId1, itemId2, linkedItemIdsByBaseId )
        return isAcceptable;
    
    def acceptableClinicalItemIdPair(self, itemId1, itemId2, linkedItemIdsByBaseId):
        isAcceptable = True;
        isAcceptable = isAcceptable and (itemId1 not in linkedItemIdsByBaseId or itemId2 not in linkedItemIdsByBaseId[itemId1]);
        isAcceptable = isAcceptable and (itemId2 not in linkedItemIdsByBaseId or itemId1 not in linkedItemIdsByBaseId[itemId2]);
        return isAcceptable;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <patientIds>\n"+\
                    "   <patientIds>    Comma-separated list of patient IDs to run the analysis on, or use option to specify a file. Leave blank and use bufferFile option if commiting a previously generated bufferFile to the database.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-i", "--idFile", dest="idFile", help="If provided, look for patient IDs in the named file, one ID per line.")
        parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run analysis on items occuring on or after this date.");
        parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run analysis on items occuring before this date.");
        parser.add_option("-p", "--patientsPerCommit", dest="patientsPerCommit", help="If provided, will commit incremental analysis results to the database after every p patients.  If not set, will just wait until full analysis to commit all (will keep more in memory, and will lose progress if script aborted during mid-execution).  Beware that large values are more efficient, but requires more runtime memory which can exceed memory limits.")
        parser.add_option("-a", "--associationsPerCommit", dest="associationsPerCommit", help="If provided, will commit incremental analysis results to the database when accrue this many association items.  Can help to avoid allowing accrual of too much buffered items whose runtime memory will exceed the 32bit 2GB program limit. 1M seems to just fit within 7.5GB memory (assuming 64-bit Python). Running batches of 3000 patients with ~3000 possible clinical items yields ~5M associations requiring ~25GB memory for learning then ~45GB memory to reload and commit a buffer file.")
        parser.add_option("-u", "--itemsPerUpdate", dest="itemsPerUpdate", help="If provided, when updating patient_item analyze_dates, will only update this many items at a time to avoid overloading MySQL query. (e.g., 10,000)")
        parser.add_option("-b", "--bufferFile", dest="bufferFile", help="If provided, send buffer to output file rather than commiting to database. If patientIds arguments and idFile parameter are blank, then instead read in bufferFile from this filename (prefix) and commit to database.")
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        analysisOptions = AnalysisOptions();

        analysisOptions.patientIds = list();
        if len(args) > 0:
            analysisOptions.patientIds.extend(args[0].split(","));
        if options.idFile is not None:
            idFile = stdOpen(options.idFile);
            for line in idFile:
                analysisOptions.patientIds.append(line.strip());

        if options.bufferFile is not None:
            analysisOptions.bufferFile = options.bufferFile

        if options.itemsPerUpdate is not None:
            self.itemsPerUpdate = int(options.itemsPerUpdate);

        if analysisOptions.bufferFile is not None and not analysisOptions.patientIds:
            # Have a previously generated result buffer file and not trying to train on any patientID subset.
            # Just commit buffer file directly to database
            self.commitUpdateBufferFromFile(analysisOptions.bufferFile);
        else:
            # Usual association analysis from scratch with option to commit direct to database or save to buffer file 
            analysisOptions.startDate = None;
            if options.startDate is not None:
                # Parse out the start date parameter
                timeTuple = time.strptime(options.startDate, DATE_FORMAT);
                analysisOptions.startDate = datetime(*timeTuple[0:3]);
            analysisOptions.endDate = None;
            if options.endDate is not None:
                # Parse out the end date parameter
                timeTuple = time.strptime(options.endDate, DATE_FORMAT);
                analysisOptions.endDate = datetime(*timeTuple[0:3]);

            if len(analysisOptions.patientIds) < 1 and analysisOptions.startDate is None and analysisOptions.endDate is None:
                # Disallow running without specifying some kind of filter
                parser.print_help();
                sys.exit(-1)
            
            if options.patientsPerCommit is not None:
                self.patientsPerCommit = int(options.patientsPerCommit);
            if options.associationsPerCommit is not None:
                self.associationsPerCommit = int(options.associationsPerCommit);

            self.analyzePatientItems(analysisOptions);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = AssociationAnalysis();
    instance.main(sys.argv);
