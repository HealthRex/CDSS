import sys, os;
from scipy import array;
from scipy.stats import chi2, chisquare, chi2_contingency;
from util import kappaStat;

# python calcAgreementStats.py mergedTags.txt mergedTags.Daniel.txt > agreementStats.txt

# Yates correction for contingency tables that have small (even 0) values to avoid overestimating statistical significance
# http://en.wikipedia.org/wiki/Yates%27s_correction_for_continuity
yatesCorrection = True;
   
# First pass to identify the category tag sets
categoryTags = set();
# Separate accounting for tag combinations as unique entities
compositeTags = set();

# Source file comma-delimited annotation tags
infile1 = open(sys.argv[1]); 
infile2 = open(sys.argv[2]); 

for line1 in infile1:
    line1 = line1.strip();
    
    line2 = infile2.readline().strip();
    
    tagSet1 = set(line1.replace(";",",").split(","));
    tagSet2 = set(line2.replace(";",",").split(","));

    categoryTags.update(tagSet1);
    categoryTags.update(tagSet2);
    
    compositeTags.add( str.join(',',tagSet1) );
    compositeTags.add( str.join(',',tagSet2) );



# Second pass to assess counts for the categoryTags
# Build a 2x2 contingency table for each tag based on counts of whether each tag appears for 
#   one, both, or neither of the two data sources
# Let row 0/false represent counts where data source 1 does not have the tag
#     row 1/true represent counts where data source 1 has the tag
# Let col 0/false represent counts where data source 2 does not have the tag
#     col 1/true represent counts where data source 2 has the tag

contingencyTableByTag = dict();
for tag in categoryTags:
    contingencyTableByTag[tag] = [ [0,0], [0,0] ];


infile1 = open(sys.argv[1]); 
infile2 = open(sys.argv[2]); 

for line1 in infile1:
    line1 = line1.strip();
    
    line2 = infile2.readline().strip();
    
    tagSet1 = set(line1.replace(";",",").split(","));
    tagSet2 = set(line2.replace(";",",").split(","));

    for tag in categoryTags:
        contingencyTable = contingencyTableByTag[tag];
        
        iRow = (tag in tagSet1);
        iCol = (tag in tagSet2);
        
        contingencyTable[iRow][iCol] += 1;
        
# Now print the values for the accumulated contingency tables as well as calculated chi-square stats and p-values
sortedTags = list(categoryTags);
sortedTags.sort();
for tag in sortedTags:
    contingencyTable = contingencyTableByTag[tag];

    (kappa, agreeRate, chanceRate) = kappaStat( contingencyTable );

    # Chi Square stat for p-value for independence
    pValue = None;
    try:
        (chi2stat, pValue, dof, expTable) = chi2_contingency(contingencyTable, yatesCorrection);
    except ValueError, err:
        # Many errors expected for cases where one data source / user never used one of the tags
        #   resulting in a column or row of the table being all 0, making the chi2stat uncalculatable
        #print >> sys.stderr, err;
        pass;

    contingencyTableText  = "%s\t%s" % tuple(contingencyTable[0]);
    contingencyTableText += "\t%s\t%s" % tuple(contingencyTable[1]);
    print "%s\t%s\t%s\t%s\t%s\t%s" % (tag, contingencyTableText, pValue, agreeRate, chanceRate, kappa);
