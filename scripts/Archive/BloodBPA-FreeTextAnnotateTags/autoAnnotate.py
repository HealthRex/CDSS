import sys, os;

PUNCTUATION = ".,:;\"'()?+";

# python autoAnnotate.py overrideComments.txt wordTags.txt > autoAnnotations.txt

infile = open(sys.argv[1]); # Source file with free text comments to parse
wordTagFile = open(sys.argv[2]);    # File with 3 columns for word counts, words and associated tags to assign if found

tagsByWord = dict();
for line in wordTagFile:
    chunks = line.strip().split("\t");
    if len(chunks) >= 3:
        (wordCount, word, tag) = chunks;
        word = word.strip(PUNCTUATION).upper();
        tagsByWord[word] = tag;

for line in infile:
    chunks = line.strip().split("\t");  # Separate out ID column
    (comment, id) = chunks;
    chunks = comment.split();    # Separate by simple white space
    
    commentTags = set();
    
    for chunk in chunks:
        word = chunk.strip(PUNCTUATION).upper();    # Ignore punctuation delimiters and case sensitivity

        if word in tagsByWord:
            commentTags.add(tagsByWord[word]);

    print "%s\t%s\t%s" % (id, str.join(",", commentTags), comment);
