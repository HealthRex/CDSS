# Read tab-delimited input using header row labels and interpret Python None strings as R NA values
dataFile = "featureMatrix.sample.tab";
#dataFile = gzfile("featureMatrix.ICUDNR.removeExtraHeaders.tab.gz");
df = read.table(dataFile,header=TRUE,sep="\t",na.strings="None");

# Convert Python 'True' or 'False' text as boolean TRUE, FALSE and convert to numerical 1 or 0 encoding by multiply * 1 or add + 0
# Should be able to do above as a loop to convert all similar .pre and .post columns
df$AnyDNR.post = (df$AnyDNR.post=='True')*1

# Parse as date strings
df$index_time = as.Date(df$index_time);

# Looking for DNR within the next day
#df$AnyDNR.within1day = !is.na(df$AnyDNR.postTimeDays < 1) # No, captures all non-null values
df$AnyDNR.within1day = 0 
df$AnyDNR.within1day[df$AnyDNR.postTimeDays < 1] = 1

# Select out those days with no prior DNR
subDF = df[ !df$AnyDNR.pre ]

