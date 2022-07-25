import sys, os;

# python compareTags.py mergedTags.txt mergedTags.Daniel.txt > tagDiffs.txt

   
# Source file comma-delimited annotation tags
infile1 = open(sys.argv[1]); 
infile2 = open(sys.argv[2]); 

for line1 in infile1:
    line1 = line1.strip();
    
    line2 = infile2.readline().strip();
    
    tagSet1 = set(line1.replace(";",",").split(","));
    tagSet2 = set(line2.replace(";",",").split(","));

    plusSet = tagSet1-tagSet2;
    minusSet = tagSet2-tagSet1;
    
    print "%s\t%s" % (str.join(",", plusSet), str.join(",", minusSet));
