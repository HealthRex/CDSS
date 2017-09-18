from time import strptime;
from datetime import datetime;

SECONDS_PER_DAY = 60*60*24;
DATE_FORMAT = "%m/%d/%y %H:%M";	# Defines how the date strings should be interpreted: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

startDateStr = "11/16/10 17:04";
startTimeTuple = strptime(startDateStr, DATE_FORMAT);	# Parses string into tuple/list of date elemenets (2010, 11, 16, 17, 4, 0)
startDate = datetime(*startTimeTuple[:6]);	# Takes date elements as parameters to create an object representing the date

endDateStr = "11/18/10 10:59";
endTimeTuple = strptime(endDateStr, DATE_FORMAT);
endDate = datetime(*endTimeTuple[:6]);


difference = endDate - startDate;	# timedelta object
diffDays = difference.total_seconds() / SECONDS_PER_DAY; # Number format in units of days

""" Comparable R code
DATE_FORMAT = "%m/%d/%y %H:%M";	# Defines how the date strings should be interpreted: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

startDateStr = "11/16/10 17:04";
startDate = strptime(startDateStr, DATE_FORMAT);

endDateStr = "11/18/10 10:59";
endDate = strptime(endDateStr, DATE_FORMAT);

diffDays = endDate - startDate;

"""