# Restore CDSS to pSQL database

## Acquiring the data

The data is stored in Box: https://stanfordmedicine.app.box.com/folder/48947257871

The `data` subfolder contains a folder called `medinfo_2008_2017`. This folder
contains all of the psql backup files.

You can download the data in one of two ways:
1. Download the files via a browser 1-by-1 (manual).
2. Download the files via `stride/box/BoxClient.py` (automated, but untested)

To use the second method, follow the instructions in `stride/box/box-API.md`.
Then call `stride.core.StrideLoader.download_stride_data()`.

Either way, downloaded the data to `stride/data/*`

The total download time might be several hours.

## Loading the data

Within `stride/data/medinfo_2008_2017`, you'll find two restore scripts.
* `restore_stride.sql`
* `restore_cdss.sql`

Run them, wait for a few hours, and hope for success.
