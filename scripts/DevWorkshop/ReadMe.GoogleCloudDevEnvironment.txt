= Dev Workshop =
Google Cloud and Compute Instance Setup

== Learning Goals ==
- Setting up Google Cloud Compute Instances
    - SSH remote connections + public-private key security
    - Snapshot management
    - Elastic compute scales + hourly billing
    - Setting up Linux server dev environment from scratch / base image
- Running batch queries on Linux server
    - Process management to allow for multiple parallel queries or allow process to keep running in background while logged off
    - (nohup command &> logFile &)

== Preconditions ==
- Google Stanford Account with VPN setup 
- Project Permissions 
- Service Account with Access Permissions to BigQuery Databases 

== Workshop Steps ==
- Login to the Google Cloud Platform and then find Compute Engine in leftside dropdown 

=== Version A - Starting from blank Compute Engine and Connecting to BigQuery ===

- Startup / Restore an RDS (Relational Database Server) Instance
	Under VM instances select CREATE INSTANCE

	- Actions > Restore Snapshot
		Most default options are fine
		- DB Instance Class
			Specify how "big" a server you want. For testing, N1 series is good enough
		- DB Instance Identifier
			Specify a unique name so you will be able to track the instance you created
		- Availability Zone
			Specific choice is not as important as being consistent 
			(Keep all your spawned servers in the same area to minimize network latency and security risks). 
			I've usually been using "us-east-1c."

- Startup a Compute VM Instance
	These are general purpose (Linux) servers that can basically do whatever you want them to 
	(Including running relational databases, if you don't need the convenience of the RDS setup).
	
	- Launch Instance
		- Pick the Compute VM Image to start from
			Compute Instances is also possible here if you did a lot of custom configuration, 
			but here we want to illustrate how to get going from a "blank" instance
		- Choose an Instance Type
			For testing purposes, a f1-micro instance should again be good enough. I've been using n1-standard.
			If subsequently going to be doing some heavy computing, then pick a server with more CPUs and more RAM.
		- Configure Instance Details
			Most defaults are fine.
			- Subnet / Availability Zone
				As above, pick a consistent zone so all of your servers spawn in the same place
		- Add Storage
			Can be customized in 'Machine type' dropdown under custom. Otherwise select a compute instance that fulfills your needs  
        - Boot Disk
            Allows you to change the Operating System 
		- **Identify and API access**
			This is the most important for accessing BigQuery. You should have access to a service account that has the BQ enabled. 
            Under service account there should be a dropdown of different APIs you can access. Subsequently the API you select 
            should have your IAM role access determined (read, write)
		- Firewall
			By default all incoming traffic from outside a network is blocked. 
        - Starting an Instance
            Once you create your instance you select the instance and hit Start 
		- SSH Connection
            Once you start the compute instance, you may remote access with SSH.  I typically use 'Open in browser  window' (may not be  best practice) 

		- Install Libraries and Dependencies / Package Managers
            Installs  Dependencies: Python/Bigquery
            Creates Directory 
            Creates  Virtual Environment
            Installs Python dependencies in virtual environment 
            Install  Git for  Version Control 
                For  steps 6 and 7 you  may change then name of your bq project

			      1  sudo apt update
            2  sudo apt install python3 python3-dev python3-venv
            3  wget https://bootstrap.pypa.io/get-pip.py
            4  sudo python get-pip.py
            5  mkdir bq_project
            6  cd bq_project/
            7  python3 -m venv venv
            8  source venv/bin/activate
            9  pip install google-cloud-storage
            10 pip install google-cloud-bigquery
            11 pip install pandas
            12 sudo apt install git-all

		- Download Copy of Application Code Repository
		    `git clone https://github.com/HealthRex/CDSS.git`
	    
	    - Run Script for Reading Data from BigQuery 
            cd into `CDSS`
            in your virtual environment: run this script from CDSS repo
                `python3 scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py`
      - Passing SQL Arguments  to Read Data from BigQuery 
          in your virtual environment: run this script from CDSS repo
              'python3 scripts/DevWorkshop/GoogleCloudPlatform/instance_read_arg.py SELECT jc_uid, order_type,  description FROM datalake_47618_sample.order_proc'

