"""For existing admit diagnosis order reference sets, generate worksheet data
so another annotater can review and curate themselves.
Include orders that are 
- mentioned in the existing reference sets,
- top X overall common orders, 
- top X orders most likely for that admission diagnosis (within 24 hours, sorted by PPV), and 
- top X orders disproportionately likely for that admission diagnosis (within 24 hours, sorted by p-value)
"""

import sys,os;
from pprint import pprint;
from datetime import datetime, timedelta;
from medinfo.db import DBUtil;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, RecommenderQuery;

TOP_ITEM_COUNT = 25;    # Number of top items from different lists to consider

existingReferenceOrderQuery = \
    """
    select dxici.clinical_item_id, ic.section, ic.name, ci.clinical_item_id, ci.name, ci.description, count(*)
    from
    clinical_item as dxci, item_collection_item as dxici, item_collection as ic,
    item_collection_item as refici,
    item_collection_item as recici,
    clinical_item as ci, clinical_item_category as cic
    where dxci.clinical_item_id = dxici.clinical_item_id
    and dxici.item_collection_id = ic.item_collection_id
    and ic.item_collection_id = refici.item_collection_id
    and refici.clinical_item_id = ci.clinical_item_id
    and ci.clinical_item_category_id = cic.clinical_item_category_id

    and dxici.collection_type_id = 5 -- Diagnosis Link
    and dxici.value = 3 -- Guidelines referenced
    and refici.collection_type_id = dxici.value

    and recici.collection_type_id = 1 -- Look for items that are referenced AND recommended
    and recici.clinical_item_id = refici.clinical_item_id
    and recici.item_collection_id = refici.item_collection_id

    and ci.analysis_status <> 0 and ci.default_recommend <> 0 and cic.default_recommend <> 0 -- Filter out items not usually considered for recommendation
    group by dxici.clinical_item_id, dxci.description, ic.name, ic.section, ci.clinical_item_id, ci.name, ci.description
    order by ic.section, ic.name, ci.name;
    """;

resultsTable = DBUtil.execute( existingReferenceOrderQuery );

admitDxIdSectionGuidelineNameTuples = set();    # Keep track of each guideline name set
itemIdsByAdmitDxId = dict();
for admitDxId, sectionName, guidelineName, itemId, itemName, itemDescription, itemCount in resultsTable:
    if admitDxId not in itemIdsByAdmitDxId:
        itemIdsByAdmitDxId[admitDxId] = set();
    itemIdsByAdmitDxId[admitDxId].add(itemId);
    admitDxIdSectionGuidelineNameTuples.add( (admitDxId, sectionName, guidelineName) );

recommender = ItemAssociationRecommender();

for admitDxId, itemIds in itemIdsByAdmitDxId.items():
    print(admitDxId, len(itemIds), file=sys.stderr);
    recQuery = RecommenderQuery();
    recQuery.excludeItemIds = recommender.defaultExcludedClinicalItemIds();
    recQuery.excludeCategoryIds = recommender.defaultExcludedClinicalItemCategoryIds();
    recQuery.queryItemIds = [admitDxId];
    recQuery.timeDeltaMax = timedelta(1);    # Within one day
    recQuery.countPrefix = "patient_";
    recQuery.limit = TOP_ITEM_COUNT;

    # Top results by P-value
    recQuery.sortField = "P-YatesChi2-NegLog";
    results = recommender(recQuery);
    #recommender.formatRecommenderResults(results);
    for result in results:
        itemIds.add( result["clinical_item_id"] );
        #print >> sys.stderr, result["description"];

    print(admitDxId, len(itemIds), file=sys.stderr);

    # Top results by PPV
    recQuery.sortField = "PPV";
    results = recommender(recQuery);
    for result in results:
        itemIds.add( result["clinical_item_id"] );

    print(admitDxId, len(itemIds), file=sys.stderr);

    # Top results by baseline prevalence
    recQuery.sortField = "prevalence";
    results = recommender(recQuery);
    for result in results:
        itemIds.add( result["clinical_item_id"] );

    print(admitDxId, len(itemIds), file=sys.stderr);

# Load clinicalItem models for quick lookups 
clinicalItemById = DBUtil.loadTableAsDict("clinical_item");

print(str.join("\t",["Admit Dx ID","Section","Guideline","item_collection_id","collection_type_id","value","comment","clinical_item_id","Name","Description"]));

for (admitDxId, sectionName, guidelineName) in admitDxIdSectionGuidelineNameTuples:
    itemIds = itemIdsByAdmitDxId[admitDxId];

    for itemId in itemIds:
        clinicalItem = clinicalItemById[itemId];
        # Note just printing blank spaces for values in middle
        print("%s\t%s\t%s\t\t1\t\t\t%s\t%s\t%s" % (admitDxId, sectionName, guidelineName, clinicalItem["clinical_item_id"], clinicalItem["name"], clinicalItem["description"]));
        print("%s\t%s\t%s\t\t3\t\t\t%s\t%s\t%s" % (admitDxId, sectionName, guidelineName, clinicalItem["clinical_item_id"], clinicalItem["name"], clinicalItem["description"]));

