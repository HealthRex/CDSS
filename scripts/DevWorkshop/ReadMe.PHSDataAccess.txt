


1) PHS Access to Restricted Datasets:
2) (Optional) Install Cardinal Key:
	- a digital certificate that is installed on a device and provides a user’s
		identity to a remote server in place of a SUNet ID and password
	- https://phsdocs.developerhub.io/software-installation/cardinal-key
3) Sign up for PHS Data Portal Account
	 	- Go to https://redivis.com/StanfordPHS/ and click on create account
			- additional information:
			- https://phsdocs.developerhub.io/computing-environment/quick-tour-phs-data-portal
		- Strongly recommend signing up for the PHS data slack channel
		- https://docs.google.com/document/d/1n304k9zMM3dji_ngJ9SQBovllK_s7zIg-du2XoRpQPc/edit
5) Getting Access to Dataset:
	- a) apply for permissions
	- b) Levels of Access:
		- overview access
		- metadata access
		- data access
	- c) Go to https://redivis.com/StanfordPHS/datasets
	- d) Select Data Access on Restricted Datasets you want access to

		E.g., Optum databases, note they are separated into versions that include Socioeconomic Status (SES), ZIP code, Date of Death, specifically because they do not want to allow you to reconstruct records with all of that information at one time (too identifying).

		IBM (previously Truven) MarketScan databases, including some supporting lookup databases like Redbook for pharamacy category data. Not as up to date as Optum and has some bad Diagnosis coding data structure based around encounters.

	- e) Complete steps for metadata access and data access
		- typically training
		- encryption verification
		- study approval: "HealthRex and Diagnostics" has already been approved

		Once access granted, can "Add Dataset" to "Projects" which will bring to Redivis graphical tree view to query 1% or 100% data samples
		Not allowed to download data or results from here, but enough to query and review high level reports.

		Can hack together queries through graphical interface, or click on code symbol button ("</>") to enter direct SQL queries.
		Add a "Transform" to a table of interest, which is basically a SQL query that can be custom edited and run, to generate a new Table of results.
		For large databases, note the different between full database and 1% sample (suffix ":sample" to the table name)
	- Note that there is a channel in the PHS slack called #access-admin if you have difficulty / substantial delays with any step



Creating API credentials:
	- Credentials enable you to access PHS projects: The token will be  used in scripts (R and Python) for authorization
			- https://redivis.com/workspace/settings
	- Scroll down to API tokens:
	- Generate new token
	- Select all access measures(all boxes): Public, Data, Organization: including edit/read
	- Save token to a file somewhere secure for reference later:

Accessing Nero Computing Environment:

Prereq:
	Stanford Sunet:
	PI emails srcc-support@stanford.edu for Nero Account
		- https://nero-docs.stanford.edu/user-prerequisites.html#submit-request-for-nero-account
		(Specify Jonathan Chen as PI / research group / supervisor and CC jonc101@stanford.edu)


Accessing PHS Data through Nero Compute:

1) GO TO: nero.compute.stanford.edu
	- make sure your stanford vpn is on (See notes from GoogleCloud VPC DevWorkshop)
	- https://nero-docs.stanford.edu/jupyter.html
2) Open a terminal under 'Other'   (Or if happy with base R, Stata, Jupyter notebook, etc. can use those interfaces via a "New Launcher...")

# https://apidocs.redivis.com/client-libraries/redipy.bigquery
3) git clone https://github.com/redivis/redipy.git		# Works for other GitHub repositories like general lab repo
4) export PYTHONPATH=/home/[SUNETID]/redipy/bigquery;$PYTHONPATH		# Better yet, add this to .bash_profile (or .bashrc if not autorun, or just do `source .bash_profile` when startup)


6) enter python console: type python
7) in python:
	import os
	from redivis import bigquery 	# or from google.cloud import bigquery
	import pandas
	os.environ['REDIVIS_API_TOKEN'] = "[TOKEN_FROM_REDIVIS]"	# Better yet, add to .bash_profile. Note the token is not a file, it's a string of characters that should be copied directly.
	client=bigquery.Client()
	# Perform a query.
	# Table at https://redivis.com/StanfordPHS/datasets/1411/tables
	QUERY = 'SELECT * FROM `jonc101.test_project_multi_user:1.query_counts_for_diabetic_med_class_claims_by_year_output:7` LIMIT 10'
	#QUERY = ('SELECT * FROM `stanfordphs.optum_zip5:139:v3_0.rx_pharmacy:9` LIMIT 10')	# Of can query from your own named sample/tables from your Redivis UI project or some general table name you have access to? Permissions note allowed to directly query off the source tables?
	df = client.query(QUERY).to_dataframe()  # API request
	print(df)

Accessing through Jupyter Notebook:
	- select home directory on left toolbar:
	- select your sunetid folder: ex: (jichiang)
	- select redipy
	- select bigquery
		- this will bring you into home/SUNETID/redivis/bigquery folder:
	- select jupyer notebook on the middle panel:
	- Repeat steps in 7 to copy code into jupyter noteboook
	
	
Install new packages:
	-R packages: http://nero-docs.stanford.edu/jupyter-installing-r-packages.html
	-Python packages: http://nero-docs.stanford.edu/anaconda_usage.html
	
Tips on working with PHS data:
-The export limit is 1 GB (though the size may change) - querying PHS data using the API from Nero counts as an export! This means that you cannot query most of the original tables in Optum (or other datasets) as they are usually >1 GB
-Two possible solutions are: 
i) you can request an exemption to the export size (there's a button in the upper right corner of the Redivis GUI) - I had no issues getting these quickly approved so long as I clarified that I was requesting the exemption to query the tables from Nero (and NOT to export data >1 GB onto my local machine)
ii) you can create smaller tables in the Redivis GUI and query those
-If you're using the BigQuery API, it is much faster to do data processing/cleaning via SQL commands since BigQuery is optimized for speed. Doing larger queries, converting the result to a dataframe, and then doing data processing is much slower
