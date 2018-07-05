# Derived CDSS / CPOE Tables

## Overview
Much of our research is based on the Stanford Clinical Data Warehouse
aka STARR, formerly STRIDE). However, these tables are sometimes difficult
to query because all of the information about a given patient is strewn about
5-6 separate tables. To make day-to-day research and development easier, we
have created "derived tables" from the original STRIDE data.

For more information about the raw STRIDE data, see `stride/stride.md`.

## Building CDSS

### Load the STRIDE tables

For information on how to do this, see `stride/stride.md`.

### Transform the STRIDE tables --> CDSS (runtime: 40 – 50 hours)

First, build the schemata for the derived tables.

**schemata (runtime: 20 – 30 seconds)**

`python scripts/CDSS/CDSSDataLoader.py --schemata`

Second, convert all of the STRIDE tables to derived tables.

**stride_patient (runtime: 5 – 10 minutes)**

`python medinfo/dataconversion/STRIDEDemographicsConversion.py`

**stride_treatment_team (runtime: 60 – 90 minutes)**

`python medinfo/dataconversion/STRIDETreatmentTeamConversion.py -a -s 2008-01-01`

**stride_dx_list (runtime: 60 - 90 minutes)**

`python medinfo/dataconversion/STRIDEDxListConversion.py -s 2008-01-01`

**stride_preadmit_med (runtime: 5 – 10 minutes)**

`python medinfo/dataconversion/STRIDEPreAdmitMedConversion.py -m 5 -s 2008-01-01`

**stride_order_med (runtime: 3 – 4 hours)**

`python medinfo/dataconversion/STRIDEOrderMedConversion.py -m 5 -d 5 -s 2008-01-01`

**stride_order_proc (runtime: 15 – 20 hours)**

`python medinfo/dataconversion/STRIDEOrderProcConversion.py -s 2008-01-01`

**stride_order_results (runtime: 20 – 25 hours)**

`python medinfo/dataconversion/STRIDEOrderResultsConversion.py -s 2008-01-01`


### Post-process the CDSS tables (runtime: 20 – 30 minutes)
The clinical decision support system relies on an association matrix which
illustrates how commonly two events co-occur. To perform this analysis, we need
to do some post-processing on the CDSS tables. In particular, we need to:
* identify clinical items we don't want in the matrix
* identify clinical items we don't want to recommend
* combine highly related clinical items into virtual clinical items
* define synonyms for certain clinical item names
* define the possible outcomes we want to track.


`python scripts/CDSS/CDSSDataLoader.py --process`

### psql --> dumps (runtime: 20 – 30 minutes)

Because this process only needs to be run once, we have stored a backup
version fo these files on [Stanford Medicine Box](https://stanfordmedicine.app.box.com/folder/50484084132).

First, edit the database variables in `scripts/CDSS/psql/dump_cdss.sh`.

Then run the script in the same directory as the dump files.

### dumps --> psql (runtime: 60 – 90 minutes)

First, edit the database variables in `scripts/CDSS/psql/restore_cdss.sh`

Then run the script in the same directory as the dump files.

## Querying CDSS

To get a better sense of the type of data contained within the STRIDE
data set, inspect the schema definition files in `scripts/CDSS/psql/schemata`.

To actually query the data, see [these SQL resources](https://github.com/HealthRex/CDSS/wiki/STRIDE-Database#postgresql)
and [this STRIDE-specific tutorial](https://github.com/HealthRex/CDSS/wiki/STRIDE-SQL-Tutorial).
