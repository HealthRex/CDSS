## Taken from 
# http://stackoverflow.com/questions/20039643/how-to-scrape-a-website-that-requires-login-first-with-python

import sys, os;

##################################### Method 1
#import mechanize
#import cookielib
from BeautifulSoup import BeautifulSoup
import urllib;

from medinfo.common.Util import ProgressDots, stdOpen;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

BASE_FILENAME = 'buprenorphinePhysicians.%s.htm';
N_PAGES = 641
#N_PAGES = 5

OUTPUT_FILENAME = 'prescribers.suboxone.tab';

ofs = stdOpen(OUTPUT_FILENAME,"w");
formatter = TextResultsFormatter(ofs);

colNames = list();
allColsSeen = False;

progress = ProgressDots(big=100,small=2);
for iPage in xrange(N_PAGES):
    localFilename = BASE_FILENAME % (iPage);
    localFile = open(localFilename);
    html = localFile.read();
    localFile.close()
    
    soup = BeautifulSoup(html);
    cells = soup("td");

    currRow = list();

    for cell in cells:
        if not allColsSeen: # Look for col names as go, then drop just dump out rows worth as progress
            if cell["class"] not in colNames:
                colNames.append(cell["class"]);
            else:
                allColsSeen = True;
        if allColsSeen and len(currRow) == len(colNames):
            formatter.formatTuple(currRow);
            currRow = list();
        currRow.append(cell.text.encode('utf-8'));

    #obj = soup.find(class="views-field-field-bup-physician-last-name")

    progress.update();
progress.printStatus();

ofs.close();
