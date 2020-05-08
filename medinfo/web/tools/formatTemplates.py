import sys,os;
import csv;

TEMPLATE_FOLDER = "Medicine Templates"
TOC_TEMPLATE = '<LI><A HREF="#%(TITLE)s">%(TITLE)s</A>';
ROW_TEMPLATE = '<BR><A NAME="%(TITLE)s"/><h3>%(TITLE)s</h3><textarea rows=20 style="width: 100%%">%(NOTE)s</textarea><br>'

ifs = open(sys.argv[1]);
ofs = open(sys.argv[2],"w");
reader = csv.DictReader(ifs);

rowByTitle = dict();

# First pass to collect data so can resort and build title table of contents
for row in reader:
    if row["FOLDER"] == TEMPLATE_FOLDER:
        rowByTitle[row["TITLE"]] = row;

# Build table of contents
sortedTitles = list(rowByTitle.keys());
sortedTitles.sort();

print("<ul>", file=ofs);
for title in sortedTitles:
    row = rowByTitle[title];
    print(TOC_TEMPLATE % row, file=ofs);
print("</ul>", file=ofs);

# Build actual content
for title in sortedTitles:
    row = rowByTitle[title];
    print(ROW_TEMPLATE % row, file=ofs);
        