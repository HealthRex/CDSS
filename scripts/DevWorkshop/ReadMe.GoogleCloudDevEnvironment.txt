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
- Project (mining-clinical-decisions) Permissions, including *Compute Engine Editor*
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
    - Region: A region close by can reduce network latency, but more important is consistency (e.g., us-central1-a)
    - Zone: As above, pick a consistent zone so all of your servers spawn in the same place
    - Machine Configuration: What type of hardware do you want to use
      - Series + Machine Type
        Different machines types cost different amounts based on how many CPUs and RAM you need
        For testing purposes, a small g1-small should be sufficient (the smallest f1-micro looks like it doesn't have enough RAM for subsequents steps)
    - Boot Disk: Allow specification of different default Operating Systems (default Debian GNU/Linux for now)
  	- Identity and API access
      Select 'mining-clinical-dev' for simplicity for now, 
      as this gives read/view and create job access the BigQuery databases through a Service Account 
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
  Default system comes with Python 3 installed ("python3") (as of 1/29/2021),
  but is largely barebones in terms of other software packages. Using package management software tools,
  such as apt and pip in this case, are essentially for easing the pain of "dependency hell."

  Run the following commands to install several dependencies:

    sudo apt update                               # Tell the "superuser" admin to "do" an update of the apt tool
    sudo apt install git                          # Git client to communicate with source code version control repository
    sudo apt install python3-pip                  # Install PIP tool for Python package management
    python3 -m pip install google-cloud-bigquery  # Python - Google Cloud interface to connect to BigQuery databases 
                                                    ***This takes over 10 minutes. Consider opening a second terminal connection to the compute instance so you can continue the subsequent steps in parallel
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

- Setup LocalEnv.py file so the application DBUtil knows how to find the BigQuery database
  
  Copy the CDSS/LocalEnv.py.template into a CDSS/LocalEnv.py configuration file.
    cp CDSS/LocalEnv.py.template CDSS/LocalEnv.py

  Edit the contents of the LocalEnv.py file to refer to the database of interest.
  You can use the not great, but ubiquitous "vi" editor on Unix systems
    vi CDSS/LocalEnv.py

    Quick vi commands
    - x: Delete a character
    - i: Change to "insert" (i.e., edit mode)
    - Escape: Exit out of edit mode
    - ":wq": Change to "colon-command" mode, then (w)rite your changes to the file, then (q)uit the editor
    - ":q!": Change to "colon-command" mode, (q)uit the editor, WITHOUT saving changes (!)
    
  Most of the other settings can be ignored, as they are for other environments (e.g., PostgreSQL databases)
  
    DATABASE_CONNECTOR_NAME = "bigquery"

    LOCAL_PROD_DB_PARAM["HOST"] = 'mining-clinical-decisions"

== Testing and Running (Batch) Processes ==
On GCP Linux Server:

- Test Run an Application Module that Connects to Database
  Should report the number of patient records in the example dataset

    python3 -m medinfo.db.DBUtil "select count(*) from starr_datalake2018.demographic"

- Running an example script to process data from database and manage intermediate results files
  - Go to CDSS/scripts/DevWorkshop/GoogleCloudPlatform 
  - Run the following commands

    python3 ExampleQueryApp.py -r Intravenous -d CEF -p 0 -

  Should output a bunch of data rows to the console.
  If you don't want to see it all, you can send the output to a text file

    python3 ExampleQueryApp.py -r Intravenous -d CEF -p 0 results/dataRows.tab

  For potentially very large (intermediate) data files, consider storing them in gzipped format
  by piping the output through the gzip program and redirecting to a respectively named file.

    python3 ExampleQueryApp.py -r Intravenous -d CEF -p 0 - | gzip > results/dataRows.tab.gz

  Note that this functionality is already embedded in medinfo.common.Util.stdOpen to transparently
  treat any text files with the .gz suffix as presumptive gzipped content and treat "-" as stdin or stdout.

    python3 ExampleQueryApp.py -r Intravenous -d CEF -p 0 results/dataRows.tab.gz

  You can similarly then decompress and read the contents of gzipped files on-demand

    gzip -dc results/dataRows.tab.gz



- Artificially simulate a slow/long process by adding in a 0.5 second pause between each result row

    python3 ExampleQueryApp.py -r Intravenous -d CEF -p 0.5 results/dataRows.tab

  When you get bored waiting for above to finish, Ctrl+C to abort the process

- Run the process again, but do so in the background

    nohup python3 ExampleQueryApp.py -r Intravenous -d CEF -p 0.5 results/dataRows.tab &> log/progress.log &

  Above will run the process in the background (ending &) and continue even if you logoff (nohup = "no hangup").
  So you can start a long process and just let the server continue to work on it,
  without requiring you to keep your (laptop) client computer logged in.
  Any error messages, progress indicators, or other text that you normally see in the console window will be
  redirected (&>) to the specified log file (log/progress.log)

- Check on the progress of the process you have running in the background
  `ps -u yourUserName -f`
    Checks which processes are running under your username, with full details. Note the Process ID (PID)
  `kill <PID>`
    If you need to kill a process that you don't want to continue anymore
  `top`
    Running monitor of all the most intensive processes running on the server
    Overall reporting can track how much total free memory (RAM) the server still has available,
    and how much processor (CPU) is being used. Helpful when trying to gauge the bottleneck 
    for intensive processes (need more processors or need more RAM?).
    Note that total CPU load can be >100% for servers with multiple CPUs.
    The whole point of using a multi-processor server is that you should run 
    multiple simultaneous (parallel) processes to take advantage of extra CPUs working for you.
    You can't make a single process run at 200% speed with two CPUs,
    but you can break up the work into two separate tasks, and have each running at 100% on separate CPUs.
    Beware that the multiple processors are both using the same shared memory (RAM), so if you have a process
    that uses a lot of RAM, parallelizing the process will also multiply the amount of total RAM needed.

    "M" to sort the results by which processes are using the most memory
    "q" to quit/exit when done.
  `cat log/progress.log`
    Show the output of the redirected console output from your application process
  `tail -f log/progress.log`
    Show just the last few lines of the redirected console output, 
    and continue watching it until Ctrl+C to abort.
    (Ctrl+C will abort the "tail" monitoring process, not the original application process.)

- Use a batch driver script to run multiple (parallel) processes
  (Beware that this is likely to overwhelm the RAM (memory) available on your tiny test compute instance)

  `bash batchDriver.sh`

  Though bash (.sh) scripts are more common, I often prefer Python when it can do all of the above, 
  is more flexible, platform independent, and unifies the programming/scripting language used.
  For example, rather than copy-pasting a dozen similar but different command line calls in batchDriver.sh,
  use a Python loop to dynamically generate those commands and spawn them via the subprocess module:

  `python3 batchDriver.py`

  If you prefer serial, rather than parallel, processes for more control.
  Remove the "nohup &" background commands from the .sh script, or change the Python subprocess.Popen to subprocess.call.
  You may then want to run the batchDriver itself as a background process with a redirected log file:

  `nohup python3 batchDriver.py &> log/driver.log &`

  Additional support functionality:
    medinfo/common/support/awaitProcess.py - Wait until an existing process completes before starting another one
    medinfo/common/ProcessManager.py - Not implemented yet (5/14/2018). Intended to consolidate above support functionality.

  Large compute clusters often have their own job submission and parallelization schemes (e.g., qsub, bsub grid engines).
  Depending on the scale of your needs, you may want to look into such services. 
  Otherwise, you can get a lot done cheaply by just taking advantage of multiple CPU servers as above.
  For example, once you've got your compute instance setup, create a SnapShot image of the hard disk,
  then restore that image onto a server with dozens more CPUs and then just run your processes on that server.
  We're paying for these servers by the hour, but the pricing is proportional to capacity.
  Given that proportionality, you can pay twice as much for twice as many CPUs that will get your
  job done in half the time. This is perfectly worth it since the amount of dollars spent is the same,
  but you save half your human time waiting for results.




OPTIONAL LEARNING 
- SnapShots and Machine Images
  	Useful when you need more/less compute or want to backup your virtual machine setup at a particular time:

    Option 1 - SnapShots (only saves changes compared to last copy, reducing storage costs)
    - Store / Save a copy of a currently running compute engine instance hard disk as a SnapShot
      - Compute Engine > Disks > (Find your running Instance) > [Create Snapshot]
    - Restore / Spawn a copy of a compute engine instance that was previously saved as a SnapShot
      - Compute Engine > Snapshots > (Find the snapshot of interest) > [Create Instance]
        Most settings will be similar to creating a new compute instance, 
        but note how you can choose a "bigger" computer with more CPU, RAM but still have the same
        Boot hard disk / code setup ready to go.

    Option 2 - Machine Images (includes copy of entire hard disk and operating system)
    - Store / Save a copy of a currently running compute engine instance
      - [New Machine Image] from the ... menu for your running instance
    - Restore / Spawn a copy of a compute engine instance that was previously saved as a Machine Image
      - Machine Image section > Create an Instance





- Notes on How to Upload/Download any File
  - Option 1 - Using SSH/Web Browser client
    - Top right corner of window has a "Gear" icon with a Upload and Download file option
    - To download specify your path and file you wish to download: for example:
      - ("/home/yourUserName/CDSS/scripts/DevWorkshop/ReadMe.GoogleCloudDevEnvironment.txt")
    - To upload:
      - select 'Upload file' and select the file you wish to upload to the current working directory

  - Option 2 - Using gcloud from you local command-line console to simulate an SCP (secure copy) command
    
    gcloud compute scp yourLocalFile.txt <instance-name>:/home/yourUserName/yourRemoteFileCopy.txt



- Nero Compute GCP Cheat Sheet for PHI Secure Compute Version?
https://docs.google.com/drawings/d/14Ixgar6XTSWiXwlBG16AFNxpZzPl2gNrF7P3U4s7JHc/edit?usp=sharing
