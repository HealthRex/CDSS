= Dev Workshop =
Accessing GoogleCloud BigQuery within Virtual Private Cloud
(Safe for Protected Health Information)

== Learning Goals ==
- Review tiers of access restriction for moderate to high-risk patient data
  https://uit.stanford.edu/guide/riskclassifications
- Access Control requests
- Web GUI access to BigQuery databases
- Virtual Private Network connection into PHI secure Virtual Private Cloud
- Programmatic (Python) API access to BigQuery databases

== Preconditions ==
- Know how to run command line programs and set environment variables
- Python Installed

Recommended to save time during workshop:
- Access granted to Virtual Private Cloud contained BigQuery database
- Google Cloud SDK Installed
  https://cloud.google.com/sdk/install
- Google Cloud - Python API Libraries Installed
  python -m pip install --upgrade google-cloud-bigquery

== Workshop Steps ==
- Review tiers of access restriction for moderate to high-risk patient data
  * Name (non-obvious) data elements that qualify as Protected Health Information (and thus High-Risk Data that require stronger security)
    - Real dates (relative times or date shifted / jittered okay)
    - Location more precise than 3 digit ZIP code (including hospital bed numbers)
    - Age when >90 years old
    - Any freely entered text fields (risk of incidentally embedded PHI written in a text field)

  * Distinguish between public Google Cloud Platform, Stanford-only GCP, Stanford-VPC GCP
    https://github.com/HealthRex/CDSS/wiki/Google-BigQuery-Access

=== Stanford-only GCP project "mining-clinical-decisions" (still not safe for PHI) ===
- Access Control requests
  If you want in this club, complete the data usage requirements first and have a group sys admin grant BigQuery User privileges through GCP interface linked below.  
  https://github.com/HealthRex/CDSS/wiki/Data-usage-training-and-agreements
  https://console.cloud.google.com/iam-admin/iam?authuser=1&project=mining-clinical-decisions
  
- Web GUI access to BigQuery databases
  Connect to the project through a web browser  
  https://console.cloud.google.com/bigquery?authuser=1&project=mining-clinical-decisions
  - Note that you have to select your stanford.edu account login in the top-right
  - Note that you may have to select the project name from the drop list on the top-middle nav bar
  - See bottom left for lists of projects, which contain lists of datasets/databases, which contain lists of tables that you can query. For example:

          SELECT *
          FROM starr_datalake2018.order_med
          LIMIT 100;

=== Stanford-VPC GCP project "som-nero-phi-jonc101" (safe for PHI) ===
- Access Control requests
  If you want in this club, you will further need to be added to a respective IRB that allows for PHI access and have a group sys admin grant membership to the nero:jonc101-bq-users workgroup via the link below. 
  If additional privileges are needed, they need to be requested through Stanford Research Computing Center support <srcc-support@stanford.edu>
  https://workgroup.stanford.edu/main/WGApp

- Web GUI access to BigQuery databases
  Try connecting to the secure project through browser similar to above...
  https://console.cloud.google.com/bigquery?authuser=1&project=som-nero-phi-jonc101

  It should fail with an error like: "VPC Service Controls: Request is prohibited by organization's policy..."
  To get through, you will first need to Virtual Private Network (VPN) connection into a Stanford secured network:

- Virtual Private Network connection into PHI secure Virtual Private Cloud
  Download and run the respective VPN client from the link below
  https://uit.stanford.edu/service/vpn
  
  Login (SUNetID and password with two-factor authentication) through the VPN client and be sure to select
  "Full Traffic non-split-tunnel" for the Group option.

  Try refreshing your web browser to reconnect through the web GUI to the BigQuery project database again.
  You can continue to do any regular work in the meantime, though technically any internet traffic you're conducting is not being sent direct. It is being encrypted and sent through the Stanford secure network first and then relayed on to the actual websites or email servers you're trying to reach. This allows your computer now to mimic being within the secured virtual private network.

- Programmatic (Python) API access to BigQuery databases (Google Cloud SDK)
  You will need to create a local JSON key file to identify yourself in your (Python) programs if you want them to access these secured databases.

  - Find, download and run the respective Google Cloud SDK installer for your system from the link below. 
    (If you already have Python 2.7 installed on your system, you can skip that dependency)
    https://cloud.google.com/sdk/install
  - Run the Google Cloud SDK initializer from command-line 

    gcloud init

  - Run the Google Cloud application authentication
    This should spawn a web browser (or create a web link you can use) to login as a specific user 
    After completing the above, go back to your command terminal and it should report a message that it created a JSON key file in a local directory (recommend you rename it to something that includes your user name, and store it in a place you will remember).

    gcloud auth application-default login

  - Install Python-Google Cloud connection libraries with the PIP installer

    python -m pip install --upgrade google-cloud-bigquery

  - Create a local environment variable to tell the Google Cloud libraries where to find the key file
    Python code in medinfo tree can just import LocalEnv.py that can set the environment variable at runtime
    Mac/Linux: export GOOGLE_APPLICATION_CREDENTIALS=[PathToKeyFile]
    Windows(cmd): set GOOGLE_APPLICATION_CREDENTIALS=[PathToKeyFile] 
       (Replace [PathToKeyFile] with the location of the JSON key file created in the prior step)

  - Try connecting to a secured project BigQuery database and query for some data
    
    Python
    >>> from google.cloud import bigquery;
    >>> from google.cloud.bigquery import dbapi;
    >>> client = bigquery.Client("som-nero-phi-jonc101"); # Project identifier
    >>> conn = dbapi.connect(client);
    >>> cursor = conn.cursor();
    >>> query = "select rit_uid, gender, birth_date_jittered from `starr_datalake2018.demographic` limit 10"; # Example dataset table
    >>> cursor.execute(query);
    >>> results = cursor.fetchall();
    >>> for row in results:
    ...   print row;

    Or if you prefer Pandas dataframes
    >>> import pandas as pd;
    >>> resultsDF = pd.read_sql_query(query, conn);
    >>> print resultsDF;


== See Also ==
Notes on connecting to BigQuery databases through R API
https://cloud.google.com/blog/products/gcp/google-cloud-platform-for-data-scientists-using-r-with-google-bigquery


Support Notebooks in Jupyter for examples of tips and tricks for reviewing and manipulating datasets.
https://code.stanford.edu/starr/nero-starr-notebooks


If set CDSS code tree LocalEnv.DATABASE_CONNECTOR_NAME parameters, then medinfo.db.DBUtil.connection should take care of setting up a Python DB-API compliant connection object to the BigQuery database (not all functionality supported at this time).
If you need to do direct manipulations against the database (e.g., creating and renaming tables, importing data, etc.), then you may want to directly use the BigQueryClient interface. Otherwise I recommended sticking to the generic DB-API interface, so you remain cross-platform compatible with other databases.



Alternative option to create service account authentication keys instead of user authentication keys
https://cloud.google.com/bigquery/docs/authentication/
