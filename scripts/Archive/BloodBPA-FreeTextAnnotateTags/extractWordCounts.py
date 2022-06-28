import sys, os;

PUNCTUATION = ".,:;\"'()?+";

infile = open(sys.argv[1]);

wordCounts = dict();

for line in infile:
    chunks = line.strip().split("\t");  # Separate out ID column
    (comment, id) = chunks;
    chunks = comment.split();    # Separate by simple white space
    
    for chunk in chunks:
        word = chunk.strip(PUNCTUATION).upper();    # Ignore punctuation delimiters and case sensitivity
        
        if word not in wordCounts:
            wordCounts[word] = 0;
        wordCounts[word] += 1;

wordList = wordCounts.keys();
wordList.sort();
for word in wordList:
    print "%s\t%s" % (wordCounts[word], word);
