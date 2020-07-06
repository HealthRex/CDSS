#!/usr/bin/env python
"""
Train a Latent Dirichlet Allocation (LDA) model from bag of words sparse vector data of clinical items,
likely generated through PreparePatientItems.
"""

import sys, os
import time;
import json;
from optparse import OptionParser
from io import StringIO;
from datetime import timedelta;
from pprint import pprint;

from medinfo.common.Const import COMMENT_TAG, NULL_STRING;
from medinfo.common.Util import stdOpen, ProgressDots, loadJSONDict;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from .Util import log;

DEFAULT_TOPIC_ITEM_COUNT = 100; # When using or printing out topic information, number of top scored items to consider
BUFFER_UPDATE_SIZE = 100000;   # Number of document Bag-of-Words to keep in memory before performing model updates.

class TopicModel:
    def __init__(self):
        self.model = None;   # Means to provide output feedback to caller for debugging purposes
        self.docCountByWordId = None;
        self.randomState = None;   # Allow caller to set initial (fixed) random_state to facilitate consistent unit/regression testing. E.g., numpy.random.RandomState(10)

    def buildModel(self, corpusBOWGenerator, numTopics):
        """Build topic model from corpus (interpret as generator over contents)

        Given the bag-of-words corpus, build a docCountByWordId count dictionary
        to facilitate subsequent Term Frequency * Inverse DOCUMENT FREQUENCY calculations.
        In Clinical context, document = patient.

        Return (model, docCountByWordId);
        """
        # Load dictionary to translate item IDs to descriptions
        itemsById = DBUtil.loadTableAsDict("clinical_item");
        id2word = dict();   # Models expect a pair for every possible item ID, and judges vocabulary size by length of this dictionary rather than the maximum ID values.  That means have to populate all of the empty ones as well.
        maxId = max(itemsById.keys());
        for itemId in range(maxId+1):
            description = str(itemId);  # Default to just the same as the ID string
            if itemId in itemsById:
                description = itemsById[itemId]["description"];
            id2word[itemId] = description;

        # Stream in progressive updates from corpus generator so don't have to load all into memory
        # Do a batch of many at a time, otherwise very slow to increment one at a time
        docBuffer = list();

        prog = ProgressDots();
        self.model = None;
        self.docCountByWordId = {None: 0};   # Use None key to represent count of all documents
        for i, document in enumerate(corpusBOWGenerator):
            for (wordId, wordCount) in document:    # Assuming uniqueness of wordId keys for each document
                if wordId not in self.docCountByWordId:
                    self.docCountByWordId[wordId] = 0;
                self.docCountByWordId[wordId] += 1;
            self.docCountByWordId[None] += 1;

            docBuffer.append(document);
            if i % BUFFER_UPDATE_SIZE == (BUFFER_UPDATE_SIZE-1): # Update model with current buffer of documents
                self.model = self.updateModel( self.model, docBuffer, id2word, numTopics );
                docBuffer = list(); # Discard committed buffer
            prog.update();

        self.model = self.updateModel( self.model, docBuffer, id2word, numTopics ); # Last update for any remaining documents in buffer
        docBuffer = list(); # Discard committed buffer

        # prog.printStatus();
        return (self.model, self.docCountByWordId);


    def updateModel(self, model, docBuffer, id2word, numTopics):
        """Update the given model object with the document buffer.
        If the model does not yet exist,
        then instantiate a new one to receive updates.
        """
        import gensim;  # Only import external module as needed
        if model is None:   # Initialize model
            if numTopics < 1:
                model = gensim.models.hdpmodel.HdpModel( docBuffer, id2word=id2word, random_state=self.randomState );
            else:
                model = gensim.models.LdaModel( docBuffer, id2word=id2word, num_topics=numTopics, random_state=self.randomState );
        else:
            model.update( docBuffer );
        return model;

    def jsonGeneratorFromFile(self, inputFile):
        """Simple iterator to parse input file rows from JSON format objects"""
        for line in inputFile:
            line = line.strip();
            if not line.startswith(COMMENT_TAG):    # Skip comment lines
                yield json.loads(line);

    def enumerateTopics(self, model, itemsPerCluster):
        """Iterate through all topics in the model, including up to the specified number of itemsPerCluster.
        Need this wrapper as LDA and HDP models have different interfaces.
        Return an iterator over topic data
        Each topic data is a 2-ple: (iTopic, List of top item data)
        Each item data is a 2-ple: (itemId, itemTopicWeight)
            Will favor reporting of itemId rather than translated itemDescription / itemWord, since can always map with id2word later

        Can take several seconds to extract this information out of the model objects,
            so probably worth it to cache the results if going to do repeated enumeration queries
        """
        # Use raw IDs instead of word translation
        id2word = model.id2word;
        id2id = dict();
        for id in id2word:
            id2id[id] = id;
        model.id2word = id2id;

        import gensim; # External import as needed
        if isinstance(model, gensim.models.HdpModel):   # Has different topic API for no good reason
            # topics = model.show_topics(num_topics=-1, num_words=itemsPerCluster, formatted=False);
            topics = model.show_topics(num_words=itemsPerCluster, formatted=False);
            for topicId, topicItems in topics:
                #for (itemId, itemWeight) in topicItems:  # 2-ple order is also reversed for no good reason
                #    print topicId, itemDescr, itemWeight;
                yield topicId, topicItems;
        else:   # Assume default API for LDA based models
            topics = model.show_topics(num_topics=-1, num_words=itemsPerCluster, formatted=False);
            for topicId, topicItems in topics:
                yield topicId, topicItems;

        model.id2word = id2word;    # Revert back to normal id-word translation

    def generateWeightByItemIdByTopicId(self, model, itemsPerCluster):
        """Go through results of enumerateTopics and store results (essentially all of the model parameters)
        into a big dictionary of dictionaries.  Allows for results to be cached in memory so don't
        have to go back to the model to (expensively) re-extract these contents.
        """
        weightByItemIdByTopicId = dict();
        for (topicId, topicItems) in self.enumerateTopics(model, itemsPerCluster):
            weightByItemIdByTopicId[topicId] = dict();
            for (itemId, weight) in topicItems:
                weightByItemIdByTopicId[topicId][itemId] = weight;
        return weightByItemIdByTopicId;

    def printTopicsToFile(self, model, docCountByWordId, topicFile, itemsPerCluster):
        """Print out the topic model contents to file in tab-delimited format for easy review"""

        print("topic_id\titem_id\tdescription\tscore\ttfidf", file=topicFile);
        id2word = model.id2word;
        for (topicId, topicItems) in self.enumerateTopics(model, itemsPerCluster):
            for (itemId, itemScore) in topicItems:
                itemDescription = id2word[itemId];
                tfidf = 0.0;
                if itemId in docCountByWordId and docCountByWordId[itemId] > 0:
                    tfidf = itemScore * docCountByWordId[None] / docCountByWordId[itemId];
                print("%s\t%s\t%s\t%s\t%s" % (topicId, itemId, itemDescription, itemScore, tfidf), file=topicFile);

        # Now print out basic word-document counts under the "None" Topic representing all documents / entire corpus
        for itemId, docCount in docCountByWordId.items():
            itemDescription = None;
            if itemId in id2word:
                itemDescription = id2word[itemId];
            print("%s\t%s\t%s\t%s\t%s" % (None, itemId, itemDescription, docCount, docCountByWordId[None]), file=topicFile);

    def topTopicFilename(self, baseName):
        """Generate a name for a top topics summary file given a base output filename"""
        return baseName+".topics.tab";

    def loadModel(self, filename):
        """Given the name of a model output file, load it back into an executable object.
        Have to do some conjecture based on accompanying file presence to figure out the correct object class.
        """
        import gensim; # External import as needed
        if os.path.exists(filename+".state"):   # Looks like LDA model
            return gensim.models.ldamodel.LdaModel.load(filename);
        else:   # Presume HDP model
            return gensim.models.hdpmodel.HdpModel.load(filename);

    def loadDocCountByWordId(self, filename):
        """Given the name of a top topics file,
        load the section reporting the overall word document counts
        """
        docCountByWordId = dict();
        reader = TabDictReader(stdOpen(filename));
        for topicItem in reader:
            if topicItem["topic_id"] == NULL_STRING:    # All document section, not topic specific
                itemId = None;
                if topicItem["item_id"] != NULL_STRING:
                    itemId = int(topicItem["item_id"]);
                docCount = int(topicItem["score"]);
                docCountByWordId[itemId] = docCount;
        reader.close()
        return docCountByWordId;

    def loadModelAndDocCounts(self, filename):
        """Convenience wrapper to load the model object and the top topic item word document
        counts from multiple files, but just designate one base filename.
        """
        model = self.loadModel(filename);
        docCountByWordId = self.loadDocCountByWordId(self.topTopicFilename(filename));
        return (model, docCountByWordId);

    def itemCountByIdToBagOfWords(itemCountById, observedIds=None, itemsById=None, excludeCategoryIds=None ):
        """Return 2-ple (itemId, count) representation of item IDs, but filter out those in excluded set,
        or whose category looked up via itemsById is already observed previously or so far.
        """
        for itemId, itemCount in itemCountById.items():
            categoryId = None;
            if itemsById is not None and itemId in itemsById:
                categoryId = itemsById[itemId]["clinical_item_category_id"]
            if itemId not in observedIds and (excludeCategoryIds is None or categoryId not in excludeCategoryIds):
                yield (itemId, itemCount);    # Record presence of item
                observedIds.add(itemId);
    itemCountByIdToBagOfWords = staticmethod(itemCountByIdToBagOfWords);

    def bagOfWordsToCountById(bagOfWords):
        """Convert bag of words collection of 2-ple (itemId, count) representation into a dictionary of itemId: count mappings."""
        itemCountById = dict();
        for itemId, itemCount in bagOfWords:
            itemCountById[itemId] = itemCount;
        return itemCountById;
    bagOfWordsToCountById = staticmethod(bagOfWordsToCountById);

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile>    Name of input file, assume input is already in bag of words sparse vector format compatible with GenSim.\n"+\
                    "   <outputFile>   Binary / pickle output file to save model for reuse later.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-n", "--numTopics",  dest="numTopics", help="Numbers of topics to model.  Specify 0 to use non-parameteric Hierarchical Dirichlet Process model instead.");
        parser.add_option("-i", "--itemsPerCluster",  dest="itemsPerCluster", default=DEFAULT_TOPIC_ITEM_COUNT, help="Specify number of top topic words to store in an additional tab-delimited file with the top N words for each topic by score, as well as the total docCountByWordId.");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) >= 1:
            inputFilename = args[0];

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];

            corpusBOWGenerator = self.jsonGeneratorFromFile(stdOpen(inputFilename));

            # Parse some options
            numTopics = int(options.numTopics);

            # Main Model construction
            (model, docCountByWordId) = self.buildModel(corpusBOWGenerator, numTopics);

            # Save in binary format for reuse later
            model.save(outputFilename);

            # Save top topic information in readable tab-delimited format
            itemsPerCluster = int(options.itemsPerCluster);
            topicFile = stdOpen(self.topTopicFilename(outputFilename),"w");
            print(COMMENT_TAG, json.dumps({"argv":argv}), file=topicFile);    # Print comment line with analysis arguments to allow for deconstruction later
            self.printTopicsToFile(model, docCountByWordId, topicFile, itemsPerCluster);
            topicFile.close()

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = TopicModel();
    instance.main(sys.argv);
