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
- Access granted to Virtual Private Cloud containing BigQuery database
- Google Cloud SDK Installed
  https://cloud.google.com/sdk/install
- Google Cloud - Python API Libraries Installed
  python -m pip install --upgrade google-cloud-bigquery

== Workshop Steps ==
- Review tiers of access restriction for moderate to high-risk patient data
  * Name (non-obvious) data elements that qualify as Protected Health Information 
      (and thus High-Risk Data that require stronger security)
    - Real dates (relative times or date shifted / jittered okay)
    - Location more precise than 3 digit ZIP code (including hospital bed numbers)
    - Age when >90 years old
    - Any freely entered text fields (risk of incidentally embedded PHI written in a text field)

  * Distinguish between public Google Cloud Platform, Stanford-only GCP, Stanford-VPC GCP
    https://github.com/HealthRex/CDSS/wiki/Google-BigQuery-Access

=== Stanford-only GCP project "mining-clinical-decisions" (still not safe for PHI) ===
- Access Control requests
  If you want in this club, complete the data usage requirements first and have a group sys admin grant 
  BigQuery User and Viewer privileges through the GCP interface linked below.  
  https://github.com/HealthRex/CDSS/wiki/Data-usage-training-and-agreements
  https://console.cloud.google.com/iam-admin/iam?authuser=1&project=mining-clinical-decisions
  
- Web GUI access to BigQuery databases
  Connect to the project through a web browser  
  https://console.cloud.google.com/bigquery?authuser=1&project=mining-clinical-decisions
  - Note that you have to select your stanford.edu account login in the top-right
  - Note that you may have to select the project name from the drop list on the top-middle nav bar


  It should fail with an error like: "VPC Service Controls: Request is prohibited by organization's policy..."
  To get through, you will first need to Virtual Private Network (VPN) connection into a Stanford secured network:

- Virtual Private Network connection into PHI secure Virtual Private Cloud
  Download and run the respective VPN client from the link below
  https://uit.stanford.edu/service/vpn
  
  Login (SUNetID and password with two-factor authentication) through the VPN client and be sure to select
  "Full Traffic non-split-tunnel" for the Group option.
  
  Try refreshing your web browser to reconnect through the web GUI to the BigQuery project database again.
  You can continue to do any regular work in the meantime, though technically any internet traffic 
  you're conducting is not being sent direct. It is being encrypted and sent through the Stanford 
  secure network first and then relayed on to the actual websites or email servers you're trying to reach. 
  This allows your computer now to mimic being within the secured virtual private network.

- IPv4 vs. IPv6
  If you're still getting VPC access control errors despite the above (particularly when logging in from home),
  be sure your network adapter is set to use IPv4 rather than IPv6. 
  This reflects an updated version of the way internet addresses are allocated, 
  but looks like GCP VPC protocols don't accomodate for the newer system yet.
  
  Apple Systems:
  - Go to Apple - > System Preferences -> Network
  - Select the current network connection listed on the left-hand side, then click the Advanced button.
  - Go to the TCP/IP tab at the top
  - Beside "Configure IPv6", set it to "Link-local Only" and "Apply"
  
  Windows Systems:
  - Settings > Network & Internet
  - Change Adapter Options
  - Select your WiFi or Ethernet or other network connection device
  - Properties
  - Uncheck "Internet Protocol Version 6 (TCP/IPv6)"

- VPN Group option:
  If you're still getting VPC access control errors despite the above,
  try to go back and change the group option from "Full Traffic non-split-tunnel" to "Stanford Default ..." and reconnect the vpn. 

- Test Queries
  - See bottom left for lists of projects, which contain lists of datasets/databases, 
    which contain lists of tables that you can query.
    (You may need to manually search for the project "mining-clinical-decisions" and "Pin" it for later use.)
    For example:

          SELECT *
          FROM starr_datalake2018.order_med
          LIMIT 100;

=== Stanford-VPC GCP project "som-nero-phi-jonc101" (safe for PHI) ===
- Access Control requests
  If you want in this club, you will further need to be added to a respective IRB that allows for 
  PHI access and have a group sys admin grant membership to the 
  nero:jonc101-bq-users workgroup (or subgroups for specific datasets) via the link below. 
  If additional privileges are needed, they need to be requested through 
  Stanford Research Computing Center support <srcc-support@stanford.edu>
  https://workgroup.stanford.edu/main/WGApp

- Web GUI access to BigQuery databases
  Try connecting to the secure project through your browser similar to above...
  https://console.cloud.google.com/bigquery?authuser=1&project=som-nero-phi-jonc101

