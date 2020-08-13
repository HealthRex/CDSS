


1) PHS Access to Restricted Datasets:
2) (Optional) Install Cardinal Key:
	- a digital certificate that is installed on a device and provides a user’s
		identity to a remote server in place of a SUNet ID and password
	- https://phsdocs.developerhub.io/software-installation/cardinal-key
3) Sign up for PHS Data Portal Account
	 	- Go to https://redivis.com/StanfordPHS/ and click on create account
			- additional information:
			- https://phsdocs.developerhub.io/computing-environment/quick-tour-phs-data-portal
5) Getting Access to Dataset:
	- a) apply for permissions
	- b) Levels of Access:
		- overview access
		- metadata access
		- data access
	- c) Go to https://redivis.com/StanfordPHS/datasets
	- d) Select Data Access on Restricted Datasets you want access to
	- e) Complete steps for metadata access and data access
		- typically training
		- encryption verification
		- study approval: HealthRex and Diagnostics has already been approved

		Once access granted, can "Add Dataset" to "Projects" which will bring to Redivis graphical tree view to query 1% or 100% data samples
		Not allowed to download data or results from here, but enough to query and review high level reports.

		Can hack together queries through graphical interface, or click on code symbol button ("</>") to enter direct SQL queries.
		Add a "Transform" to a table of interest, which is basically a SQL query that can be custom edited and run, to generate a new Table of results.
		For large databases, note the different between full database and 1% sample (suffix ":sample" to the table name)



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


Accessing PHS Data through Nero Compute:

1) GO TO: nero.compute.stanford.edu
	- make sure your stanford vpn is on
	- https://nero-docs.stanford.edu/jupyter.html
2) Open a terminal under 'Other'
3) git clone https://github.com/redivis/redipy.git
4) export PYTHONPATH='/home/[SUNETID]/redipy'
5) cd redipy/bigquery/
6) enter python console: type python
7) in python:
	import os
	from redivis import bigquery 
	import pandas
	os.environ['REDIVIS_API_TOKEN'] = "[TOKEN_FROM_REDIVIS]"
	client=bigquery.Client()
	# Perform a query.
	# Table at https://redivis.com/StanfordPHS/datasets/1411/tables
	QUERY = ('SELECT * FROM `jichiang.optum_access_test:1.top_10_diabetes_lab_tests:12`')
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
