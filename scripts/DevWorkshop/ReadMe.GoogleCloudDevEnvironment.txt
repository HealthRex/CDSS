= Dev Workshop =
Google Cloud and Compute Instance Setup

== Learning Goals ==
- Setting up Google Cloud Compute Instances
    - SSH GCloud
    - Setting up Linux Instance
- Running queries on Linux server
    - Process management to allow process to keep running in background while logged off
    - (nohup command &> logFile &)
- Parallel and Batch Processes
    - Importing medinfo

== Preconditions ==
- Google Stanford Account with VPN setup
- Project Permissions
- Service Account with Access Permissions to BigQuery Databases

== Workshop Steps ==
=== Starting from blank Compute Engine and Connecting to BigQuery ===
- Login to the Google Cloud Platform
  - Make sure connected as your stanford.edu account
  - Pick the correct GCP Project (Mining-Clinical-Decisions depending on access needed)
  (See prior workshop on VPN access if needed)

- Select "VM instances" under "Compute Engine" section in left-side dropdown under "COMPUTE"

- Startup a Compute VM Instance
    - Click on Create Instance button in top bar under header
	- Name
  	- Name your instance: For example, username or last name first letter initial for workshop. ie. chiangj
        - Region
            - Geographic location where  you run your instance
            - Decreased Network Latency
                - Choose a region close by to reduce latency, but more important is just to be consistent (e.g., us-west1-b)
  		 - Zone
    		    - As above, pick a consistent zone so all of your servers spawn in the same place
     - Series
     	- select N1 for  workshop
     	- type of server processor
     
     - Machine type
	     Can be customized in 'Machine type' dropdown under custom.
             Otherwise select a compute instance that fulfills your needs
	     - select n1-standard1 for workshop.
	     - different machines types cost different amounts based on compute  power  (ram, processor, etc)

		For testing purposes we can use n1-standard
            	With heavy computing, you can pick a server with more CPUs and more RAM
        - Boot Disk
            Allows you to change the Operating System
        
	OPTIONAL: 
          ??? Define / describe what a snapshot / image is
          Store a compute engine snapshot and restore 
              - Under Compute Engine (left) Go to disks (dropdown)
              - Go to create snapshot
                - you  will see a dropdown of your Instances
                - on the right you will see actions
                  - hit  "Create Snapshot"
                  - name your snapshot (i.e based on your vm instance)
                  - source  disk represents the  vm you are  snapshotting
              - then make snapshot from that  instance
              - Under Compute  Engine (left)  go to snapshot
                - here we can  create an instance with more/less/same  compute as  before with the  same file  directories as  			  your instance
                - steps will be the same as creating an instance


	
	- **Identity and API access**
	    - Select 'mining-clinical-dev' in dropdown. This gives read/view access and create job access
		    This is the most important for accessing BigQuery. You should have
		    access to a service account that has the BQ enabled.
		    (	???Explain sErvice account is a permissions method to enable compute instances to access BigQuery databases without requiring individual login key file (thought that is an option to). For further information... what is an IAM role and API...

		    	???Skip or otherwise replace this, because may not work in the som-nero-phi-jonc101 environment anyway. Users can't acceess IAM page, and may have to use an alternative to API service accounts unless SRCC offers alternative

			    Under service account there should be a dropdown of different APIs
			    you can access. Subsequently the API you select
			    should have your IAM role access determined (read, write)
			)
    - Create
        - then you can create your instance

