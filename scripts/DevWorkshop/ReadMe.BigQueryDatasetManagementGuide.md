#### Learning Objectives:
- Utilize BigQuery's capabilities to efficiently transfer datasets across projects, maintaining data integrity and continuity to accommodate annual updates.

# BigQuery Cross-Project Dataset Copy Guide

### Introduction
This guide outlines the procedure for copying a dataset from an external source project into a new, uniquely identified dataset within your own BigQuery project (`som-nero-phi-jonc101`). 

### Prerequisites
* Access to the BigQuery Web UI.
* Permissions to copy datasets in the source project and to create new datasets in the destination project.

### Creating a Unique Dataset ID for the Copy
#### 1. Access BigQuery Console
* Navigate to the [BigQuery console](https://console.cloud.google.com/bigquery).

#### 2. Open the Dataset Copy Interface
* Locate the dataset you wish to copy in the source project.
* Click on the "COPY" button.

#### 3. Specify a Unique Dataset ID
* In the "Destination" field, provide a new Dataset ID that does not exist in your project (`som-nero-phi-jonc101`). This will be the ID for the new dataset where the tables will be copied.
* If you have an existing empty dataset intended for this purpose, you must choose a new ID for the copying process to avoid the "Dataset already exists" error.
* Make sure to change the Project ID to "som-nero-phi-jonc101" on the top. 
* Complete the rest of the copy configuration as necessary and initiate the dataset copy.

### Setting Access Controls for the New Dataset
#### 1. Configure Dataset Permissions
* After the dataset has been successfully copied, navigate to your new dataset in the BigQuery Web UI.
* Click on "SHARE DATASET" to open the access control settings.


### Best Practices
- **Data Consistency**: Post-copy, check the new dataset for completeness and consistency with the source.
