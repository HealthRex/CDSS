# HealthRex Laboratory at Stanford University
## PI: Jonathan Chen (http://web.stanford.edu/~jonc101)

Review the Wiki (https://github.com/HealthRex/CDSS/wiki) for Starter Notes on using some of the common data sources and codebase as well as general lab/group infrastructure.

General Guidelines for Code Repo:
* Avoid any large data files, so the repo stays lightweight for new devs to quickly download/clone.
* For one-off or very project specific files and scripts, basically do whatever you want in the workspace areas under the /scripts directory (but again, avoid big data files and also avoid any private / patient information, including analysis results that include individual patient items, as this repo will publicly accessible).
* Try to promote reusable components to the medinfo core application modules.

Broad description of core application directories
* medinfo/analysis - General purpose analysis and data manipulation modules, not specific to any type of project. For example, serially calculating t-tests, list rank similarity measures, ROC plots, precision-recall curves, SQL-like manipulation functions for CSV / TSV files.
* medinfo/common - General purpose computing utilities, such as calculating different 2x2 contingency stats, adding progress trackers to long processes.
* medinfo/cpoe - More project specific applications related to Computerized Physician Order Entry projects, implementing different approaches to clinical order recommendations and evaluating/analyzing them with different experiments on historical data. Application code for clinical case simulations for users to interact with.
* medinfo/dataconversion - General and project specific utilities to pre-process data sources. Given a dump of hospital data, conversion scripts to unify into a simplified / pre-processed clinical_item transaction series. FeatureMatrixFactory to extract out clinical data into simple "feature matrix" / dataframe form to feed into assorted learning algorithms. Subdirecties with additional supporting mapping data (e.g., ICD9 codes to Charlson comorbidity categories).
* medinfo/db - Utilities to connect between Python code and SQL databases, with a relatively plain JSON-like model of tables represented by lists of dictionaries (name-value pairs of each row of data). ResultsFormatter has several convenience functions to interconvert between SQL data tables, CSV/TSV plain text files, Pandas dataframes, and JSON-like lists of Python dictionaries. Several project specific application database schemas in the definition subdirectory. Support subdirectory with "dump" and "restore" convenience scripts to move database content between systems.
* medinfo/geography - Not much here yet. One example of how to generate data labeled geographic maps of the US.
* medinfo/textanalysis - Not much here yet. One example of a project specific parsing script that translates a stream of text documents into an interactive HTML file that attempts to auto-annotate features of the documents based on Python coded annotator classes.
* medinfo/web - View and Controller layer for web interface to application functions.

	 
