#!/usr/bin/env python
"""
Application / business logic and data management functions
for interactive clinical state simulations.
"""

import sys, os
import time;
from optparse import OptionParser
import math;
from datetime import datetime;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.DBUtil import DB_CONNECTOR_MODULE;
IntegrityError = DB_CONNECTOR_MODULE.IntegrityError;
from medinfo.db.Model import SQLQuery, RowItemModel, generatePlaceholders;
from medinfo.db.Model import modelListFromTable, modelDictFromList, columnFromModelList;
from medinfo.cpoe.Const import AD_HOC_SECTION;
from Const import DEFAULT_STATE_ID;

IntegrityError = DBUtil.DB_CONNECTOR_MODULE.IntegrityError;

class SimManager:
    connFactory = None;

    def __init__(self):
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

    def getSchemaFilepath(self):
        """Find the file path for the schema definition for for simulation data."""
        # For better platform independence, derive based on imported module location
        import medinfo.cpoe.cpoeSim;
        cpoeSimDir = os.path.dirname(medinfo.cpoe.cpoeSim.__file__);
        schemaFilepath = os.path.join(cpoeSimDir,"simdata/cpoeSim.sql");
        return schemaFilepath;

    def buildCPOESimSchema(self, conn=None):
        """Create the schema/table definitions needed for 
        Clinical Provider Order Entry (CPOE) case Simulation interface.
        Mostly for allowing (unit) testing purposes.
        For human testing, probably want to just use the SQL data dumps to get
        the schema and data files.
        """
        schemaFile = open(self.getSchemaFilepath());
        DBUtil.execute(schemaFile.read(), conn=conn, connFactory=self.connFactory);

    def createUser(self, userData, conn=None):
        """Create a new user record given the data dictionary
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            DBUtil.insertRow("sim_user", userData, conn=conn);
            conn.commit();
        finally:
            if not extConn:
                conn.close();
    
    def loadUserInfo(self, userIds=None, conn=None):
        """Load basic information about the specified users
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            query.addSelect("su.sim_user_id");
            query.addSelect("su.name");
            query.addFrom("sim_user as su");
            if userIds is not None:
                query.addWhereIn("su.sim_user_id", userIds );
            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            return dataModels;
        finally:
            if not extConn:
                conn.close();

    def createPatient(self, patientData, initialStateId, conn=None):
        """Create a new patient record given the data dictionary.
        Create a respective initial patient state record as well.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            DBUtil.insertRow("sim_patient", patientData, conn=conn);
            patientId = DBUtil.execute(DBUtil.identityQuery("sim_patient"),conn=conn)[0][0];
            patientStateData = {"sim_patient_id": patientId, "sim_state_id": initialStateId, "relative_time_start": 0};
            DBUtil.insertRow("sim_patient_state", patientStateData, conn=conn);
            
            conn.commit();  # Transactional commit for two step process
            return patientId;
        finally:
            if not extConn:
                conn.close();

    def copyPatientTemplate(self, patientData, templatePatientId, conn=None):
        """Create a new patient record based on the given template patient ID to copy from.
        Will copy shallow attributes, overridden by any provided in the given patientData,
        as well as any patient states, notes, or physician orders UP TO (and including)
        relative time zero, but not subsequent states, notes, or physician orders 
        (the latter is expected to reflect real user interaction records).
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            templatePatientData = DBUtil.loadRecordModelById("sim_patient", templatePatientId, conn=conn);
            del templatePatientData["sim_patient_id"];  # Remove prior ID to allow for new one
            templatePatientData.update( patientData );  # Override with new content (if exists)
            DBUtil.insertRow("sim_patient", templatePatientData, conn=conn);    # Create new patient record
            patientId = DBUtil.execute(DBUtil.identityQuery("sim_patient"),conn=conn)[0][0];

            # Copy initial template patient states
            query = SQLQuery();
            query.addSelect("*");   # Copy all columns
            query.addFrom("sim_patient_state as sps");
            query.addWhereEqual("sps.sim_patient_id", templatePatientId );
            query.addWhereOp("relative_time_start","<=", 0 );
            query.addOrderBy("relative_time_start");
            dataTable = DBUtil.execute(query,includeColumnNames=True,conn=conn);
            dataModels = modelListFromTable(dataTable);
            nStates = len(dataModels);
            for i, dataModel in enumerate(dataModels):
                del dataModel["sim_patient_state_id"];  # Discard copied ID to allow new one
                if i == nStates-1:
                    del dataModel["relative_time_end"]; # Last state. Blank out end time to reflect open ended for simulation
                dataModel["sim_patient_id"] = patientId;
                DBUtil.insertRow("sim_patient_state", dataModel, conn=conn);

            # Copy initial template orders
            query = SQLQuery();
            query.addSelect("*");
            query.addFrom("sim_patient_order as spo");
            query.addWhereEqual("sim_patient_id", templatePatientId );
            query.addWhereOp("relative_time_start","<=", 0 );
            query.addOrderBy("relative_time_start");
            dataTable = DBUtil.execute(query,includeColumnNames=True,conn=conn);
            dataModels = modelListFromTable(dataTable);
            for dataModel in dataModels:
                del dataModel["sim_patient_order_id"];
                dataModel["sim_patient_id"] = patientId;
                DBUtil.insertRow("sim_patient_order", dataModel, conn=conn);

            conn.commit();  # Transactional commit for multi-step process
            return patientId;
        finally:
            if not extConn:
                conn.close();

    def loadPatientInfo(self, patientIds=None, relativeTime=None, conn=None):
        """Load basic information about the specified patients.
        Report patient state at given time, or default to time zero
        """
        if relativeTime is None:
            relativeTime = 0;   # Just look for time zero default then

        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            query.addSelect("sp.sim_patient_id");
            query.addSelect("sp.name");
            query.addSelect("sp.age_years");
            query.addSelect("sp.gender");
            query.addSelect("s.sim_state_id");
            query.addSelect("s.name as state_name");
            query.addSelect("s.description as state_description");
            query.addSelect("sps.relative_time_start");
            query.addSelect("sps.relative_time_end");
            query.addFrom("sim_patient as sp");
            query.addFrom("sim_patient_state as sps");
            query.addFrom("sim_state as s");
            query.addWhere("sp.sim_patient_id = sps.sim_patient_id");
            query.addWhere("sps.sim_state_id = s.sim_state_id");
            if patientIds is not None:
                query.addWhereIn("sp.sim_patient_id", patientIds );
            
            # Look for the state that matches the given relative time offset
            query.addWhereOp("sps.relative_time_start","<=", relativeTime);
            query.openWhereOrClause();
            query.addWhere("sps.relative_time_end is null");
            query.addWhereOp("sps.relative_time_end",">", relativeTime);
            query.closeWhereOrClause();
            
            query.addOrderBy("sp.name");

            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            
            if len(dataModels) > 0:
                # Secondary query to build lookup table of possible state transition options from patient current states
                subQuery = SQLQuery();
                subQuery.addSelect("pre_state_id");
                subQuery.addSelect("post_state_id");
                subQuery.addSelect("clinical_item_id");
                subQuery.addSelect("time_trigger");
                subQuery.addFrom("sim_state_transition as sst");
                subQuery.addWhereIn("pre_state_id", columnFromModelList(dataModels,"sim_state_id"));
                subResults = DBUtil.execute(subQuery,conn=conn);
                
                # For each pre-state, track which clinical items or times trigger which post-states
                postStateIdByItemIdByPreStateId = dict();
                postStateIdTimeTriggerByPreStateId = dict();
                for preStateId, postStateId, itemId, timeTrigger in subResults:
                    if preStateId not in postStateIdByItemIdByPreStateId:
                        postStateIdByItemIdByPreStateId[preStateId] = dict();
                    postStateIdByItemIdByPreStateId[preStateId][itemId] = postStateId;
                    
                    if timeTrigger is not None:
                        postStateIdTimeTriggerByPreStateId[preStateId] = (postStateId, timeTrigger);
            
                
                # Record in patient result models for retrieval
                for i, dataModel in enumerate(dataModels):
                    patientId = dataModel["sim_patient_id"];
                    stateId = dataModel["sim_state_id"];
                    
                    dataModel["postStateIdByItemId"] = dict();
                    if stateId in postStateIdByItemIdByPreStateId:
                        dataModel["postStateIdByItemId"] = postStateIdByItemIdByPreStateId[stateId];
                    dataModel["postStateIdTimeTriggerByPreStateId"] = dict();
                    if stateId in postStateIdTimeTriggerByPreStateId:
                        dataModel["postStateIdTimeTrigger"] = postStateIdTimeTriggerByPreStateId[stateId];
                    
                    if dataModel["relative_time_end"] is None and "postStateIdTimeTrigger" in dataModel:
                        # Check that we haven't passed (and should thus trigger) a time-based state transition
                        (postStateId, timeTrigger) = dataModel["postStateIdTimeTrigger"];
                        preStateTime = dataModel["relative_time_start"];
                        postStateTriggerTime = (preStateTime + timeTrigger);
                        
                        if postStateTriggerTime <= relativeTime:    # Trigger state transition just by time elapsed
                            #print >> sys.stderr, relativeTime, preStateTime, stateId, postStateTriggerTime, postStateId
                            self.recordStateTransition(patientId, stateId, postStateId, postStateTriggerTime, conn=conn);
                            # State change which can yield new triggers, so recursively reload.
                            # Small risk of infinite recusion if timeTriggers are zero. Otherwise, should converge as each recursion will update the preState relativeTimeStart
                            dataModels[i] = self.loadPatientInfo([patientId], relativeTime, conn=conn)[0];
            
            return dataModels;
        finally:
            if not extConn:
                conn.close();

    def loadStateInfo(self, stateIds=None, conn=None):
        """Load basic information about the specified patient states
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            query.addSelect("ss.sim_state_id");
            query.addSelect("ss.name");
            query.addSelect("ss.description");
            query.addFrom("sim_state as ss");
            if stateIds is not None:
                query.addWhereIn("ss.sim_state_id", stateIds );
            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            return dataModels;
        finally:
            if not extConn:
                conn.close();

    def signOrders(self, userId, patientId, currentTime, orderItemIds, discontinuePatientOrderIds=None, conn=None):
        """Commit new order item IDs for the given patient and starting now,
        and discontinue (set end date) for any existing orders specified.
        
        Record any patient state transitions the orders would trigger
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Denormalized recording of current patient state to facilitate easy retrieval linked to orders later
            patientInfo = self.loadPatientInfo( [patientId], currentTime, conn=conn)[0];
            stateId = patientInfo["sim_state_id"];
            postStateIdByItemId = patientInfo["postStateIdByItemId"];
            
            orderItemIdSet = set(orderItemIds); # Ensure unique and facilitate set operations
            
            insertDict = {"sim_user_id": userId, "sim_patient_id": patientId, "sim_state_id": stateId, "relative_time_start": currentTime};
            for itemId in orderItemIdSet:
                insertDict["clinical_item_id"] = itemId;
                DBUtil.insertRow("sim_patient_order", insertDict, conn=conn);

            # See if any of these new orders triggered state transitions
            triggerItemIds = postStateIdByItemId.viewkeys() & orderItemIdSet;
            while triggerItemIds:   # Found a trigger item
                triggerItemId = None;
                if len(triggerItemIds) > 1: # Found multiple. Weird. Arbitrarily act on the one that appeared first in the input list
                    for itemId in orderItemIds:
                        if itemId in triggerItemIds:
                            triggerItemId = itemId;
                            break;
                else:
                    triggerItemId = triggerItemIds.pop();
                postStateId = postStateIdByItemId[triggerItemId];
                
                # Record the state transition
                self.recordStateTransition(patientId, stateId, postStateId, currentTime, conn=conn);
                
                # Reload patientInfo to reflect new patient state
                patientInfo = self.loadPatientInfo( [patientId], currentTime, conn=conn)[0];
                stateId = patientInfo["sim_state_id"];
                postStateIdByItemId = patientInfo["postStateIdByItemId"];
                
                orderItemIdSet.discard(triggerItemId);  # Don't keep looking for this one, important to avoid infinite loop
                triggerItemIds = postStateIdByItemId.viewkeys() & orderItemIdSet;
                
        
            if discontinuePatientOrderIds is not None:
                updateDict = {"relative_time_end": currentTime };
                for patientOrderId in discontinuePatientOrderIds:
                    DBUtil.updateRow("sim_patient_order", updateDict, patientOrderId, conn=conn);
        finally:
            conn.commit();
            if not extConn:
                conn.close();

    def recordStateTransition(self, patientId, preStateId, postStateId, currentTime, conn=None):
        """Record a patient state transition
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Ending of pre-state
            updateQuery = \
                """update sim_patient_state 
                set relative_time_end = %(p)s
                where sim_patient_id = %(p)s
                and sim_state_id = %(p)s
                and relative_time_start <= %(p)s
                and relative_time_end is null
                """ % {"p": DBUtil.SQL_PLACEHOLDER};
            updateParams = (currentTime, patientId, preStateId, currentTime);
            DBUtil.execute(updateQuery, updateParams, conn=conn);
            
            # Beginning of post-state
            insertDict = {"sim_patient_id": patientId, "sim_state_id": postStateId, "relative_time_start": currentTime};
            DBUtil.insertRow("sim_patient_state", insertDict, conn=conn);
        finally:
            conn.commit();
            if not extConn:
                conn.close();
    
    def loadPatientOrders(self, patientId, currentTime, loadActive=True, conn=None):
        """Load orders for the given patient that exist by the specified current time point.
        loadActive - Specify whether to load active vs. inactive/completed orders.  Set to None to load both
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            query.addSelect("po.sim_patient_order_id");
            query.addSelect("po.sim_user_id");
            query.addSelect("po.sim_patient_id");
            query.addSelect("po.sim_state_id");
            query.addSelect("po.clinical_item_id");
            query.addSelect("po.relative_time_start");
            query.addSelect("po.relative_time_end");
            query.addSelect("ci.name");
            query.addSelect("ci.description");
            query.addSelect("cic.source_table");
            query.addSelect("cic.description as category_description");
            query.addFrom("sim_patient_order as po");
            query.addFrom("clinical_item as ci");
            query.addFrom("clinical_item_category as cic");
            query.addWhere("po.clinical_item_id = ci.clinical_item_id");
            query.addWhere("ci.clinical_item_category_id = cic.clinical_item_category_id");
            query.addWhereEqual("sim_patient_id", patientId );
            query.addWhereOp("relative_time_start","<=", currentTime );

            
            if loadActive:  # Filter out inactive orders here.
                query.openWhereOrClause();
                query.addWhereOp("relative_time_end",">", currentTime);
                query.addWhere("relative_time_end is null");
                query.closeWhereOrClause();
            #elif loadActive is not None:    # Filter out active orders here.
            #    query.addWhereOp("relative_time_end","<=", currentTime);
            
            if loadActive:  # Organize currently active orders by category
                query.addOrderBy("cic.description");
                query.addOrderBy("ci.description");
            else:   # Otherwise chronologic order
                query.addOrderBy("relative_time_start");

            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            return dataModels;
        finally:
            if not extConn:
                conn.close();

    def loadResults(self, patientId, relativeTime, conn=None):
        """Load all results active by the given relativeTime.
        Will look for sim_patient_state times and sim_patient_order for diagnostic orders,
        to extrapolate all state-specific results for each order, or using default values
        if no state specific ones available.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # First query for all expected result labels and states, without state-specific values as 
            #   may want outer join behvaior against default state values
            query = SQLQuery();
            
            query.addSelect("distinct spo.sim_state_id");
            query.addSelect("sr.sim_result_id");
            query.addSelect("sr.name");
            query.addSelect("sr.description");
            query.addSelect("sr.priority");
            query.addSelect("sr.group_string");

            query.addSelect("spo.relative_time_start");
            query.addSelect("sorm.turnaround_time");
            query.addSelect("(spo.relative_time_start + sorm.turnaround_time) as result_relative_time")
            
            query.addFrom("sim_patient_order as spo");
            query.addFrom("sim_order_result_map as sorm");
            query.addFrom("sim_result as sr");
            
            query.addWhere("spo.clinical_item_id = sorm.clinical_item_id");
            query.addWhere("sorm.sim_result_id = sr.sim_result_id");

            query.addWhereEqual("spo.sim_patient_id", patientId );
            # Only unlock results if appropiate prereq orders were placed in the past (and longer than the turnaround time)
            query.addWhereOp("spo.relative_time_start + sorm.turnaround_time","<=", relativeTime );  

            query.addOrderBy("result_relative_time");
            query.addOrderBy("sr.priority");
            
            resultTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            resultModels = modelListFromTable(resultTable);

            # Pass through results to get set of states to search for
            stateIds = set([DEFAULT_STATE_ID]); # Include default state to fall back on
            for resultModel in resultModels:
                stateIds.add(resultModel["sim_state_id"]);
            
            # Second query for state-specific values
            valueQuery = SQLQuery();
            valueQuery.addSelect("ssr.sim_state_id");
            valueQuery.addSelect("ssr.sim_result_id");
            valueQuery.addSelect("ssr.num_value");
            valueQuery.addSelect("ssr.num_value_noise");
            valueQuery.addSelect("ssr.text_value");
            valueQuery.addSelect("ssr.result_flag");
            valueQuery.addSelect("ssr.clinical_item_id");    # Output clinical item if result flag means something
            valueQuery.addFrom("sim_state_result as ssr");
            valueQuery.addWhereIn("ssr.sim_state_id", stateIds);
            valueTable = DBUtil.execute( valueQuery, includeColumnNames=True, conn=conn);
            valueModels = modelListFromTable(valueTable);
            
            # Store in-memory dictionary for rapid cross-referencing "join" to result table
            valueModelByStateIdByResultId = dict();
            for valueModel in valueModels:
                resultId = valueModel["sim_result_id"];
                stateId = valueModel["sim_state_id"];
                if resultId not in valueModelByStateIdByResultId:
                    valueModelByStateIdByResultId[resultId] = dict();
                valueModelByStateIdByResultId[resultId][stateId] = valueModel;

            # Now go back through original results and join up state-specific values, or use default values if needed
            resultValueModels = list();
            for resultModel in resultModels:
                resultId = resultModel["sim_result_id"];
                stateId = resultModel["sim_state_id"];
                if resultId in valueModelByStateIdByResultId:
                    valueModelByStateId = valueModelByStateIdByResultId[resultId];
                    if stateId in valueModelByStateId:
                        # Have a state-specific value, populate that
                        valueModel = valueModelByStateId[stateId];
                        resultModel.update(valueModel);
                    elif DEFAULT_STATE_ID in valueModelByStateId:
                        # No state-specific value, but have a default one to populate instead
                        valueModel = valueModelByStateId[DEFAULT_STATE_ID];
                        resultModel.update(valueModel);
                    resultValueModels.append(resultModel);
                else:
                    # No result information available, even in default state. Skip these
                    #resultModel["num_value"] = None;
                    #resultModel["num_value_noise"] = None;
                    #resultModel["text_value"] = None;
                    #resultModel["result_flag"] = None;
                    #resultModel["clinical_item_id"] = None;
                    pass;

            return resultValueModels;
        finally:
            if not extConn:
                conn.close();

    def loadNotes(self, patientId, currentTime, conn=None):
        """Load notes committed up to the given simulation time.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            
            query.addSelect("sn.sim_note_id");
            query.addSelect("sps.sim_patient_id"); # Link
            query.addSelect("sn.sim_state_id");
            query.addSelect("sn.note_type_id");
            query.addSelect("sn.author_type_id");
            query.addSelect("sn.service_type_id");
            query.addSelect("(sps.relative_time_start + sn.relative_state_time) as relative_time");
            query.addSelect("sn.content");
            
            query.addFrom("sim_note as sn");
            query.addFrom("sim_patient_state as sps");
            
            query.addWhere("sn.sim_state_id = sps.sim_state_id");
            query.addWhereEqual("sps.sim_patient_id", patientId );
            # Only unlock notes once traverse expected time
            query.addWhereOp("(sps.relative_time_start + sn.relative_state_time)","<=", currentTime );  
            query.addOrderBy("(sps.relative_time_start + sn.relative_state_time)");
            
            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            return dataModels;
        finally:
            if not extConn:
                conn.close();


    def recentItemIds(self, patientId, currentTime, timeDelta=None, conn=None):
        """Load a list of clinicalItemIds
        (orders, diagnoses, unlocked results, etc.)
        to establish current patient context.
        
        If timeDelta specified, only count items that occurred within that much past time from the current simTime
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            itemIds = set();
            
            patientOrders = self.loadPatientOrders(patientId, currentTime, loadActive=True, conn=conn);
            for patientOrder in patientOrders:
                itemIds.add(patientOrder["clinical_item_id"]);
            
            results = self.loadResults(patientId, currentTime, conn=conn);
            for result in results:
                if result["clinical_item_id"] is not None:
                    itemIds.add(result["clinical_item_id"]);
            
            return itemIds;
        finally:
            if not extConn:
                conn.close();

    def clinicalItemSearch(self, itemQuery, conn=None):
        """Look for clinical items based on specified query criteria"""
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            query.addSelect("ci.clinical_item_id");
            query.addSelect("ci.name");
            query.addSelect("ci.description");
            query.addSelect("cic.source_table");
            query.addSelect("cic.description as category_description");
            query.addFrom("clinical_item as ci");
            query.addFrom("clinical_item_category as cic");
            query.addWhere("ci.clinical_item_category_id = cic.clinical_item_category_id");
            if itemQuery.searchStr is not None:
                searchWords = itemQuery.searchStr.split();
                #query.openWhereOrClause();
                for searchField in ("ci.description",):
                    for searchWord in searchWords:
                        query.addWhereOp(searchField,"~*","^%(searchWord)s|[^a-z]%(searchWord)s" % {"searchWord": searchWord} ); # Prefix search by regular expression
                #query.closeWhereOrClause();
            if itemQuery.sourceTables:
                query.addWhereIn("cic.source_table", itemQuery.sourceTables );
            if itemQuery.analysisStatus is not None:
                query.addWhereEqual("ci.analysis_status", itemQuery.analysisStatus );
                query.addWhere("ci.item_count <> 0");    # Also ignore items with no occurence in the analyzed data (occurs if item was accepted for analysis from multi-year dataset, but never used in a sub-time frame's analysis)

            if itemQuery.sortField:
                query.addOrderBy(itemQuery.sortField);
            query.addOrderBy("cic.description");
            query.addOrderBy("ci.name");
            query.addOrderBy("ci.description");
            if itemQuery.resultCount is not None:
                query.limit = itemQuery.resultCount;
            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            return dataModels;
        finally:
            if not extConn:
                conn.close();


    def orderSetSearch(self, itemQuery, conn=None):
        """Look for clinical items based on specified query criteria"""
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = SQLQuery();
            query.addSelect("ic.item_collection_id");
            query.addSelect("ic.external_id");
            query.addSelect("ic.name as collection_name");
            query.addSelect("ic.section");
            query.addSelect("ic.subgroup");
            query.addSelect("ci.clinical_item_category_id");
            query.addSelect("ci.clinical_item_id");
            query.addSelect("ci.name");
            query.addSelect("ci.description");
            query.addFrom("item_collection as ic");
            query.addFrom("item_collection_item as ici");
            query.addFrom("clinical_item as ci");
            query.addWhere("ic.item_collection_id = ici.item_collection_id");
            query.addWhere("ici.clinical_item_id = ci.clinical_item_id");
            query.addWhereNotEqual("ic.section", AD_HOC_SECTION );
            if itemQuery.searchStr is not None:
                searchWords = itemQuery.searchStr.split();
                for searchWord in searchWords:
                    query.addWhereOp("ic.name","~*","^%(searchWord)s|[^a-z]%(searchWord)s" % {"searchWord": searchWord} ); # Prefix search by regular expression
            if itemQuery.analysisStatus is not None:
                query.addWhereEqual("ci.analysis_status", itemQuery.analysisStatus );
            query.addOrderBy("lower(ic.name)");
            query.addOrderBy("ic.external_id");
            query.addOrderBy("lower(ic.section)");
            query.addOrderBy("lower(ic.subgroup)");
            query.addOrderBy("ci.clinical_item_id");
            query.addOrderBy("ci.name");
            dataTable = DBUtil.execute( query, includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);

            # Aggregate up into order sets
            orderSetModel = None;
            for row in dataModels:
                if orderSetModel is None or row["external_id"] != orderSetModel["external_id"]:
                    if orderSetModel is not None:
                        # Prior order set exists, yield/return it before preparing next one
                        yield orderSetModel;
                    orderSetModel = \
                        {   "external_id": row["external_id"], 
                            "name": row["collection_name"],
                            "itemList": list(),
                        };
                orderSetModel["itemList"].append(row);
            yield orderSetModel;    # Yield the last processed model
        finally:
            if not extConn:
                conn.close();


class ClinicalItemQuery:
    """Struct to capture query elements for clinical item / order instances"""
    def __init__(self):
        self.searchStr = None;
        self.analysisStatus = None;
        self.sourceTables = None;   # Valid source data tables to use
        self.resultCount = None;
        self.sortField = None;

    def parseParams(self, paramDict):
        """Look through the dictionary for key-value pairs that can be parsed into query object parameters.
        Facilitates easy setup from web or command-line text interfaces.
        """
        if "searchStr" in paramDict:
            self.searchStr = paramDict["searchStr"];
        if "analysisStatus" in paramDict:
            self.analysisStatus = paramDict["analysisStatus"];
        if "sourceTables" in paramDict:
            self.sourceTables = paramDict["sourceTables"].split(",");
        if "resultCount" in paramDict:
            self.resultCount = int(paramDict["resultCount"]);
        if "sortField" in paramDict:
            self.sortField = paramDict["sortField"];
        
if __name__ == "__main__":
    instance = SimManager();
    instance.main(sys.argv);
