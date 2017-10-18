"""Given 2D Table of values, spit out "melted" long-relational form to feed into antibiogramData.js"""

import sys,os;
from medinfo.common.Const import NULL_STRING;
from medinfo.common.Util import stdOpen;
from medinfo.db.ResultsFormatter import TabDictReader, TextResultsFormatter;

ifs = stdOpen(sys.argv[1]); # Input tab delimited file
ofs = stdOpen(sys.argv[2],"w");	# "-" for stdout

reader = TabDictReader(ifs);
formatter = TextResultsFormatter(ofs);
for row in reader:
	bug = row["Bug"];
	for key in reader.fieldnames:
		value = row[key];
		if key != "Bug" and value and value != NULL_STRING:
			formatter.formatTuple([value, bug, key]);
