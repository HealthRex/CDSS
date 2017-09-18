import sys,os;
from medinfo.db import DBUtil;

# Clear out any previous reference data (but keep the fixed order set data)
# (May want to backup database before running these commands)
print >> sys.stderr, "About to delete/replace existing item_collection_item reference data."
print >> sys.stderr, "Are you sure? (Ctrl-C to cancel)"
raw_input();	# Pause for command-line input/confirmation

conn = DBUtil.connection();
try:

	DBUtil.execute \
	(	"""
		-- Delete reference or diagnosis linking items
		delete
		from item_collection_item as ici
		where collection_type_id in (1,2,3,5);

		-- Delete the resultant orphaned parent collection records
		delete
		from item_collection
		where item_collection_id not in
		(
			select item_collection_id
			from item_collection_item
		);
		""",
		conn=conn
	);


	# Populate the database with updates to the item_collection and item_collection_item tables to add more reference collections
	DBUtil.insertFile( open("item_collection.update.tab"), "item_collection" );
	DBUtil.insertFile( open("item_collection_item.diagnosisLink.update.tab"), "item_collection_item" );
	DBUtil.insertFile( open("item_collection_item.referenceOrders.update.tab"), "item_collection_item" );

	conn.commit();
finally:
	conn.close();
