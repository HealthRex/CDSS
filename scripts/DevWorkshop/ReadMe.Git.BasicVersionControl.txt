Visualization of Git version control commands.
https://twitter.com/MJAlwajeeh/status/984177298076262401?s=20

See CDSS/scripts/DevWorkshop/GithubWorkshop for additional examples.
Otherwise, quick test commands here:


# Get a copy/clone of the code repository to work with
	git clone https://github.com/HealthRex/CDSS.git

# Pull any latest updates or changes from the master online repository to your local copy
	git pull

# Identify yourself to the GitHub repository
	git config --global user.email "yourGitHubEmail"
	git config --global user.name "yourGitHubUserName"

# Try creating a file in the sandbox directory
	cd CDSS/scripts/DevWorkshop/sandbox
	vi yourTestFile.txt

	    Quick vi commands
	    - x: Delete a character
	    - i: Change to "insert" (i.e., edit mode)
	    - Escape: Exit out of edit mode
	    - ":wq": Change to "colon-command" mode, then (w)rite your changes to the file, then (q)uit the editor
	    - ":q!": Change to "colon-command" mode, (q)uit the editor, WITHOUT saving changes (!)

# Tell Git that you want this file to be tracked
	git add yourTextFile.txt

# Save the version of the file to your LOCAL repository
	git commit yourTextFile.txt
		# It will ask for a commit message. Add a 1 or 2 liner comment describing the major changes you made with this commit

# Save your local repository changes to the master online repository
	git push
		# It may ask for your GitHub login info. You can later configure ways to automatically do this
		# It may complain about your local repository not being up to date if others have already pushed their own changes.
		# If so, then first update your own local copy...

# Update your local working code with whatever has been pushed to the master online repository
	git pull


# Try making further edits to one of the files (including ones created by others), and manually correcting any merged file conflicts
	vi yourTestFile.txt

# Review what changes have been made to the file since it was last commit/pushed
	git diff yourTestFile.txt

# Commit changes to local repository with comment message at the same time
	git commit -m "Test revision message" yourTestFile.txt

# Push your changes up to the server again
	git push

# Check a log of all the changes made to the file
	git log yourTestFile.txt
	

# Git contains much more advanced functionality for code branches and remerges, but likely excessive for small-medium sized teams
# Essentially all code content, logs, as well as a Wiki + basic Issue and Project Tracker are accessible on the GitHub website.
