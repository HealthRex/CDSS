= Dev Workshop =
Google Cloud and Compute Instance Setup

== Learning Goals ==
- Setting up Google Cloud Compute Instances
    - SSH remote connections + public-private key security
    - Snapshot management
    - Elastic compute scales + hourly billing
    - Setting up Linux server dev environment from scratch / base image
- Running batch queries on Linux server
    - Process management to allow for multiple parallel queries or allow process 
        to keep running in background while logged off
    - (nohup command &> logFile &)


[ ] 
[ ] 


== Preconditions ==
- Google Stanford Account with VPN setup 
- Project Permissions 
- Service Account with Access Permissions to BigQuery Databases 

== Workshop Steps ==
=== Version A - Starting from blank Compute Engine and Connecting to BigQuery ===
- Login to the Google Cloud Platform
  - Make sure connected as your stanford.edu account
  - Pick the correct GCP Project (e.g., som-nero-phi-jonc101 or Mining-Clinical-Decisions depending on access needed)
  (See prior workshop on VBPN access if needed)

- Go to Compute Engine section in leftside dropdown 

- Startup a Compute VM Instance
	These are general purpose (Linux) servers that can basically do whatever you want them to 
	
    - Click on Create Instance button in top bar...
	- Launch Instance
		- Pick the Compute VM Image to start from
			Compute Instances is also possible here if you did a lot of custom configuration, 
			but here we want to illustrate how to get going from a "blank" instance
		- Choose an Instance Type
			For testing purposes, a f1-micro instance should again be good enough. 
            		I've been using n1-standard. If subsequently going to be doing some heavy computing, 
            		then pick a server with more CPUs and more RAM.
		- Configure Instance Details
			Most defaults are fine.
		- Subnet / Availability Zone
			As above, pick a consistent zone so all of your servers spawn in the same place
		- Add Storage
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


???????????Vs. Having users upload login JSON key to identify themselves???????
???????Especially because som-nero-phi-jonc101 project, we don't have owner access to create API accounts anyway....
?????Would probably then be good for people to know about SCP file uploads as well?????
????THis probably means as a precondition, that they've already done the GoogleCloud-VPC Access Key workshop so they'll have they're own JSON ????

		- SSH Connection
            Once you start the compute instance, you may remote access with SSH.  
            I typically use 'Open in browser  window' (may not be  best practice) 

        	[[[[[[[[[[[[[[Figure out option for connecting with any SSH client]]]]]]]]]]]]]]


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
            5  mkdir bq_project
            6  cd bq_project/
            7  python3 -m venv venv
            8  source venv/bin/activate
            9  pip install google-cloud-storage
            10 pip install google-cloud-bigquery
            11 pip install pandas
            12 sudo apt install git-all
            13 mkdir results
            14 mkdir log


            [[[[[ Figure out what is minimum necessary dependency installation to just make demo process work]]]]]
        	[[[[[ See if simpler git install so doesn't require so much download and install ]]]]]

	- Download Copy of Application Code Repository
		    `git clone https://github.com/HealthRex/CDSS.git`
	    
	- Run Script for Reading Data from BigQuery 
            in your virtual environment: run this script from CDSS repo
                `python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py`

[[[[[[[[[[[Clarify if some kind of access crediential was necessary to make this step work]]]]]]]]]]]

        - Passing SQL Arguments to Read Data from BigQuery 
            in your virtual environment: run this script from CDSS repo
                'python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read_arg.py SELECT jc_uid, order_type, description FROM datalake_47618_sample.order_proc'

== Testing and Running (Batch) Processes ==
On GCP Linux Server:

- Run the process again, but do so in the background
	`nohup python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py &> log/progress.log &`


[[[[[[[[[[[[Add back example where the compute/query process takes a while, adding back option parser and time delay between results]]]]]]]]]]]]
[[[[[[[[[[[That way people can learn about running a process in the background...]]]]]]]]]]]

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

