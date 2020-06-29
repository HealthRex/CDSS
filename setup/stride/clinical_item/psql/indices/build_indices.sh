psql -U ec2-user stride-inpatient-2008-2017 -f clinical_item.indices.sql
psql -U ec2-user stride-inpatient-2008-2017 -f patient_item.indices.sql
psql -U ec2-user stride-inpatient-2008-2017 -f clinical_item_association.indices.sql
psql -U ec2-user stride-inpatient-2008-2017 -f item_collection_item.indices.sql
psql -U ec2-user stride-inpatient-2008-2017 -f clinical_item_category.indices.sql
psql -U ec2-user stride-inpatient-2008-2017 -f patient_item_collection_link.indices.sql
