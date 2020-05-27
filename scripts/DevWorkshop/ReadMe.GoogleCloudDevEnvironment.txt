= Dev Workshop =
Google Cloud and Compute Instance Setup

== Learning Goals ==
- Setting up Google Cloud Compute Instances
    - SSH remote connections + public-private key security
    - Setting up a Linux Instance
- Running queries on Linux server
    - Process management to allow (parallel) processes to keep running in background while logged off
    - (nohup command &> logFile &)

== Preconditions ==
- Google Stanford Account with VPN setup
- Project (mining-clinical-decisions) Permissions
  (See ReadMe.GoogleCloud-BigQuery-VPC.txt DevWorkshop)

== Workshop Steps ==
=== Setting up a Compute Engine Instance from Scratch ===
- Login to the Google Cloud Platform
    https://console.cloud.google.com/home/dashboard?project=mining-clinical-decisions&authuser=1
  - Make sure connected as your stanford.edu account
  - Pick the correct GCP Project on the top nav bar ([Mining Clinical Decisions] depending on access needed)

- Top Left Menu > [Compute Engine] > [VM instances]

- Startup a Compute VM Instance
  - [Create Instance] under the top nav bar header
    - Name
    - Region: A region close by can reduce network latency, but more important is consistency (e.g., us-west1-b)
    - Zone: As above, pick a consistent zone so all of your servers spawn in the same place
    - Machine Configuration: What type of hardware do you want to use
      - Series + Machine Type
        Different machines types cost different amounts based on how many CPUs and RAM you need
        For testing purposes, just pick choose one of the smallest ones (e.g., N1 - f1-micro)
    - Boot Disk: Allow specification of different default Operating Systems (default Debian GNU/Linux for now)
  	- Identity and API access
	    If you want the compute instance to have specific access privilieges.
      Select 'mining-clinical-dev' for simplicity for now, as this gives read/view and create job access
      against the BigQuery databases through a Service Account 
      without requiring individual login key files (though that is an option too).
    - Create

- Accessing your Compute Instance:
  SSH secure shell terminals allow for secure encrypted command-line access to computers
  This requires SSH public-private key pairs or a login/password (though the latter is not as secure)

  - Option 1 - Using the browser based SSH client
    - Find the compute instance you created under Compute Engine > VM Instances
    - Click the [SSH] Connect option to the right of your instance name
      This should spawn a terminal console window that logs you into the 
      home directory of a Linux server where you can interactively enter shell commands (e.g., ls, mkdir, pwd)

  - Option 2 - Using gcloud/SSH command-line tools
    Requires gcloud installation (see ReadMe.GoogleCloudDevEnvironment.txt DevWorkshop)
  	From your local command-line terminal/console:
			
      gcloud init
			- Pick configuration (typically 1)
			- Choose account (stanford.edu)
			- Pick a cloud project (mining-clinical-decisions)
			- Select the region associated with instance (optional)
			
      From the browser VM list, look under the other menu options after the [SSH] default Connect option, 
      including the gcloud command line option. This should an SSH terminal console to the compute instance.
      You should get a warning about the authenticity of the server/host not being established.
      This makes sense since you've never connected to this server before, and you could be the
      subject of a "man-in-the-middle" attack. Just agree to the connection for test/dev purposes,
      but for real applications with security risks, you should authenticate the server by other channels.

        gcloud compute ssh <instanceName>

- Install Libraries and Dependencies / Package Managers
  You'll need software packages and dependencies installed on the compute instance for development work
  Default system comes with both Python 2.7 and Python 3.7 installed (latter as "python3") (as of 5/26/2020),
  but is largely barebones in terms of other software packages. Using package management software tools,
  such as apt and pip in this case, are essentially for easing the pain of "dependency hell."

  Run the following commands to install several dependencies:

    sudo apt update                               # Tell the "superuser" admin to "do" an update of the apt tool
    sudo apt install git                          # Git client to communicate with source code version control repository
    sudo apt install python3-pip                  # Install PIP tool for Python package management
    python3 -m pip install google-cloud-bigquery  # Python - Google Cloud interface to connect to BigQuery databases
    python3 -m pip install pandas                 # Popular Python package for manipulating tabular dataframes

- Download a Copy of the Application Code Repository
	
  git clone https://github.com/HealthRex/CDSS.git

- Setup PYTHONPATH so Python knows where to find Application Code
  Enter the following shell command to create/update a PYTHONPATH shell environment variable
  to tell Python where to look for code package and module imports beyond the current working directory.

    export PYTHONPATH=/home/yourUserName/CDSS:$PYTHONPATH

  Or wherever you put the CDSS directory. Followed by a $ reference to any existing $PYTHONPATH 
  so if you already had anything set, you'll copy the prior value and just preprend your additions here.
  Better yet, append the command to the .bash_profile script:

    echo "export PYTHONPATH=/home/yourUserName/CDSS:$PYTHONPATH" >> .bash_profile

  Or use a Unix text editor to edit the profile script (`vi /home/yourUserName/.bash_profile`)
  The .bash_profile script (the . prefix indicates a hidden system file you can find with `ls -la`)
  will run every time you connect to the server, or you can direct invoke it with:

    source .bash_profile


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
      python programs you want to run.
    - We will be using cloud_read.py which is a python script that converts a sql query from BigQuery into rows of output
      on the command line. It accepts three arguments that you can change.
    - First change the directory

  	   cd batch/

    - the first argument is the delay time in seconds (1) between result outputs
    - the second argument is the letter to query (a)
    - the third argument is the number of rows to output (5)

        python cloud_read.py 1 a 5

    - Feel free to change the arguments and see how the output changes

    - Then you can run 'cloudDriverScript.py' which is a script that creates a python batch file.
    - The 'cloudDriverScript.py' creates a shell script (A shell script is a computer program that runs on the command line interpreter)

        python cloudDriverScript.py

    - The cloud_log.sh file that is created is a shell script that includes batch python scripts, that builds off of the cloud_read.py
    - It outputs the first 100 rows of med descriptions, for each letter  of the alphabet, giving 26 different log files.

      bash cloud_driver.sh

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
                  - here we can  create an instance with more/less/same  compute as  before with the  same file  directories as
                       your instance
                  - steps will be the same as creating an instance



- Notes on How to Upload/Download any File
  - Option 1 - Using SSH/Web Browser client
    - Top right corner of window has a "Gear" icon with a Upload and Download file option
    - To download specify your path and file you wish to download: for example:
      - ("/home/yourUserName/CDSS/scripts/DevWorkshop/ReadMe.GoogleCloudDevEnvironment.txt")
    - To upload:
      - select 'Upload file' and select the file you wish to upload to the current working directory

  - Option 2 - Using gcloud from you local command-line console to simulate an SCP (secure copy) command
    
    gcloud compute scp yourLocalFile.txt <instance-name>:/home/yourUserName/yourRemoteFileCopy.txt


