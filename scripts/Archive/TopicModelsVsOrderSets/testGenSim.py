import sys, os;
from pprint import pprint   # pretty-printer

import gensim;
from gensim import corpora, models, similarities
from medinfo.common.Util import *;

def main(argv):
    pass;
    
    
documents = \
    [   "Human machine interface for lab abc computer applications",
        "A survey of user opinion of computer system response time",
        "The EPS user interface management system",
        "System and human system engineering testing of EPS",
        "Relation of user perceived response time to error measurement",
        "The generation of random binary unordered trees",
        "The intersection graph of paths in trees",
        "Graph minors IV Widths of trees and well quasi ordering",
        "Graph minors A survey",
    ];

# Texts: Lists of words
stoplist = set('for a of the and to in'.split())
texts = \
    [   [word for word in document.lower().split() if word not in stoplist] 
        for document in documents];

pprint(texts);

# Word/Token/Term frequency counts
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1


# Remove words that appear only once
texts = \
    [   [token for token in text if frequency[token] > 1]
        for text in texts
    ];

pprint(texts);



# GenSim Dictionary format to convert item lists into count vectors/dicts
dictionary = corpora.Dictionary(texts); # Instead of full list of texts, could feed in an iterator/generator
# dictionary.save("temp.dict");
print(dictionary);
print(dictionary.token2id); # Mapping of text tokens to generated indexes
print(dictionary.id2token); # Mapping of text tokens to generated indexes

# Convert a document into vector form
newDoc = "Human computer interaction";
newVec = dictionary.doc2bow(newDoc.lower().split());
print(newVec);

# Corpus: Bag of Words (BoW) sparse vector/dictionary formats (list of 2-ples: (wordId, frequencyCount))
corpus = [dictionary.doc2bow(text) for text in texts];
corpora.MmCorpus.serialize("temp.mm",corpus)
pprint(corpus); # Table of (wordId, count) pairs.  One row per document.
"""
print "---------"

reloadCorpus = corpora.MmCorpus("temp.mm");
for bag in reloadCorpus:
    print bag
"""
# NumPy and SciPy conversions   (Matrixes seem to be transposed compared to what would expect)
"""
numpyMatrix = gensim.matutils.corpus2dense(corpus, len(dictionary));
print numpyMatrix;

scipyCSC = gensim.matutils.corpus2csc(corpus);
print scipyCSC;
"""

# Model data.  TFIDF simple example.  Later Latent Dirichlet Allocation will be much more costly
tfidf = models.TfidfModel(corpus);  # Computes document frequencies of each item
# Use model to convert (bag-of-word count) vectors into new (TFIDF floating point weights).  Normalize each document vector so Eucledean magnitude of 1
corpus_tfidf = tfidf[corpus]

"""
# Latent Semantic Indexing
print "LSI?????"
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2);
corpus_lsi = lsi[corpus_tfidf]; # Chaining transformation wrappers
pprint(lsi.print_topics(2));
"""
print "LDA..."
nTopics = 4;
#lda = models.LdaMulticore(corpus_tfidf,id2word=dictionary, num_topics=nTopics, workers=2);
lda = models.LdaModel(corpus_tfidf,id2word=dictionary, num_topics=nTopics);
hdp = models.hdpmodel.HdpModel(corpus_tfidf,id2word=dictionary);

#for iTopic in xrange(nTopics):
#    print lda.show_topic(iTopic, topn=20);

#topics = lda.show_topics(num_topics=-1, num_words=20, formatted=False)
#topics = lda.show_topics(topics=-1, topn=20, formatted=False)
#for topicId, topicItems in enumerate(topics):
#    for (itemDescr, itemScore) in topicItems:
#        print topicId, itemDescr, itemScore;

#corpus_lda = lda[corpus_tfidf];
#for doc in corpus_lda:
#    print(doc);

if __name__ == "__main__":
    main(sys.argv);
    