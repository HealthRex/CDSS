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
    - Shell Scripting

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

	- Identity and API access
	    - Select 'mining-clinical-dev' in dropdown. This gives read/view access and create job access
		    This is the most important for accessing BigQuery. You should have
		    access to a service account that has the BQ enabled.
		    (Service accounts are different levels of permissions to access data in bigquery
        is a permissions method to enable compute instances to access BigQuery databases
        without requiring individual login key file (though that is an option too).

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
	  		- requires gcloud installation (see GoogleCloudDevEnvironment.txt devworkshop)
	  		- Access on SSH
	  			1) gcloud init
  				2) pick configuration (typically 1)
  				3) choose  account (stanford account)
  				4) pick a cloud project (mining-clinical-decisions)
  				5) select region associated with instance
	  			6) gcloud compute ssh <name-instance>



    	- Using gcloud / command-line
		      gcloud compute scp yourLocalFile.txt <instance-name>:/home/yourID/yourRemoteFileCopy.txt

            (where instance-name is the name of your instance)

	- Install Libraries and Dependencies / Package Managers

      - The following steps ensure that you have the proper packages installed in python as well the proper
          linux dependencies installed.
      - Unix based operating systems use 'sudo' commands as a superuser command.
          This means that your command acts as the admin and may require a password to use.
      - 'apt' acts a  command line interface for linux distribution commands. Typically system wide installations or changes
          will be prefaced by  'sudo apt ...'
      - 'git' acts as the way to communicate with out repository to maintain our code.
      - 'pip' is the python package manager command and helps to install python modules
      - 'pandas' is a very popular python package used to manage dataframes in a more user friendly way,
          which is helpful for interfacing with tabular EHR data in a python and analytical environment

            - Installs Dependencies: Python/Bigquery
            - Installs Python dependencies
            - Install  Git for  Version Control

        sudo apt update
        sudo apt install git
        wget https://bootstrap.pypa.io/get-pip.py
        sudo python get-pip.py
        pip install google-cloud-bigquery
        pip install pandas

	- Download Copy of Application Code Repository
		    git clone https://github.com/HealthRex/CDSS.git

  - How to upload and download files to your compute instance (i.e., SCP)
  	- Using SSH/Web Browser client
  		- Top right corner of window has a Gear icon with a Upload and Download file option
      - ("/home/yourUserName/CDSS/scripts/DevWorkshop/ReadMe.GoogleCloudDevEnvironment.txt")


  - Python Modules and Exporting PythonPath to use medinfo module (linux)

      - The import statement combines two operations; it searches for the named module, then it binds the results of that search to a name in the local scope.
      - When a module is first imported, Python searches for the module in the current path and if found, it creates a module object 1, initializing it.
      - If the named module cannot be found, a ModuleNotFoundError is raised.
      - Python can look for modules in the PYTHONPATH
      - use (can use 'pwd' to get path attributes [your_directory])

            export PYTHONPATH=/[your_directory]/CDSS/

      - then type in 'python' in the command line to open the python shell
             python
      - import medinfo to confirm you can import the CDSS modules
             >>> import medinfo

      - Exit out of python shell
             >>> quit()

      - Change your directory to the devworkshop in our repo

            cd CDSS/scripts/DevWorkshop/GoogleCloudPlatform


== Testing and Running (Batch) Processes ==
On GCP Linux Server:


  - First run this command to see the expected print.
  - Prints out a progress indicator every second for N iterations. (This should print out a progress indicator and finish after 10 seconds)

        python sleep_loop.py 10

  - Run the command again, but with a different option, where it will take a long time
    and you will want to hit Ctrl+C after starting to finish

        python sleep_loop.py 1000

  - (This should print out a progress indicator and would finish after 1000 seconds, but you can just Ctrl+C to quit it,
     while we now examine how you might manage long compute processes)


- Running Background Processes

  - Run this next version of the command, but run the process in the background (ending &) and continue even if you logoff (nohup = "no hangup").
  - So you can start a long process and just let the server continue to work on it, without requiring you to keep your (laptop) client computer logged in.
  - Any error messages, progress indicators, or other text that you normally see in the console window will be redirected (&>)
    to the specified log file (progress.log)

      nohup python -u sleep_loop.py 1000 &> progress.log &

  - to see progress.log updates use the 'cat' command which in this case can display text files on screen

      cat progress.log

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

- Running a batch script in the background
  	- If you have a series of python scripts you would like to run in the background you can create a shell script of
      python scripts.
    - This would be effective for reads that you may have to do step by step (1,000,000 rows at a time).
    - We will be using cloud_read.py which is a python script that converts a sql query from BigQuery into rows of output
      on the command line. It accepts three arguments that you can change.
    - First change the directory

  	   cd batch/

    - the first argument is the time in seconds (1)
    - the second argument is the letter to query (a)
    - the third argument is the number of rows to output (5)

        python cloud_read.py 1 a 5

    - Feel free to change the arguments and see how the output changes

    - Then you can run 'cloud_write.py' which is a script that creates a python batch file.
    - The 'cloud_write.py' creates a shell script (A shell script is a computer program that runs on the command line interpreter)

        python cloud_write.py

    - The cloud_log.sh file that is created is a shell script that includes batch python scripts, that builds off of the cloud_read.py
    - It outputs the first 100 rows of med descriptions, for each letter  of the alphabet, giving 26 different log files.

      bash cloud_log.sh

    - The cloud_log.sh file gives a template for writing scripts or programs that may a take a long time to run,
    - runs in the background, while recording the progress and outputs as they occur.
    - If a process is taking too long or your dataset increases in size. You may think about increasing your compute on the instance.

- SNAPSHOTS
  	OPTIONAL LEARNING (Useful when you need more/less compute or want to backup your VM):
            provide a mechanism to create one or a series of persistent disk backups,
            each at a specific point-in-time. Snapshots are stored as differential captures of the actual data on a persistent disk,
            using storage space efficiently.

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
