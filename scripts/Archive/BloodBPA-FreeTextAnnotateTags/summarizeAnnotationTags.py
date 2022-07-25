import sys, os;

# python summarizeAnnotationTags.py sampleTags.txt > tagCounts.txt

PUNCTUATION = ".,:;\"'()?+";
    
# Source file comma-delimited annotation tags
infile = open(sys.argv[1]); 

countsPerTag = dict();
for line in infile:
    line = line.strip();
    if line != "":  # Skip blank lines / no tags
        tags = line.replace(";",",").split(",");
        for tag in tags:
            tag = tag.upper();  # Ensure case insensitivity
            if tag not in countsPerTag:
                countsPerTag[tag] = 0;
            countsPerTag[tag] += 1;

print "Count\tTag";
for tag, count in countsPerTag.iteritems():
    print "%s\t%s" % (count, tag);