- Programmatic (Python) API access to BigQuery databases (Google Cloud SDK)
  You will need to create a local "Application Default Credentials" JSON key file 
  to identify yourself in your (Python) programs as 
  if you want them to access these secured databases.
  https://cloud.google.com/docs/authentication/getting-started
  https://cloud.google.com/docs/authentication/best-practices-applications

     - To locate the JSON key file for your Google Cloud service account on a Mac, you can follow these steps: 
     1.	Google Cloud Console: 
         •Go to the Google Cloud Console: https://console.cloud.google.com/ 
         • Log in with the Google account associated with "som-nero-phi-jonc101" Google Cloud project. 
     2.	Service Account: 
         • In the left navigation pane, click on "IAM & Admin" > "Service accounts." 
     3.	Locate Your Service Account:
         • Look for the service account you want to use to access Google BigQuery within the project. 
            It should be listed in the "Service accounts" section. 
     4.	Create a JSON Key File: 
         • Click on the service account name to access its details. 
         • In the "Keys" tab, you'll see a list of keys associated with the service account. If you don't have one yet, you can create a new key. 
         • Click on the "Add Key" dropdown and select "Create new key." 
         • Choose the key type as JSON. 
         • Click the "Create" button. This will download a JSON key file to your computer. 
     5.	Locate the JSON Key File: 
         • The JSON key file will typically be downloaded to your computer's default downloads directory.
     6.	Move the JSON Key File: 
         • Once you've located the JSON key file, you may want to move it to a secure location on your computer. 

     - Contact SRCC Help Desk (If Needed): 
       If you encounter the error message: "You need additional access. You do not have permission to view the service accounts in this project."
       or if you don't see the permission to view keys, you can contact the SRCC Help Desk for assistance: 
         • Email: "srcc-support AT stanford DOT edu"

     - Additional Note:
       If you have service account permission but still don't see the permission to view keys, you can grant yourself access by becoming a Service 
       Account Key Admin. Here's how:
         • Go to the Google Cloud Console: https://console.cloud.google.com/ 
         • Navigate to the project. 
         • Click on "IAM & Admin" > "Service accounts." 
         • Locate your service account. 
         • Under the "Actions" tab, click on the three dots and select "Manage Permissions."
         • Click on "GRANT ACCESS" and add yourself as a "Service Account Key Admin."

  - Find, download and run the respective Google Cloud SDK installer for your system from the link below. 
    (If you already have Python installed on your system, you can skip that dependency)
    https://cloud.google.com/sdk/install
  - Run the Google Cloud SDK initializer from command-line 

    gcloud init

  - Run the Google Cloud application authentication

    gcloud auth application-default login
    
    This should spawn a web browser (or create a web link you can use) to login as a specific user 
    After completing the above, go back to your command terminal and it should report a message 
    that it created a JSON key file in a local directory 
    E.g., "Credentials saved to file: [C:\Users\jonc1\AppData\Roaming\gcloud\application_default_credentials.json]"
    (recommend you rename it to something that includes your user name, and store it in a place you will remember).

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
    >>> client = bigquery.Client("som-nero-phi-jonc101"); # Alternatively, set GOOGLE_CLOUD_PROJECT environment variable
    >>> conn = dbapi.connect(client);
    >>> cursor = conn.cursor();
    >>> query = "select rit_uid, gender, birth_date_jittered from `starr_datalake2018.demographic` limit 10"; # Example dataset table
    >>> cursor.execute(query);
    >>> results = cursor.fetchall();
    >>> for row in results:
    ...   print( row );

    Or if you prefer Pandas dataframes
    >>> import pandas as pd;
    >>> resultsDF = pd.read_sql_query(query, conn);
    >>> print( resultsDF );
    
    If getting errors about access issues (e.g., "VPC Service Controls: Request is prohibited by organization's policy"),
    make sure you're able to query through the BigQuery web interface and review above steps.
    - Did you fix your internet connection to use IPv4 instead of IPv6 protocol?
    - Did you connect to the VPN?
    - Did you login through your stanford.edu address, not gmail.com?
    Consider saving the above python code snippets as a small script file so you don't have to keep retyping it, 
    you can just quickly rerun them to test variations.


== See Also ==
Notes on connecting to BigQuery databases through R API
https://cloud.google.com/blog/products/gcp/google-cloud-platform-for-data-scientists-using-r-with-google-bigquery


Support Notebooks in Jupyter for examples of tips and tricks for reviewing and manipulating datasets.
https://code.stanford.edu/starr/nero-starr-notebooks


If you set the CDSS code tree LocalEnv.DATABASE_CONNECTOR_NAME parameters, 
then medinfo.db.DBUtil.connection should take care of setting up a Python DB-API compliant connection object 
to the BigQuery database (not all functionality supported at this time).

If you need to do direct manipulations against the database 
(e.g., creating and renaming tables, importing data, etc.), 
then you may want to directly use the BigQueryClient interface. 
Otherwise I recommended sticking to the generic DB-API interface, 
so you remain cross-platform compatible with other databases.


Alternative option to create service account authentication keys instead of user authentication keys
https://cloud.google.com/bigquery/docs/authentication/
          
===== Troubleshooting =====
Here, common issues that we faced while using the google cloud are presented and appropriate solutions and troubleshootings are described.

Issue: I should have access to database X (for example som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021), but cannot find the database when I search for it.
Solutions: Try typing only the database name (Jon_Chen_data_Oct_2021 in this example) in the search box on the top middle search bar (in the middle of the top blue ribbon). 
          
