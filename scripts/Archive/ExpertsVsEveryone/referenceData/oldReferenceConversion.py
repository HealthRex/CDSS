# Translate old guideline reference data into current data model's clinical_item_id encoding
# Will end up without perfect 1-to-1 mapping, so still need some curation afterwards

from medinfo.db.ResultsFormatter import *

candidateOrdersDF = pandas_read_table(open("candidateOrders.tab"));
oldReferencesDF = pandas_read_table(open("oldReferences.tab"));

conn = pandas_to_sqlconn(candidateOrdersDF,"candidateOrders");
conn = pandas_to_sqlconn(oldReferencesDF,"oldReferences",conn);

resultsDF = pandas_read_sql_query("""
	select oldReferences.*, candidateOrders.* 
	from oldReferences left join candidateOrders on  oldReferences.name_1 = candidateOrders.name
	order by oldReferences.name, oldReferences.type, oldReferences.name
	""",
	conn=conn);

pandas_write_table(resultsDF, open("oldReferencesMerged.tab","w"))
