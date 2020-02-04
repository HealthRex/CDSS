= Dev Workshop =
Google Cloud and Compute Instance Setup

== Learning Goals ==
- Setting up Google Cloud Compute Instances
    - SSH GCloud
    - Setting up Linux Instance
- Running queries on Linux server
    - Process management to allow process to keep running in background while logged off
    - (nohup command &> logFile &)

== Preconditions ==
- Google Stanford Account with VPN setup 
- Project Permissions 
- Service Account with Access Permissions to BigQuery Databases 

== Workshop Steps ==
=== Starting from blank Compute Engine and Connecting to BigQuery ===
- Login to the Google Cloud Platform
  - Make sure connected as your stanford.edu account
  - Pick the correct GCP Project - Mining-Clinical-Decisions depending on access needed)
  (See prior workshop on VPN access if needed)

- Select "VM instances" under "Compute Engine" section in leftside dropdown under "COMPUTE"

- Startup a Compute VM Instance	
    - Click on Create Instance button in top bar under header 
	- Launch Instance
		- Name:
			????Compute Instances is also possible here if you did a lot of custom configuration, 
			but here we want to illustrate how to get going from a "blank" instance
			((((Can create off a prior image, but here show example of starting from blank))))
			????
			???Could name it after yourself and purpose, so know to keep track and delete later???
        - Region
            ???
            - Decreased Network Latency 
                - Choose a region close by to reduce latency, but more important is just to be consistent (e.g., us-west1-b)
            ????- Handling failures
                - must choose different regions if using multiple instances to avoid outages
                ((((This would be more if building a large fault-tolerant system that shoudl keep running even if some parts go down))))
                ???
		 - Zone???
			- As above, pick a consistent zone so all of your servers spawn in the same place
		 - Machine type
			Can be customized in 'Machine type' dropdown under custom. 
			Otherwise select a compute instance that fulfills your needs  

			For testing purposes we can use n1-standard  
            		With heavy computing, you can pick a server with more CPUs and more RAM.
        - Boot Disk
            Allows you to change the Operating System 
            ???Later show option to store a compute engine snapshot and restore here???

	 - Machine Configuration
		- Most defaults are fine.
		???Not sure what specific this is referring to???

	- **Identify and API access**
	    - Select 'mining-clinical-dev' in dropdown. This gives read/view access and create job access  
		    This is the most important for accessing BigQuery. You should have 
		    access to a service account that has the BQ enabled. 
		    Under service account there should be a dropdown of different APIs 
		    you can access. Subsequently the API you select 
		    should have your IAM role access determined (read, write)
    - Create 
        - then you can create your  instance
    
-- ACCESSING YOUR  INSTANCE: 
	???Different options to establish an SSH terminal connection to the compute instance / server:...
	???What's the relative advantage/disadvantage of each of these???

    - Access with SSH/Browser
    	- Click ssh on the right of your instance name 

    - Access with gcloud/SSH 

    ???????????????????????????????????????
    ???????????????????????????????????????
    ???????????????????????????????????????
    ???????????????????????????????????????
    ???????????????????????????????????????
    	- Precondition: 
		-  requires gcloud installation (see devworkshop) 
		- Access on SSH 
			1) gcloud init 
			2) pick configuration (typically 1) 
			3) choose  account (stanford account) 
			4) pick a cloud project (mining-clinical-decisions)
			5) gcloud compute ssh name-instance 
			6) select region associated with instance 
			
	    	- scp a file 
			- 'gcloud compute scp ~/Downloads/your_file.txt \instance-name:~/your_file.txt'
				(where instance-name is the name of your instance)  
        
	- SSH Connection ???Redundant with prior step
            Once you start the compute instance, you may remote access with SSH.  
            'Open in browser window'  

	- Install Libraries and Dependencies / Package Managers
            Installs  Dependencies: Python/Bigquery
            -- Creates  Virtual Environment ???Remove unless pseicifcally necessary to minimize number of steps and dependencies to keep track of
            Installs Python dependencies in virtual environment 
            Install  Git for  Version Control 

	    sudo apt update
		sudo apt install git
		sudo apt install python3 python3-dev python3-venv
		wget https://bootstrap.pypa.io/get-pip.py
		sudo python get-pip.py
		-- python3 -m venv venv
		-- source venv/bin/activate
		pip install google-cloud-bigquery
		pip install pandas
		-- mkdir results
		-- mkdir log
	    
	- Download Copy of Application Code Repository
		    `git clone https://github.com/HealthRex/CDSS.git`
	    
	- Run Script for Reading Data from BigQuery 
            in your virtual environment: run this script from CDSS repo
            ????Add some description of what people should expect, what is it this example is doing????
                `python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py`

        - Passing SQL Arguments to Read Data from BigQuery 
            in your virtual environment: run this script from CDSS repo
                'python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read_arg.py SELECT jc_uid, order_type, description FROM datalake_47618_sample.order_proc'

            ???Looking more for examples where can import modules from medinfo rather just local scripts... Really best example would be to update DBUtil interface so can work in this interface as well....????

== Testing and Running (Batch) Processes ==
On GCP Linux Server:

????Add- Run a long script first... run sleeper example, but change it so it's a for loop that just prints a line or dot every 1 second, so people can see what it looks like and see that it's not idling, but it will take a long time to finish


- Run the process again, but do so in the background
	`nohup python3 -u CDSS/scripts/DevWorkshop/GoogleCloudPlatform/sleeper_1000.py  &> log/progress.log &
`
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


Section on running serial and parallel processes using simple scripts.
Then snapshoting the server and restarting it or reconfiguring it to use multiple CPUs and RAM.

