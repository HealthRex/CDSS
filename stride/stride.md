# STRIDE Inpatient Data Loading Notes

## Overview
Much of our research is based on the Stanford Clinical Data Warehouse
aka STARR, formerly STRIDE). Our primary data source within STARR is
[Epic "Clarity" database](https://www.med.upenn.edu/dac/epic-clarity-data-warehousing.html),
from which STARR has provided us data for all Stanford hospital _inpatients_
from 2008 onward. For more information about the STARR data warehouse, see [this overview](https://med.stanford.edu/researchit/services/clinical-data-warehouse.html).

## Loading STRIDE

### Download the data

STARR delivers the data to us as compressed `.csv.gz` files.

Loading the data into a queryable has the following formats:
raw --> clean --> psql

First, download all of the data from Stanford Medicine Box to
`CDSS/stride/data/`:

https://stanfordmedicine.app.box.com/folder/48947323122

(For many, you can likely skip to just downloading the pre-processed PostgreSQL dumps under data/medinfo_2008_2017.
If you have the Box Sync desktop client, you can go to the above link and pick "Sync to Desktop" under the Details options to easily download all of the files.)

### raw --> clean (runtime: 1 – 1.5 hours)

The CSVs as provided by STARR have some formatting issues
(e.g. unclosed quotes, extra commas). To fix these, use StrideLoader.

`python stride/core/StrideLoader.py --clean`

Because this process only needs to be run once, we have stored a backup
version of these files on
[Stanford Medicine Box](https://stanfordmedicine.app.box.com/folder/49709022468). These files can be imported into psql, R, or any other analysis software.

### clean --> psql (runtime: 1.5 – 2 hours)

The clean CSVs can be easily imported into a PostgreSQL database.

`python stride/core/StrideLoader.py --psql`

Note that this command also builds schemata, does some post-processing, and
builds indices. Because this database is read-only for the most part, we have
stored a backup version of this database as table dumps in
[Stanford Medicine Box](https://stanfordmedicine.app.box.com/folder/50484084132).

### psql --> dumps (runtime: 30 – 60 minutes)

First, edit the database variables in `stride/psql/dump_stride.sh`.

Then run the script in the same directory as the dump files.

### dumps --> psql (runtime: 60 – 90 minutes)

First, edit the database variables in `stride/psql/restore_stride.sh`

Then run the script in the same directory as the dump files.

## Querying STRIDE

To get a better sense of the type of data contained within the STRIDE
data set, inspect the schema definition files in `stride/psql/schemata`.

To actually query the data, see [these SQL resources](https://github.com/HealthRex/CDSS/wiki/STRIDE-Database#postgresql)
and [this STRIDE-specific tutorial](https://github.com/HealthRex/CDSS/wiki/STRIDE-SQL-Tutorial).
