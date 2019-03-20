Directory contains a dump of latest version of data that drives clinical order entry case simulations.
Requires a matching clinical_item database to work off of, currently compatible with the STRIDE Inpatient 2009-2014 (5 year) sample. 
Will NOT automatically be compatible with more recent versions, because the clinical_item_id assignments will be different, 
though much of this could be remapped if needed.

Some of the data preparation steps necessary to re-create the simulation mapping data (e.g., mapping test orders to expected results)
is defined in the following script. For new cases, would require some manual inspection of the large table of relations.
  prepCPOESimulationData.py

If want to add common synonyms for order lookups (e.g., 'BMP' for 'Basic Metabolic Panel', see (and run)
  stride.clinical_item.ClinicalItemDataLoader.ClinicalItemDataLoader.add_clinical_item_synonyms() 

See schema definition (without data in this folder) in the file below for a description of the simulation data organization
  medinfo/db/definition/cpoeSimulation.sql


