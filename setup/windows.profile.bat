@echo off
rem Example profile script to setup environment variables need to run programs on a Windows machine.
rem Analogous to a bash profile script on a Unix machine.
rem Modify these to match your own computer.  
rem Use regedit to create an entry pointing to this script to autorun on startup at
rem		HKEY_CURRENT_USER\Software\Microsoft\Command Processor\AutoRun
rem Enter "cmd /?" for additional info

rem Application path.  Directory containing modules can be imported by each other
set MEDINFO_DIR=C:\CDSS
set PYTHONPATH=%PYTHONPATH%;%CHEM_DIR%;%MEDINFO_DIR%

rem Put Python on path for command-line convenience
set PYTHONHOME=D:\Dev\Python3.12
set PATH=%PYTHONHOME%;%PYTHONHOME%\Scripts;%PATH%

rem Put R on path for command-line convenience
set PATH=C:\Dev\R\R-3.6.1\bin;%PATH%

rem PostgreSQL DLL's need to be accessible for clients to work
set POSTGRESQL_HOME=D:\Dev\PostgreSQL16
set PATH=%POSTGRESQL_HOME%\bin;%PATH%
set PG_PASSWORD=1234

rem MOD_WSGI Apache connections
set MOD_WSGI_APACHE_ROOTDIR=D:\Dev\Apache24

rem Git Unix tools
set PATH=%PATH%;C:\Program Files\Git\usr\bin

rem Google Cloud authentication
set GOOGLE_APPLICATION_CREDENTIALS=C:\GoogleDrive\Tools\application_default_credentials.jonc101@stanford.edu.json

rem Organize DIR listings
set DIRCMD=/O:GEN /P

rem Add date time to command line prompt
set PROMPT=$D $T$_$P$G

rem Starting Directory
c:
cd %MEDINFO_DIR%