-- ACCESSING YOUR  INSTANCE:

  -  Gcloud SSH versus Browser:
     - SSH key is an access credential in the SSH protocol for VM/instances  (like a login/password)

    - Access with SSH/Browser
      - Click ssh on the right of your instance name
      - Can Download and upload files with GUI
      - No other installation required (very convenient)
      - Connecting may be  a little slower depending on  number of vms and identifying ssh keys 

    - Access with gcloud/SSH
      - You may use gcloud instead of the SSH browser provided on the google console window. This allows you to use
        the terminal on your system.
      - automatic generation of ssh keys 

	    - Precondition:
	  		- requires gcloud installation (see devworkshop???Change to specific name or a link to the other workshop???)
	  		- Access on SSH
	  			1) gcloud init
				2) pick configuration (typically 1)
				3) choose  account (stanford account)
				4) pick a cloud project (mining-clinical-decisions)
				5) select region associated with instance
	  			6) gcloud compute ssh <name-instance>

    - How to upload and download files to your compute instance (i.e., SCP)
    	- Using SSH/Web Browser client
    		- Top right corner of window has a Gear icon with a Upload and Download file option
    		???Worth explaining or offering a concrete example, because people will get confused on what path to specify when trying to download a file.
    		(e.g., specifying home directory: "/home/yourUserName/fileName")

    	- Using gcloud / command-line 
		gcloud compute scp yourLocalFile.txt <instance-name>:/home/yourID/yourRemoteFileCopy.txt

            (where instance-name is the name of your instance)

	- Install Libraries and Dependencies / Package Managers
		(???Make descriptions a little more self-sufficient so that a user could in theory go through the entire workshop by themselves, without external guidance. For example, here separate what the intent of the step is, why it's necessary, and then call out what the explicit command line execution steps to enter...???

		???Worth a brief blurb to explain to uninitiated users, what is sudo, apt, git, PIP, pandas???)
            Installs  Dependencies: Python/Bigquery
            Installs Python dependencies 
            Install  Git for  Version Control

    	  sudo apt update
    		sudo apt install git
    		wget https://bootstrap.pypa.io/get-pip.py
    		sudo python3 get-pip.py
    		pip install google-cloud-bigquery
    		pip install pandas

	- Download Copy of Application Code Repository
		    git clone https://github.com/HealthRex/CDSS.git

  - Export PythonPath to use medinfo module (linux)
  	??? Worth a little explanation here about how Python finds local code modules and packages to import.
  	There is also a teaching opportunity here about use of environment variables, like the PYTHONPATH to have people access and setup their dev environment...
  	Try copying back from AWS Dev starter workshop
  	???
       export PYTHONPATH=/[your_directory]/CDSS/
       (can use 'pwd' to get path attributes)

       ???Next examples should actually import modules from the code tree to illustrate and confirm that works...???

	- Run Sample Scripts for Reading Data from BigQuery
            in your virtual environment: run this script from CDSS repo
            the script makes a connection to sample datalake ???Define where this came from???, makes a big query job that reads from the order_proc table
            and converts it to and prints out a dataframe
                python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read.py

        - Passing SQL Arguments to Read Data from BigQuery
            in your virtual environment: run this script from CDSS repo
                python3 CDSS/scripts/DevWorkshop/GoogleCloudPlatform/instance_read_arg.py SELECT jc_uid, order_type, description FROM datalake_47618_sample.order_proc

== Testing and Running (Batch) Processes ==
On GCP Linux Server:

  ????Add command line option to sleep_loop to illustrate able to input, and lead with example that dodes not require Ctrl+C to exit...??
  ???Earlier, I would tell peoiple to "cd" to the GoogleCLoudPlatform devworkshop folder, so they don't have to retype that every time...???
  - First run this command to see the expected print. It will just print out a progress indicator every second for N iterations.
      python3 -u CDSS/scripts/DevWorkshop/GoogleCloudPlatform/sleep_loop.py 10
       (This should print out a progress indicator and finish after 10 seconds)

  - Run the command again, but with a different option, where it will take a long time and you will want to hit Ctrl+C after starting to finish...???
      python3 -u CDSS/scripts/DevWorkshop/GoogleCloudPlatform/sleep_loop.py 1000
       (This should print out a progress indicator and would finish after 1000 seconds, but you can just Ctrl+C to quit it, while we now examine how you might manage long compute processes)


- Run this next version of the command, but run the process in the background (ending &) and continue even if you logoff (nohup = "no hangup").
  So you can start a long process and just let the server continue to work on it,
  without requiring you to keep your (laptop) client computer logged in.
  Any error messages, progress indicators, or other text that you normally see in the console
  window will be redirected (&>) to the specified log file (progress.log)

      nohup python3 -u sleep_loop.py 1000 &> progress.log &

- Check on the progress of the process you have running in the background
    `ps -u`
	`ps -u USER -f`
        USER will be replaced with your google user name  or user name associated  with the compute instance
		Checks which processes are running under the USER, with full details. Note the Process ID (PID)
	`kill <PID>`
		If you need to kill/stop a process that you don't want to continue anymore
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
	`cat process.log`
		Show the output of the redirected console output from your application process
	`tail -f process.log`
		Show just the last few lines of the redirected console output,
		and continue watching it until Ctrl+C to abort.
		(Ctrl+C will abort the "tail" monitoring process, not the original application process.)


- Section on running serial and parallel processes using simple scripts.

- Running a batch script in  the background 
	If you have a series of python scripts  you  would like to run in the  background  you can create a bash script  and  follow a similar  template  as 'batch_read.sh' 
	This would  be effective for reads that you may have to do step by step (1,000,000 rows at a time) 

  	cd /[PATH_TO_DIRECTORY]/CDSS/scripts/DevWorkshop/GoogleCloudPlatform/batch
  	bash ./batch_read.sh


?????Instead of instance_read, and sleeper_loop, and cloud_read....
?????Make a single little program, "ExampleQueryApp" (GCP version)
Functions it should have are:
- Takes command line argument of a pause duration (default to 0 seconds) between outputting results
- Takes command line argument of a order description prefix 
- Needs to take another commandline argument which specifies what file to output to
- It should then query an example database in GCP BigQuery (e.g., starr_datalake2018)
  Look for the top 100 order_med med_descriptions whose description starts with the given prefix
  Then output each of those descriptions found and their count, output by printing to output file one line at a time.
      Pausing for the pause duration (i.e., sleep) between each result output print
  