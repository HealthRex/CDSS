import sys, os;

MERGE_TAG_COL = 2;
MERGE_ALT_COL = 3;

# python mergeTags.py sampleTags.txt tagMergeWorksheet.txt > mergedTags.txt

# Source file comma-delimited annotation tags
infile = open(sys.argv[1]); 
mergeWorksheet = open(sys.argv[2]);

# Look for worksheet data to merge tags
altTagsByKeyTag = dict();
if len(sys.argv) > 2:
    for line in mergeWorksheet:
        chunks = line.strip().split("\t");
        if len(chunks) > MERGE_ALT_COL and chunks[MERGE_ALT_COL] != "":
            tag = chunks[MERGE_TAG_COL].upper();
            altTags = chunks[MERGE_ALT_COL].split(",");
            if tag not in altTagsByKeyTag:
                altTagsByKeyTag[tag] = set();
            for altTag in altTags:
                altTagsByKeyTag[tag].add(altTag.upper());

# Now rewrite the source tags into merged results
for line in infile:
    line = line.strip().replace(" ","");    # Discard whitespace
    tags = line.replace(";",",").split(",");
    tagSet = set();
    for tag in tags:
        tag = tag.upper();  # Ensure case insensitivity
        if tag in altTagsByKeyTag:
            tagSet.update(altTagsByKeyTag[tag]);
        else:
            tagSet.add(tag);
    print str.join(",", tagSet );
    