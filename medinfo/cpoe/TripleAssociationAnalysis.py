#!/usr/bin/env python
import sys, os
import time;
import math;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, generatePlaceholders;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;

from .AssociationAnalysis import AssociationAnalysis, AnalysisOptions;
from .DataManager import DataManager;

from .Const import DELTA_NAME_BY_SECONDS;

from .Util import log;

class TripleAssociationAnalysis(AssociationAnalysis):
    """Pre-Computation module to sort through data on patient clinical items
    (orders, lab results, problem list entries, etc.) and aggregate
    statistics on item associations, but in this case look only for specific
    triple sequences.
    Specify IDs for items of type B1 and B2, which will be linked to a virtual item B'
    (e.g., B1 = Admit Patient, B2 = Discharge Patient, B' = Re-Admission)
    Will increment association statistics for all items Ai leading to virtual item B',
    where B2 is used as the time point for B', and only count cases where the time sequence Ai->B1->B2 is observed.
    """
    connFactory = None; # Allow specification of alternative DB connection source

    def __init__(self):
        """Default constructor"""
        AssociationAnalysis.__init__(self);
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source
        self.dataManager = DataManager();

    def analyzePatientItems(self, patientIds, itemIdSequence, virtualItemId):
        """Primary run function to analyze patient clinical item data and
        record updated stats to the respective database tables.

        Does the analysis only for records pertaining to the given patient IDs
        (provides a way to limit the extent of analysis depending on params).

        Note that this does NOT record analyze_date timestamp on any records analyzed,
        as would collide with AssociationAnalysis primary timestamping, thus it is the
        caller's responsibility to be careful not to repeat this analysis redundantly
        and generating duplicated statistics.
        """
        progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            # Preload lookup data to facilitate rapid checks and filters later
            linkedItemIdsByBaseId = self.dataManager.loadLinkedItemIdsByBaseId(conn=conn);
            self.verifyVirtualItemLinked(itemIdSequence, virtualItemId, linkedItemIdsByBaseId, conn=conn);

            # Keep an in memory buffer of the updates to be done so can stall and submit them
            #   to the database in batch to minimize inefficient DB hits
            updateBuffer = dict();
            log.info("Main patient item query...")
            analysisOptions = AnalysisOptions();
            analysisOptions.patientIds = patientIds;
            for iPatient, patientItemList in enumerate(self.queryPatientItemsPerPatient(analysisOptions, progress=progress, conn=conn)):
                log.debug("Calculate associations for Patient %d's %d patient items" % (iPatient, len(patientItemList)) );
                self.updateItemAssociationsBuffer(itemIdSequence, virtualItemId, patientItemList, updateBuffer, linkedItemIdsByBaseId, progress=progress);
                # Periodically send a quick arbitrary query to DB, otherwise connection may get recycled because DB thinks timeout with no interaction
                DBUtil.execute("select 1+1", conn=conn);
            log.info("Final commit");
            self.commitUpdateBuffer(updateBuffer, linkedItemIdsByBaseId, conn=conn);  # Final update buffer commit
        finally:
            conn.close();
        # progress.PrintStatus();

    def updateItemAssociationsBuffer(self, itemIdSequence, virtualItemId, patientItemList, updateBuffer, linkedItemIdsByBaseId=None, progress=None):
        """Given a list of data on patient clinical items,
        ordered by item event date, increment information in the
        updateBuffer to inform subsequent updates to the clinical_item_association
        stats based on all item pairs observed.

        Looking for specific triple sequences only though with items followed by those specified
        in the itemIdSequence.  If a triple sequence is found, then mark the end point as
        a virtualItem instance for counting associations.
        """
        # Keep track of which items to mark as newly analyzed
        newlyAnalyzedPatientItemIdSet = set();

        # Keep track of which subsequent items have been analyzed, so we don't count further duplicates (just the first ones found)
        subsequentItemIds = set();
        # Keep track of all item pairs encountered to avoid counting patient level duplicates
        encounterIdPairsByItemIdPair = dict();

        # Track where the mid-sequence items occur for easy comparison later
        midSequenceItemDates = set();
        for patientItem in patientItemList:
            if patientItem["clinical_item_id"] == itemIdSequence[0]:
                midSequenceItemDates.add(patientItem["item_date"]);
        endSequenceItemsByPatientItemId = dict();

        # Main nested loop to look for associations
        for iItem1, patientItem1 in enumerate(patientItemList):
            subsequentItemIds.clear();

            for iItem2, patientItem2 in enumerate(patientItemList):
                itemIdPair = (patientItem1["clinical_item_id"], virtualItemId);
                encounterIdPair = (patientItem1["encounter_id"], patientItem2["encounter_id"]);

                # Verify is not a previously linked item pair, in which case no meaningful asssociation stats to calculate
                #   and that the item dates are in non-negative direction
                isPairToAnalyze = self.acceptableClinicalItemPair(patientItem1, patientItem2, linkedItemIdsByBaseId);
                if isPairToAnalyze and self.isTripleSequence(patientItem1, patientItem2, midSequenceItemDates, itemIdSequence):
                    # Record the stat update
                    isNewSubsequentItem = virtualItemId not in subsequentItemIds;   # Track repeats
                    isNewPair = itemIdPair not in encounterIdPairsByItemIdPair; # Pair ever seen for this patient
                    isNewPairWithinEncounter = (encounterIdPair[0]==encounterIdPair[-1]) and (isNewPair or encounterIdPair not in encounterIdPairsByItemIdPair[itemIdPair]);    # Pair ever seen for a common encounter combination

                    self.updateClinicalItemAssociationBuffer( patientItem1, patientItem2, isNewSubsequentItem, isNewPair, isNewPairWithinEncounter, updateBuffer, itemIdPair=itemIdPair );

                    subsequentItemIds.add(virtualItemId);
                    endSequenceItemsByPatientItemId[patientItem2["patient_item_id"]] = patientItem2;

                    if itemIdPair not in encounterIdPairsByItemIdPair:
                        encounterIdPairsByItemIdPair[itemIdPair] = set();
                    encounterIdPairsByItemIdPair[itemIdPair].add(encounterIdPair);

            # Update progress meter if available
            if progress is not None:
                progress.Update();

        # Separate pass to get virtual item baseline counts.  Cannot be done directly, since the virtual items do not actually exist in the raw data
        subsequentItemIds.clear();
        for iItem1, patientItem1 in enumerate(endSequenceItemsByPatientItemId.values()):
            for iItem2, patientItem2 in enumerate(endSequenceItemsByPatientItemId.values()):
                itemIdPair = (virtualItemId, virtualItemId);
                encounterIdPair = (patientItem1["encounter_id"], patientItem2["encounter_id"]);

                isNewSubsequentItem = virtualItemId not in subsequentItemIds;   # Track repeats
                isNewPair = itemIdPair not in encounterIdPairsByItemIdPair; # Pair ever seen for this patient
                isNewPairWithinEncounter = (encounterIdPair[0]==encounterIdPair[-1]) and (isNewPair or encounterIdPair not in encounterIdPairsByItemIdPair[itemIdPair]);

                self.updateClinicalItemAssociationBuffer( patientItem1, patientItem2, isNewSubsequentItem, isNewPair, isNewPairWithinEncounter, updateBuffer, itemIdPair=itemIdPair );

                subsequentItemIds.add(virtualItemId);
                if itemIdPair not in encounterIdPairsByItemIdPair:
                    encounterIdPairsByItemIdPair[itemIdPair] = set();
                encounterIdPairsByItemIdPair[itemIdPair].add(encounterIdPair);

    def verifyVirtualItemLinked(self, itemIdSequence, virtualItemId, linkedItemIdsByBaseId, conn=None):
        """Verify links exist from the virtualItemId to those in the itemIdSequence.
        If not, then create them in the database and in memory
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        try:
            if virtualItemId not in linkedItemIdsByBaseId:
                linkedItemIdsByBaseId[virtualItemId] = set();

            for componentId in itemIdSequence:
                if componentId not in linkedItemIdsByBaseId[virtualItemId]:
                    linkModel = RowItemModel();
                    linkModel["clinical_item_id"] = virtualItemId;
                    linkModel["linked_item_id"] = componentId;

                    insertQuery = DBUtil.buildInsertQuery("clinical_item_link", list(linkModel.keys()) );
                    insertParams= list(linkModel.values());
                    DBUtil.execute( insertQuery, insertParams, conn=conn);

                    linkedItemIdsByBaseId[virtualItemId].add(componentId);
        finally:
            if not extConn:
                conn.close();

    def isTripleSequence(self, patientItem1, patientItem2, midSequenceItemDates, itemIdSequence):
        """Assess whether the pair of items represents an acceptable triple sequence.
        Is so if end point matches the end of the itemIdSequence, and there exists a mid-sequence
        item in the intervening time, as previously tracked by the midSequenceItemDates.

        Assume previous check has already confirmed that the item pairs are not previously linked,
        and that there is a non-negative / forward direction in the relationship
        """
        itemId1 = patientItem1["clinical_item_id"]
        itemId2 = patientItem2["clinical_item_id"]

        isAcceptable = True;
        isAcceptable = isAcceptable and itemId2 == itemIdSequence[-1];

        foundMidSequenceDate = False;
        for midDate in midSequenceItemDates:
            if patientItem1["item_date"] <= midDate and midDate <= patientItem2["item_date"]:
                foundMidSequenceDate = True;
                break;  # Don't need to keep looking
        isAcceptable = isAcceptable and foundMidSequenceDate;
        return isAcceptable;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <patientIds>\n"+\
                    "   <patientIds>    Patient ID file, or comma-separated list of patient IDs.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-s", "--itemIdSequence", dest="itemIdSequence", help="Comma-separated sequence of item IDs to look for as representing the end of a triple of interest.")
        parser.add_option("-v", "--virtualItemId", dest="virtualItemId", help="ID of virtual clinical item to record against if find a specified triple.")
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        patientIds = set();
        patientIdsParam = args[0];
        try:
            # Try to open patient IDs as a file
            patientIdFile = stdOpen(patientIdsParam);
            patientIds.update( patientIdFile.read().split() );
        except IOError:
            # Unable to open as a filename, then interpret as simple comma-separated list
            patientIds.update(patientIdsParam.split(","));

        itemIdSequence = [int(idStr) for idStr in options.itemIdSequence.split(",")];
        virtualItemId = int(options.virtualItemId);

        self.analyzePatientItems(patientIds, itemIdSequence, virtualItemId);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = TripleAssociationAnalysis();
    instance.main(sys.argv);
