


1) PHS Access to Restricted Datasets: 
2) Install Cardinal Key: 
	- https://phsdocs.developerhub.io/software-installation/cardinal-key
3) Sign up for PHS Data Portal Account 
4) Go to https://redivis.com/StanfordPHS/ and click on create account 
		- additional information: 
			-  https://phsdocs.developerhub.io/computing-environment/quick-tour-phs-data-portal
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


Creating API credentials: 
https://redivis.com/workspace/settings
- Scroll down to API tokens: 
- Generate new token 
- Select all access measures(all boxes): Public, Data, Organization: including edit/read
- Save token to a file somewhere secure for reference later:


Prereq: 
	Stanford Sunet: 
	PI emails srcc-support@stanford.edu for Nero Account
		- https://nero-docs.stanford.edu/user-prerequisites.html#submit-request-for-nero-account

1) GO TO: nero.compute.stanford.edu 
	- make sure your stanford vpn is on
	- https://nero-docs.stanford.edu/jupyter.html
2) On top bar, click on: 'Help'
3) 'Launch Classic Notebook'
4) On Upload and New tabs click: 'New'
5) Click 'noVNC Desktop'
6) Click 'Connect'
7) Open Terminal Emulator on below toolbar 
7) git clone https://github.com/redivis/redipy.git
8) export PYTHONPATH='/home/[SUNETID]/redipy'
9) cd redipy/bigquery/
10) enter python console: type python
11) in python: 
	import os 
	from redivis import bigquery 
	import pandas
	client=bigquery.Client()
	
	os.environ['REDIVIS_API_TOKEN'] = "[TOKEN_FROM_REDIVIS]"
	# Perform a query.
	# Table at https://redivis.com/StanfordPHS/datasets/1411/tables
	QUERY = ('SELECT * FROM `stanfordphs.commuting_zone:v1_0.life_expectancy_trends` LIMIT 10')

	df = client.query(QUERY).to_dataframe()  # API request

	print(df)
