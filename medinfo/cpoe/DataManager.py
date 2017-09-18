#!/usr/bin/env python
"""
Support module to manage data and statistics
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
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from Util import log;

IntegrityError = DBUtil.DB_CONNECTOR_MODULE.IntegrityError;

class DataManager:
    connFactory = None;
    maxClinicalItemId = None;

    def __init__(self):
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source
        self.maxClinicalItemId = None;  # Can set to a value to limit what items will be processed.  Particularly for setting to 0, so will only work on negative values, generally only test cases, while leaving "real" data alone
        self.dataCache = dict();  # If set, use as in memory data cache.  Set to None to avoid usage if having memory leak problems with persistent processes
        self.queryCount = 0;

    def resetAssociationModel(self, conn=None):
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            log.debug("Connected to database for reseting purposes");
            result = DBUtil.execute("DELETE FROM clinical_item_association;", conn=conn);
            log.debug("Training table cleared items: %s" % result);

            # Droppings constraints can greatly speed up the next step of updating analyze dates
            #curs.execute("ALTER TABLE backup_link_patient_item drop constraint backup_link_patient_item_patient_item_fkey;")
            #curs.execute("ALTER TABLE patient_item_collection_link drop constraint patient_item_collection_link_patient_fkey;")
            #curs.execute("ALTER TABLE patient_item drop constraint patient_item_pkey;")
            #curs.execute("ALTER TABLE patient_item drop constraint patient_item_clinical_item_fkey;")
            #curs.execute("drop index index_patient_item_clinical_item_id_date;")
            #curs.execute("drop index index_patient_item_patient_id_date;")
            #curs.execute("drop index index_patient_item_external_id;")
            #curs.execute("drop index index_patient_item_encounter_id_date;")
            #curs.execute("ALTER TABLE patient_item drop constraint patient_item_composite;")
            
            result = DBUtil.execute("UPDATE patient_item SET analyze_date = NULL where analyze_date is not NULL;", conn=conn);
            log.debug("Analyze_date set to NULL: %s" % result);
            
            # Add  back constraints
            #curs.execute("ALTER TABLE patient_item ADD CONSTRAINT patient_item_pkey PRIMARY KEY (patient_item_id);")
            #curs.execute("ALTER TABLE patient_item ADD CONSTRAINT patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);")
            #curs.execute("CREATE INDEX index_patient_item_clinical_item_id_date ON patient_item(clinical_item_id, item_date);")
            #curs.execute("CREATE INDEX index_patient_item_patient_id_date ON patient_item(patient_id, item_date);")
            #curs.execute("CREATE INDEX index_patient_item_external_id ON patient_item(external_id, clinical_item_id);")
            #curs.execute("CREATE INDEX index_patient_item_encounter_id_date ON patient_item(encounter_id, item_date);")
            #curs.execute("ALTER TABLE patient_item ADD CONSTRAINT patient_item_composite UNIQUE (patient_id, clinical_item_id, item_date);")
            #curs.execute("ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_patient_item_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id);")
            #curs.execute("ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_patient_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id);")

            # Flag that any cached association metrics will be out of date
            self.clearCacheData("analyzedPatientCount",conn=conn);

            # Reset clinical_item denormalized counts
            self.updateClinicalItemCounts(conn=conn);

            conn.commit();
            log.debug("Connection committed");
        finally:
            if not extConn:
                conn.close();


    def updateClinicalItemCounts(self, acceptCache=False, conn=None):
        """Update the summary item_counts for clinical_items based
        on clinical_item_association summary counts.
        
        If acceptCache is True, then will first check for existence of an entry "clinicalItemCountsUpdated"
            in the data_cache table.  If it exists, assume we have done this update already, and no need to force the calculations again
        """

        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            if acceptCache:
                isCacheUpdated = (self.getCacheData("clinicalItemCountsUpdated",conn=conn) is not None);
                if isCacheUpdated:
                    # Item count caches already updated, no need to recalculate them
                    return;

            # First reset all counts to zero
            query = "update clinical_item set item_count = 0, patient_count = 0, encounter_count = 0 ";
            params = [];
            if self.maxClinicalItemId is not None:  # Restrict to (test) data
                query += "where clinical_item_id < %s" % DBUtil.SQL_PLACEHOLDER;
                params.append(self.maxClinicalItemId);
            DBUtil.execute(query, params, conn=conn);
        
            sqlQuery = SQLQuery();
            sqlQuery.addSelect("clinical_item_id");
            sqlQuery.addSelect("count_0 as item_count");
            sqlQuery.addSelect("patient_count_0 as patient_count");
            sqlQuery.addSelect("encounter_count_0 as encounter_count");
            sqlQuery.addFrom("clinical_item_association as ci");
            sqlQuery.addWhere("clinical_item_id = subsequent_item_id"); # Look along "diagonal" of matrix for primary summary stats
            if self.maxClinicalItemId is not None:  # Restrict to (test) data
                sqlQuery.addWhereOp("clinical_item_id","<", self.maxClinicalItemId );

            resultTable = DBUtil.execute( sqlQuery, includeColumnNames=True, conn=conn );
            resultModels = modelListFromTable( resultTable );
            
            for result in resultModels:
                DBUtil.updateRow("clinical_item", result, result["clinical_item_id"], conn=conn);

            # Make a note that this cache data has been updated
            self.setCacheData("clinicalItemCountsUpdated", "True", conn=conn);
        finally:
            if not extConn:
                conn.close();


    def loadClinicalItemBaseCountByItemId(self, countPrefix=None, acceptCache=True, conn=None):
        """Helper query to get the baseline analyzed item counts for all of the clinical items
        If countPrefix is provided, can use alternative total item counts instead of the default item_count,
        such as patient_count or encounter_count to match the respective association query baselines used.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # First ensure the denormalized count data is updated
            self.updateClinicalItemCounts(acceptCache=acceptCache, conn=conn);

            if countPrefix is None or countPrefix == "":
                countPrefix = "item_";  # Default to general item counts, allowing for repeats per patient
            
            baseCountQuery = SQLQuery();
            baseCountQuery.addSelect("clinical_item_id");
            baseCountQuery.addSelect("%scount" % countPrefix); 
            baseCountQuery.addFrom("clinical_item");
            if acceptCache:
                baseCountResultTable = self.executeCacheOption( baseCountQuery, conn=conn );
            else:
                baseCountResultTable = DBUtil.execute( baseCountQuery, conn=conn );
            
            baseCountByItemId = dict();
            for (itemId, baseCount) in baseCountResultTable:
                baseCountByItemId[itemId] = baseCount;
            return baseCountByItemId;

        finally:
            if not extConn:
                conn.close();


    def deactivateAnalysis(self, clinicalItemIds, conn=None):
        """The specified clinical_items will be removed from association analysis.  
        This includes 
        - Changing analysis_status to 0, 
        - Clearing the analyze_date on any patient_items
        - Removing all related clinical_item_association records
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            placeholders = generatePlaceholders(len(clinicalItemIds))

            # Change analysis status
            DBUtil.execute("update clinical_item set analysis_status = 0 where clinical_item_id in (%s)" % placeholders, tuple(clinicalItemIds), conn=conn );
            # Retroactively remove any prior analysis records
            DBUtil.execute("delete from clinical_item_association where clinical_item_id in (%s)" % placeholders, tuple(clinicalItemIds), conn=conn );
            DBUtil.execute("delete from clinical_item_association where subsequent_item_id in (%s)" % placeholders, tuple(clinicalItemIds), conn=conn );
            # Retroactively clear any prior analyze_date recordings since effectively undoing that work that may be redone later
            DBUtil.execute("update patient_item set analyze_date = null where clinical_item_id in (%s)" % placeholders, tuple(clinicalItemIds), conn=conn );
        finally:
            if not extConn:
                conn.close();
    
    def deactivateAnalysisByCount(self, thresholdInstanceCount, categoryIds=None, conn=None):
        """Find clinical items to deactivate, based on their instance (patient_item) counts
        being too low to be interesting.  Can restrict to applying to only items under certain categories.
        
        Use data/analysis/queryItemCounts.py to help guide selections with queries like:
        
            select count(clinical_item_id), sum(item_count) 
            from clinical_item 
            where item_count > %s 
            and clinical_item_category_id in (%s)
            
            (and analysis_status = 1)?  Seems like good filter, but the process itself will change this count

        Direct search option as below, but that's usually for pre-processing before activations even start.
        Former meant to count records that have already gone through analysis.

            select clinical_item_id, count(distinct patient_id), count(distinct encounter_id), count(patient_item_id)
            from patient_item 
            group by clinical_item_id

        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Make sure clinical item instance (patient item) counts are up to date
            self.updateClinicalItemCounts(conn=conn);
            query = SQLQuery();
            query.addSelect("clinical_item_id");
            query.addFrom("clinical_item");
            if self.maxClinicalItemId is not None:  # Restrict to limited / test data
                query.addWhereOp("clinical_item_id","<", self.maxClinicalItemId );
            if categoryIds is not None:
                query.addWhereIn("clinical_item_category_id", categoryIds );
            query.addWhereOp("item_count","<=", thresholdInstanceCount);
            results = DBUtil.execute(query, conn=conn);
            
            clinicalItemIds = set();
            for row in results:
                clinicalItemIds.add(row[0]);
                
            self.deactivateAnalysis(clinicalItemIds, conn=conn);
        finally:
            if not extConn:
                conn.close();
        
    def compositeRelated(self, clinicalItemIds, itemName, itemDescription, categoryId, compositeId=None, conn=None):
        """A new clinical item will be created, with patient item records created to match every one currently 
        matching one of the specified clinical items.  
        Parameters specify new composite item name/code, description, and clinical item category to be created under.  
        Option to explicitly specify the composite clinical item Id value rather than taking a sequence number value (convenient for test cases)
        Returns ID of newly created item
        
        Depending on context, may wish to deactivateAnalysis of component items once this composite one is created
        if they are no longer of interest.
        Newly created composite item's default_recommend attribute will be reset to 0 since it presumably does not represent a 
        discrete order item.
        
        Linking records will be created in clinical_item_link between the composite and and component clinical items
        so that these relationships can be reconstructed
                
        Examples this could be relevant for:
        ICUVasopressors to include all vasopressor infusions (dopamine, norepinephrine, epinephrine, vasopressin, etc.)
        All blood transfusion indexes, G vs J vs Feeding tube equivalent, Ear, Eyes med routes irrelevant which ear/eye.
        Eventually lump together medication classes (e.g., any "PPI" same difference as choosing pantoprazole or omeprazole.
        Eventually lump together diagnosis codes by major prefix to reduce granularity and improve general signal.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Build new composite item
            compositeItem = RowItemModel();
            compositeItem["name"] = itemName;
            compositeItem["description"] = itemDescription;
            compositeItem["clinical_item_category_id"] = categoryId;
            compositeItem["default_recommend"] = 0;
            if compositeId is not None:
                compositeItem["clinical_item_id"] = compositeId;
            
            insertQuery = DBUtil.buildInsertQuery("clinical_item", compositeItem.keys() );
            insertParams= compositeItem.values();
            DBUtil.execute( insertQuery, insertParams, conn=conn);
            if compositeId is None:
                compositeId = DBUtil.execute( DBUtil.identityQuery("clinical_item"), conn=conn )[0][0];   # Retrieve the just inserted item's ID

            self.generatePatientItemsForCompositeId(clinicalItemIds, compositeId, conn=conn);
            return compositeId;
        finally:
            if not extConn:
                conn.close();

    def generatePatientItemsForCompositeId(self, clinicalItemIds, compositeId, conn=None):
        """Create patient_item records for the composite to match the given clinical item ID patient items.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Record linking information
            for componentId in clinicalItemIds:
                linkModel = RowItemModel();
                linkModel["clinical_item_id"] = compositeId;
                linkModel["linked_item_id"] = componentId;
                
                insertQuery = DBUtil.buildInsertQuery("clinical_item_link", linkModel.keys() );
                insertParams= linkModel.values();
                DBUtil.execute(insertQuery, insertParams, conn=conn);

            # Extract back link information, which will also flatten out any potential inherited links
            linkedItemIdsByBaseId = self.loadLinkedItemIdsByBaseId(conn=conn);
            linkedItemIds = linkedItemIdsByBaseId[compositeId];

            # Create patienItem records for the composite clinical item to overlap existing component ones
            # First query for the existing component records
            query = SQLQuery();
            query.addSelect("*");
            query.addFrom("patient_item");
            query.addWhereIn("clinical_item_id", linkedItemIds);
            results = DBUtil.execute(query, includeColumnNames=True, conn=conn);
            patientItems = modelListFromTable(results);
            
            # Patch component records to instead become composite item records then insert back into database
            progress = ProgressDots(total=len(patientItems));
            for patientItem in patientItems:
                del patientItem["patient_item_id"];
                patientItem["clinical_item_id"] = compositeId;
                patientItem["analyze_date"] = None;
                
                insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys() );
                insertParams= patientItem.values();
                
                try:
                    # Optimistic insert of a new unique item
                    DBUtil.execute( insertQuery, insertParams, conn=conn );
                except IntegrityError, err:
                    # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
                    log.info(err);
                progress.Update();

            progress.PrintStatus();
        finally:
            if not extConn:
                conn.close();
        
    def mergeRelated(self, baseClinicalItemId, clinicalItemIds, reassignMergedItems=True, conn=None):
        """The specified clinical items will be merged / composited into the base clinical item provided.  
        The remaining now redundant items will be deactivated
        Patient_item instances will be reassigned to the merged clinical_item 
        (while backup links will be saved to backup_link_patient_item), 
        clinical_item_association counts for the redundant items will removed and analyze_dates reset, 
        requiring a re-run of AssociationAnalysis to redo those counts from scratch
        (but will now count as the merged / composite item rather than separate ones).
        
        Could theoretically figure out how to combine the association stats without re-running analysis, but 
            patient_counts are supposed to ignore duplicates, so hard to know how to aggregate stats 
            (not enough info in them to tell if unique cooccurrences?)

        Examples this could be relevant for:
        All blood transfusion indexes, G vs J vs Feeding tube equivalent, Ear, Eyes med routes irrelevant which ear/eye.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Deactivate other items
            deactivateIds = set(clinicalItemIds);
            deactivateIds.discard(baseClinicalItemId);
            self.deactivateAnalysis(deactivateIds, conn=conn);
            
            # Build composite item name and description
            allIds = set(deactivateIds);
            allIds.add(baseClinicalItemId);
            
            query = SQLQuery();
            query.addSelect("clinical_item_id");
            query.addSelect("name");
            query.addSelect("description");
            query.addFrom("clinical_item");
            query.addWhereIn("clinical_item_id", allIds);
            query.addOrderBy("name");  # Ensure consistency across multiple runs
            results = DBUtil.execute(query, conn=conn);
            
            nameList = list();
            descrList = list();
            # First pass to get Base Item Description
            for (clinicalItemId, name, description) in results:
                if clinicalItemId == baseClinicalItemId:
                    if name is None:
                        name = "";
                    if description is None:
                        description = "";
                    nameList.append(name);
                    descrList.append(description);
                    break;
            # Second pass to get the rest
            for (clinicalItemId, name, description) in results:
                if clinicalItemId != baseClinicalItemId:
                    if name is None:
                        name = "";
                    if description is None:
                        description = "";
                    nameList.append(name);
                    descrList.append(description);
            compositeName = str.join("+", nameList );
            compositeDescription = str.join("+", descrList );
            
            DBUtil.updateRow("clinical_item", {"name": compositeName, "description": compositeDescription}, baseClinicalItemId, conn=conn);

            if reassignMergedItems:
                # Reassign other items to the base item, but save backup data first
                query = SQLQuery();
                query.addSelect("patient_item_id");
                query.addSelect("clinical_item_id");
                query.addFrom("patient_item");
                query.addWhereIn("clinical_item_id", deactivateIds);
                results = DBUtil.execute(query, conn=conn);

                insertQuery = DBUtil.buildInsertQuery("backup_link_patient_item", ["patient_item_id","clinical_item_id"] );
                for (patientItemId, clinicalItemId) in results:
                    insertParams = (patientItemId, clinicalItemId);
                    try:
                        # Optimistic insert of a new unique item
                        DBUtil.execute( insertQuery, insertParams, conn=conn );
                    except IntegrityError, err:
                        # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
                        log.info(err);
                        pass;

                # Now to actual reassignment of patient items to the unifying base clinical item
                placeholders = generatePlaceholders(len(deactivateIds));
                query = "update patient_item set clinical_item_id = %s where clinical_item_id in (%s)" % (DBUtil.SQL_PLACEHOLDER,placeholders);
                params = [baseClinicalItemId];
                params.extend(deactivateIds);
                DBUtil.execute(query, params, conn=conn);

        finally:
            if not extConn:
                conn.close();

    def unifyRedundant(self, baseClinicalItemId, clinicalItemIds, conn=None):
        """The specified clinical items will be collapsed into the first clinical item provide, 
        assuming the clinical_item pairs have perfect 1-to-1 association, indicating redundancy 
        (though this sometimes occurs legitimately as well).  
        Deactivate the duplicate items (remove from analysis as above) except for 1, and relabel that 1 
        to indicate its unification from the others
        
        Look for examples with query like the following, though it also reveals many potential false positives
        with uncommon orders that coincidentally only occur simultaneously with another order.

            select 
                preci.description, 
                cia.clinical_item_id, 
                cia.count_0,
                cia.subsequent_item_id,
                postci.description
            from 
                clinical_item as preci,
                clinical_item_association as precia,
                clinical_item_association as cia,
                clinical_item_association as postcia,
                clinical_item as postci

            where
                preci.clinical_item_id = precia.clinical_item_id and
                precia.clinical_item_id = precia.subsequent_item_id and
                precia.clinical_item_id = cia.clinical_item_id and
                cia.clinical_item_id <> cia.subsequent_item_id and
                cia.subsequent_item_id = postcia.clinical_item_id and
                postcia.clinical_item_id = postcia.subsequent_item_id and
                postcia.clinical_item_id = postci.clinical_item_id and
                precia.count_0 = cia.count_0 and
                cia.count_0 = postcia.count_0 and
                cia.count_0 > 10
            limit 1000        
        """
        # Basically does same thing as merging composite items, just skip the reassignment step
        self.mergeRelated(baseClinicalItemId, clinicalItemIds, reassignMergedItems=False);

    def loadLinkedItemIdsByBaseId(self, maxItemId=None, conn=None):
        """Effectively load the clinical_item_link table into a dictionary object
        to facilitate rapid lookup of linked clinical items.
        Includes flattening of link hierarchies such that multi-level inherited links will be reported as directly
        belonging to any parent items.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        
        linkedItemIdsByBaseId = None;
        try:
            linkedItemIdsByBaseId = dict();
            query = "select clinical_item_id, linked_item_id from clinical_item_link";
            params = list();
            if maxItemId is not None:
                query += " where clinical_item_id < %s" % DBUtil.SQL_PLACEHOLDER;
                params.append(maxItemId);
            clinicalItemLinkTable = DBUtil.execute( query, params, conn=conn);
            for (clinicalItemId, linkedItemId) in clinicalItemLinkTable:
                if clinicalItemId not in linkedItemIdsByBaseId:
                    linkedItemIdsByBaseId[clinicalItemId] = set();
                linkedItemIdsByBaseId[clinicalItemId].add(linkedItemId);

            # Additional passes to capture inherited relationships (beware this could be infinite loop if cyclic inheritance pattern)
            lookForNewLinks = True;
            inheritanceDepth = 0;
            while lookForNewLinks:
                lookForNewLinks = False;
                inheritanceDepth += 1;
                
                for (clinicalItemId, linkedItemIdSet) in linkedItemIdsByBaseId.iteritems():
                    linkedItemIdSetCopy = set(linkedItemIdSet); # Make copy as could be modifying set as iterate through it
                    for linkedItemId in linkedItemIdSetCopy:
                        if linkedItemId in linkedItemIdsByBaseId:
                            subLinkedItemIds = linkedItemIdsByBaseId[linkedItemId];
                            preSize = len(linkedItemIdSet);
                            linkedItemIdSet.update(subLinkedItemIds);
                            postSize = len(linkedItemIdSet);
                            if postSize > preSize:
                                # New inherited links were recorded, so will need to do at least one more pass to keep look for further inheritance depth
                                lookForNewLinks = True;
                
                if inheritanceDepth > 8 and (math.log(inheritanceDepth,2) % 1) < 0.001:
                    # Very high inheritance depth, caution that may be infinite loop that should be aborted
                    log.warning("Clinical Item Link Inheritance Resolution down to depth %s.  Potential for infinite loop." % inheritanceDepth );
        finally:
            if not extConn:
                conn.close();
        return linkedItemIdsByBaseId;

    def getCacheData(self,key,conn=None):
        """Utility function to retrieve cached data item from data_cache table.  Returns None if not found"""
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        cacheQuery = "select data_value from data_cache where data_key = %s" % DBUtil.SQL_PLACEHOLDER;
        cacheResult = DBUtil.execute(cacheQuery, (key,), conn=conn);
        if len(cacheResult) > 0:
            return cacheResult[0][0];
        else:
            return None;

        if not extConn:
            conn.close();

    def setCacheData(self,key,value,conn=None):
        """Utility function to set cached data item in data_cache table"""
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Clear any prior setting to make way for the new one
        self.clearCacheData(key,conn=conn);
        
        insertQuery = DBUtil.buildInsertQuery("data_cache", ("data_key","data_value","last_update") );
        insertParams= ( key, str(value), datetime.now() );
        DBUtil.execute( insertQuery, insertParams, conn=conn );

        if not extConn:
            conn.close();

    def clearCacheData(self,key,conn=None):
        """Utility function to set cached data item in data_cache table"""
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        cacheQuery = "delete from data_cache where data_key = %s" % DBUtil.SQL_PLACEHOLDER;
        DBUtil.execute( cacheQuery, (key,), conn=conn );

        if not extConn:
            conn.close();

    def executeCacheOption(self, query, parameters=None, includeColumnNames=False, incTypeCodes=False, formatter=None, conn=None, connFactory=None, autoCommit=True):
        """Wrap DBUtil.execute.  If instance's dataCache is present, will check and store any results in there
        to help reduce time for repeat queries.
        
        Beware, bad idea to store lots of varied, huge results in this cache, otherwise memory leak explosion.
        """
        if connFactory is None:
            connFactory = self.connFactory;

        dataCache = self.dataCache;
        if dataCache is None:
            dataCache = dict(); # Create a temporary holder

        queryStr = DBUtil.parameterizeQueryString(query);
        if queryStr not in dataCache:
            dataCache[queryStr] = DBUtil.execute( query, parameters, includeColumnNames, incTypeCodes, formatter, conn, connFactory, autoCommit );
            self.queryCount += 1;
        
        dataCopy = list(dataCache[queryStr]);
        
        return dataCopy;
    
    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options]\n"
        
        parser = OptionParser(usage=usageStr)
        
        parser.add_option("-d", "--deactivateAnalysis",  dest="deactivateAnalysis", metavar="<clinicalItemIds>",  help="The specified clinical_items will be removed from association analysis.  This includes changing analysis_status to 0, clearing the analyze_date on any patient_items, and removing all related clinical_item_association records.")
        parser.add_option("-D", "--deactivateAnalysisByCount",  dest="deactivateAnalysisByCount", metavar="<instanceCount|categoryIds>",  help="Deactivate analysis as above on all clinical_items with a number patient_item instances less than the specified instanceCount threshold.  Add comma separated list of category IDs after '|' delimiter to specify only certain categories to apply deactivations to")
        parser.add_option("-c", "--compositeRelated", dest="compositeRelated", metavar="<clinicalItemIds|itemName|itemDescription|categoryId(|compositeId)>",  help="A new clinical item will be created, with patient item records created to match every one currently matching one of the specified clinical items.  Expect '|' delimited parameter, with components specifying new composite item name/code, description, and clinical item category to be created under.  ID of newly created item will be printed to stdout.  Option to specify desired composite ID explicitly")
        parser.add_option("-g", "--generatePatientItemsForCompositeId", dest="generatePatientItemsForCompositeId", metavar="<clinicalItemIds|compositeId>",  help="Assume given composite clinical item has already been created, then create patient item records to match every one currently matching one of the specified clinical items or a child linked item.")
        parser.add_option("-m", "--mergeRelated", dest="mergeRelated", metavar="<clinicalItemIds>",  help="The specified clinical items will be merged / composited into the first clinical item provided.  Patient_item instances will be reassigned to the merged clinical_item (while backup links will be saved to backup_link_patient_item), clinical_item_association counts for the merged item will be updated to reflect the accumulation of all merged items, then the remaining now redundant items will be deactivated.")
        parser.add_option("-u", "--unifyRedundant",    dest="unifyRedundant", metavar="<clinicalItemIds>",    help="The specified clinical items will be collapsed into the first clinical item provide, assuming the clinical_item pairs have perfect 1-to-1 association, indicating redundancy (though this sometimes occurs legitimately as well).  Deactivate the duplicate items (remove from analysis as above) except for 1, and relabel that 1 to indicate its unification from the others")
        parser.add_option("-C", "--updateClinicalItemCounts",    dest="updateClinicalItemCounts",     action="store_true",    help="If set, will update the denormalized clinical_item.item_count columns with the current DB data")
        parser.add_option("-r", "--resetAssociationModel",    dest="resetAssociationModel",     action="store_true",    help="If set, will clear out any existing data/parameters generated from association model (e.g., clinical_item_association, analyze_date, cache values)")

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        if options.deactivateAnalysis is not None:
            clinicalItemIds = set();
            for itemIdStr in options.deactivateAnalysis.split(","):
                clinicalItemIds.add(int(itemIdStr));
            self.deactivateAnalysis(clinicalItemIds);
        elif options.deactivateAnalysisByCount is not None:
            paramSplit = options.deactivateAnalysisByCount.split("|");
            thresholdInstanceCount = int(paramSplit[0]);
            categoryIds = None;
            if len(paramSplit) > 1:
                categoryIds = set();
                categoryIdStrs = paramSplit[1].split(",");
                for idStr in categoryIdStrs:
                    categoryIds.add(int(idStr));
            self.deactivateAnalysisByCount(thresholdInstanceCount, categoryIds);
        elif options.mergeRelated is not None:
            baseClinicalItemId = None;
            clinicalItemIds = set();
            for itemIdStr in options.mergeRelated.split(","):
                clinicalItemId = int(itemIdStr);
                if baseClinicalItemId is None:
                    baseClinicalItemId = clinicalItemId;
                clinicalItemIds.add(clinicalItemId);
            self.mergeRelated(baseClinicalItemId, clinicalItemIds);
        elif options.compositeRelated is not None:
            compositeParams = options.compositeRelated.split("|");
            (sourceItemIdsStr, itemName, itemDescription, categoryIdStr) = compositeParams[:4];
            compositeItemId = None;
            if len(compositeParams) > 4:
                compositeItemId = int(compositeParams[4]);
            
            clinicalItemIds = set();
            for itemIdStr in sourceItemIdsStr.split(","):
                clinicalItemId = int(itemIdStr);
                clinicalItemIds.add(clinicalItemId);
                
            compositeItemId = self.compositeRelated(clinicalItemIds, itemName, itemDescription, int(categoryIdStr), compositeId=compositeItemId );
            print >> sys.stdout, compositeItemId;
        elif options.generatePatientItemsForCompositeId is not None:
            (sourceItemIdsStr, compositeIdStr) = options.generatePatientItemsForCompositeId.split("|");
            
            clinicalItemIds = set();
            for itemIdStr in sourceItemIdsStr.split(","):
                clinicalItemId = int(itemIdStr);
                clinicalItemIds.add(clinicalItemId);
                
            self.generatePatientItemsForCompositeId(clinicalItemIds, int(compositeIdStr) );
        
        elif options.unifyRedundant is not None:
            baseClinicalItemId = None;
            clinicalItemIds = set();
            for itemIdStr in options.mergeRelated.split(","):
                clinicalItemId = int(itemIdStr);
                if baseClinicalItemId is None:
                    baseClinicalItemId = clinicalItemId;
                clinicalItemIds.add(clinicalItemId);
            self.unifyRedundant(baseClinicalItemId, clinicalItemIds);
        elif options.updateClinicalItemCounts:
            self.updateClinicalItemCounts();
        elif options.resetAssociationModel:
            self.resetAssociationModel();

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = DataManager();
    instance.main(sys.argv);
