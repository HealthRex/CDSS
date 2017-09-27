# HealthRex Laboratory at Stanford University
## PI: Jonathan Chen (http://web.stanford.edu/~jonc101)

Shared workspace in development

General Guidelines for Code Repo:
* Avoid any large data files, so the repo stays lightweight for new devs to quickly download/clone.
* For one-off or very project specific files and scripts, basically do whatever you want in the workspace areas under the scripts directory (but again, avoid big data files).
* Try to promote reusable components to the medinfo core application modules.



====================================================

Starter Notes:
?This needs to be organized more, but a sketch of notes I usually email people initially.
?Perhaps move this to Wiki
?Similarly integrate CDSS/scripts/CDSS/setupNotes.txt into a high-level Readme starter


General Data / Code Access
	• Training / Agreements
		○ Register on CITIProgram.org
			§ Complete the module on "Biomedical Responsible Conduct of Research"
			§ Send me a copy of the Completion Certificate

(2B) HIPAA Training
	1. 2B) HIPAA Training (required for almost all datasets. Because current CITI training does not offer an excellent data security module, we are requiring HIPAA training for datasets with or derived from health information or containing PII)
		a. Go to your personal Axess page.
		b. Log in with your SUNet and password.
		c. Click on the STARS link (top).
		d. Click on “Training Needs Assessment”
		e. Only email your supervisor if you want to.
		f. Indicate that you work on research projects.
		g. Click on All Learning.
		h. If needed, use the search tool and search for  HIPAA. Enroll in HIPAA/Protecting Patient Privacy (PRIV-0010).
		i. Take the course.
		j. Once the course(s) is complete, you should receive an email confirming your completion. It should also show up as completed if you click on the “Training History” bar.
		k. Please save the screen shot as a PDF and name the file: firstinitiallastname_HIPAA_DDMMMYY.  So if Isabella Chu completed her classes July 3, 2016, ichu_HIPAA_03Jul16.


		○ Complete the HCUP Data Use Agreement
			• View Accessible HCUP DUA Training Course (Text Only) 
				· At the bottom of this page, fill in your name to print out a completion certificate and send me a copy
			• https://www.hcup-us.ahrq.gov/DUA/dua_508/DUA508version.jsp
				· Fill out and complete the HCUP Data Use Agreement, then send a copy to me and the HCUPDistributor@AHRQ.gov
		○ Health Data Protection / Hard Drive Encryption
			• Any computers you use to work on health data should be encrypted. This is usually a transparent option that is easy to turn on in the background and is generally a good idea anyway in case your computer gets lost or stolen.
			• Web link below should help you figure out if you’ve setup encryption properly. If you install Stanford’s BigFix program, it walks through most of the steps.
			• https://med.stanford.edu/datasecurity/amie/
			• I'd recommend working on a (laptop) computer with at least 16gb RAM and 512gb hard drive. I can help you get this if you do not already have it.

	• Code:
		○ I sent you a link to create an account on XP-Dev.com. I’ve been using them for free source control hosting. I think most people use GitHub nowadays, but I’m still used to using SVN (Subversion).
		○ Use an SVN client to download the codebase
			§ > svn checkout https://xp-dev.com/svn/jonc101-Projects/CDSS
			§ If that works, it should download a bunch of Python 2.7 code to your computer
	 
	• Dev Environment:
		○ Install Python PIP to facilitate other installations
			§ If you installed Python 2.7.8, it might already be installed, otherwise there’s a get_pip.py bootstrapper installer on the internet)
			§ Install some Python modules (e.g., scipy, psycopg2)
				· > python -m pip install psycopg2
		○ Install a local PostgreSQL database server instance
		○ Create a blank test database with the schema definition in cpoeStats.sql.
			§ > psql -f medinfo/db/definition/cpoeStats.sql -U <YourDBUsername> testdb
		○ Create another blank application database, but restore it with sample data:
			§ Box Data Directory: STRIDE-Inpatient-2008-2014/dump2009-2014-5year-time
			§ Restore Script Driver: restoreCPOETables.sh
				· This can take hours (overnight) to all finish patient_item and clinical_item_association tables. Make sure you start with a blank database and that the Indexes and Constraints don't yet exist, otherwise it will drag down the insert/population process
		○ Point the application code to the databases:
			§ Edit medinfo/db/Env.py file’s DB_PARAM to match the application database
			§ Edit TEST_DB_PARAM settings to point to that blank database copy.
		○ Run a basic application database unit test
			§ > python medinfo/db/test/TestDBUtil.py
			§  If that runs, you’re in good shape to have the Python application code interact with the SQL database

	• Data Access
		○ Box - Share data directories (Stanford Email)
		○ Google - Work files share
		○ OneNote - Notebook section share
		○ XP-Dev - SVN Code
 


	• Population Health Sciences Access
	 
	Here are detailed instructions for accessing PHS data. If your staff have completed their trainings and IRB, it should take about 10 minutes to complete these forms: https://tinyurl.com/PHS-Data-Access
	 
	In addition, all PHS Data Users are required to take the PHS Data Core Training and Quiz. This should take you 15 - 20 minutes (including quiz). Completion with 100% on the quiz will waive CITI and HIPAA training for most datasets. CITI and HIPAA take about 4 - 6 hours so we hope you view this as a good deal.
	 
	PHS Data Security Training: http://tinyurl.com/PHS-Data-Security-Training
	 
	For Macs open with Quicktime. For PCs, just click on the image and click the play arrow. It should start.
	 
	If you are already a PHS member and you do not have your personalized link, please request it from Isabella Chu at itaylor@stanford.edu.
	 
	If you need help, my office hours are Thursdays at SIEPR 334 and Fridays online (by appointment) from 10 AM to 11 AM or by appointment. You can sign up for office hours clicking on the PHS Office Hours Sign Up near the top of this page: https://med.stanford.edu/phs/phs-data-center.html or emailing me at itaylor@stanford.edu.
	 
