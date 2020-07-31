## Taken from 
# http://stackoverflow.com/questions/20039643/how-to-scrape-a-website-that-requires-login-first-with-python

import sys, os;

##################################### Method 1
import mechanize
import cookielib
#from BeautifulSoup import BeautifulSoup

from medinfo.common.Util import ProgressDots;



# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', 'Chrome')]

# The site we will navigate into, handling it's session
#br.open('https://xxx.org/login')

# View available forms
#for f in br.forms():
#    print f

# Select the second (index one) form (the first form is a search query box)
#br.select_form(nr=1)

# User credentials, single login and then store a cookie
#br.form['username'] = 'jonc101'
#br.form['password'] = 'xxxx'

# Login
#br.submit()

# Base URL to query for, with parameters for subsets
BASE_URL = 'http://www.samhsa.gov/medication-assisted-treatment/physician-program-data/treatment-physician-locator?field_bup_physician_us_state_value=All&page=%s'
BASE_OUTPUT_FILENAME = 'buprenorphinePhysicians.%s.htm';
N_PAGES = 641
#N_PAGES = 10

progress = ProgressDots(big=100,small=2);
for iPage in xrange(N_PAGES):
    sourceURL = BASE_URL % (iPage);
    sourceFile = br.open(sourceURL);
    sourceContent = sourceFile.read();  # Just store whole file in memory for simplicity
    sourceFile.close();
    
    localFilename = BASE_OUTPUT_FILENAME % (iPage);
    localFile = open(localFilename,"w");
    localFile.write(sourceContent);
    localFile.close();
    
    progress.update();
progress.printStatus();
