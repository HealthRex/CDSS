#### Learning Objectives:
- Identify and access an updated dataset from an external project in BigQuery.
- Copy the identified dataset into a new dataset with a unique ID within your own BigQuery project.
- Set up appropriate access controls for the newly created dataset.
- Streamline the process for annual updates, ensuring efficient data management and integrity.

# BigQuery Cross-Project Dataset Copy Guide

### Introduction
This guide details the steps for accessing and copying a dataset from an external project into a new dataset within your own BigQuery project. This process is essential for integrating annual updates and maintaining a structured and secure data environment.

### Prerequisites
* Access to the BigQuery Web UI.
* Permissions to view and copy datasets from the source project, and to create and manage datasets within the destination project.

### Accessing the Updated Dataset
#### 1. Add the External Project to Your Project List
* In the BigQuery console, click on "+ ADD" on the top left.
* Choose "Star a project by name" from the dropdown menu.
* In the dialog that appears, type the name of the external project you have been granted access to (e.g., `example-external-project`) and press Enter.
* The project should now be listed in your BigQuery resources.

#### 2. Locate the Updated Dataset
* Navigate to the newly pinned project in your resource list.
* Expand the project to view the available datasets.
* Identify the updated dataset you need to copy (e.g., `updated_dataset_2024`).

### Creating a Unique Dataset ID for the Copy
#### 1. Access BigQuery Console
* Navigate to the [BigQuery console](https://console.cloud.google.com/bigquery).

#### 2. Open the Dataset Copy Interface
* Find the dataset you intend to copy in the external project's listing.
* Click on the "COPY" button next to the dataset.

#### 3. Specify a Unique Dataset ID
* In the "Destination" field, provide a new Dataset ID that does not exist in your project (som-nero-phi-jonc101). This will be the ID for the new dataset where the tables will be copied.
* If you have an existing empty dataset intended for this purpose, you must choose a new ID for the copying process to avoid the "Dataset already exists" error.
* Make sure to change the Project ID to "som-nero-phi-jonc101" on the top.
* Complete the rest of the copy configuration as necessary and initiate the dataset copy.

### Setting Access Controls for the New Dataset
#### 1. Share the Dataset
* After the dataset has been copied, navigate to the new dataset in your project's BigQuery Web UI.
* Click "SHARE DATASET" to configure who can access the dataset.

#### 2. Manage Access
* Select the appropriate roles to grant the correct access level.
* Confirm the changes by clicking "Add", then "Done".

### Best Practices
- **Validate Data**: Ensure the copied dataset matches the source in structure and content.



