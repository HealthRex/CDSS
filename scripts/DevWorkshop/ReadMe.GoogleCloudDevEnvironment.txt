= Dev Workshop =
Google Cloud and Compute Instance Setup

== Learning Goals ==
- Setting up Google Cloud Compute Instances
    - SSH remote connections + public-private key security
    - Setting up Linux Instance
- Running queries on Linux server
    - Process management to allow process to keep running in background while logged off
    - (nohup command &> logFile &)

== Preconditions ==
- Google Stanford Account with VPN setup 
- Project Permissions 
- Service Account with Access Permissions to BigQuery Databases 

== Workshop Steps ==
=== Version A - Starting from blank Compute Engine and Connecting to BigQuery ===
- Login to the Google Cloud Platform
  - Make sure connected as your stanford.edu account
  - Pick the correct GCP Project - Mining-Clinical-Decisions depending on access needed)
  (See prior workshop on VPN access if needed)

- Select "VM instances" under "Compute Engine" section in leftside dropdown under "COMPUTE"

- Startup a Compute VM Instance	
    - Click on Create Instance button in top bar under header 
	- Launch Instance
		- Name:
			Compute Instances is also possible here if you did a lot of custom configuration, 
			but here we want to illustrate how to get going from a "blank" instance
        - Region
            - Handling failures
                - must choose different regions if using multiple instances to avoid outages
            - Decreased Network Latency 
                - choose a region close by 

		- Choose an Instance Type
			For testing purposes we can use n1-standard  
            		With heavy computing, you can pick a server with more CPUs and more RAM.
		- Machine Configuration
			Most defaults are fine.
		- Series
			As above, pick a consistent zone so all of your servers spawn in the same place
		- Machine type
			Can be customized in 'Machine type' dropdown under custom. 
			Otherwise select a compute instance that fulfills your needs  
        - Boot Disk
            Allows you to change the Operating System 
	- **Identify and API access**
	    This is the most important for accessing BigQuery. You should have 
            access to a service account that has the BQ enabled. 
            Under service account there should be a dropdown of different APIs 
            you can access. Subsequently the API you select 
            should have your IAM role access determined (read, write)
    - Firewall 
    - Create 
        - then you can create your  instace
    
-- ACCESSING YOUR  INSTANCE: 

    - Access with SSH/Browser 

    - Access with gcloud 
        
		- SSH Connection
            Once you start the compute instance, you may remote access with SSH.  
            I typically use 'Open in browser  window' (may not be  best practice) 

		- Install Libraries and Dependencies / Package Managers
            Installs  Dependencies: Python/Bigquery
            Creates Directory 
            Creates  Virtual Environment
            Installs Python dependencies in virtual environment 
            Install  Git for  Version Control 
                For  steps 6 and 7 you may change the name of your bq project

	        1  sudo apt update
            2  sudo apt install python3 python3-dev python3-venv
            3  wget https://bootstrap.pypa.io/get-pip.py
            4  sudo python get-pip.py
            5  python3 -m venv venv
            6  source venv/bin/activate
            7  pip install google-cloud-bigquery
            8  pip install pandas
            9  sudo apt install git
            10 mkdir results
            11 mkdir log
	    
	- Download Copy of Application Code Repository
		    `git clone https://github.com/HealthRex/CDSS.git`
	    
	- Run Script for Reading Data from BigQuery 
            in your virtual environment: run this script from CDSS repo
                `python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py`

        - Passing SQL Arguments to Read Data from BigQuery 
            in your virtual environment: run this script from CDSS repo
                'python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read_arg.py SELECT jc_uid, order_type, description FROM datalake_47618_sample.order_proc'

== Testing and Running (Batch) Processes ==
On GCP Linux Server:

- Run the process again, but do so in the background
	`nohup python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py &> log/progress.log`

	Above will run the process in the background (ending &) and continue even if you logoff (nohup = "no hangup"). 
	So you can start a long process and just let the server continue to work on it, 
	without requiring you to keep your (laptop) client computer logged in.  
	Any error messages, progress indicators, or other text that you normally see in the console 
	window will be redirected (&>) to the specified log file (log/progress.log)

- Check on the progress of the process you have running in the background
    `ps -u`
	`ps -u USER -f`
        USER will be replaced with your google user name  or user name associated  with the compute instance
		Checks which processes are running under the USER, with full details. Note the Process ID (PID)
	`kill <PID>`
		If you need to kill a process that you don't want to continue anymore
	`top`
		Running monitor of all the most intensive processes running on the server
		Overall reporting can track how much total free memory (RAM) the server still has available, 
		and how much processor (CPU) is being used. Helpful when trying to gauge the bottleneck for 
		intensive processes (need more processors or need more RAM?). 
		Note that total CPU load can be >100% for servers with multiple CPUs. 
		The whole point of using a multi-processor server is that you 
		should run multiple simultaneous (parallel) processes
		to take advantage of extra CPUs working for you. 
		You can't make a single process run at 200% speed with two CPUs, 
		but you can break up the work into two separate tasks, and have each running at 100% on separate CPUs.
		Beware that the multiple processors are both using the same shared memory (RAM), so if you have a process
		that uses a lot of RAM, parallelizing the process will also multiply the amount of total RAM needed.
		
		"M" to sort the results by which processes are using the most memory
		"q" to quit/exit when done.
	`cat log/process.log`
		Show the output of the redirected console output from your application process
	`tail -f log/process.log`
		Show just the last few lines of the redirected console output, 
		and continue watching it until Ctrl+C to abort.
		(Ctrl+C will abort the "tail" monitoring process, not the original application process.)
