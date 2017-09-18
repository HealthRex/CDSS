"""Simple experiments with pager text data.
"""
import sys, os;
from wordcloud import WordCloud
import urllib;
from medinfo.common.Util import ProgressDots;
from medinfo.db import DBUtil;

# Minimum number of times word should appear to include it
COUNT_THRESHOLD = 100;

# Number of words to fit into word cloud
TOP_WORDS_TO_SHOW = 40;


# Construct a set of stop words not interested in
stopWords = set();
if len(sys.argv) > 1:
	stopWordFile = open(sys.argv[1]);	# "stopWords.txt";
	stopWords = set(stopWordFile.read().split());

countPerToken = dict();

conn = DBUtil.connection();
cursor = conn.cursor();
try:
	query = \
		"""select stride_pager_message_id, date_entered, messaging_id, name, message_text 
		from stride_pager_message
		where message_text !~ 'covering for ID'
		limit 100000
		""";
	cursor.execute(query);

	prog = ProgressDots();
	row = cursor.fetchone();
	while row is not None:
		pagerText = row[-1];
		tokens = pagerText.split();
		for iToken, token in enumerate(tokens):
			tokens[iToken] = token.strip("#?:!.,;").lower();	# Remove flanking punctuations. Case insensitive
		for token in tokens:
			if token not in stopWords and len(token) > 1:	# Skip stop words and single character words
				if token not in countPerToken:
					countPerToken[token] = 0;
				countPerToken[token] += 1;
		row = cursor.fetchone();
		prog.update();
	prog.printStatus();
finally:
	cursor.close();
	conn.close();


# Only look at common words with more instances and write as sortable tuples
countTokens = list();
for token, count in countPerToken.iteritems():
	if count >= COUNT_THRESHOLD:
		countTokens.append( (count, token) );
countTokens.sort(reverse=True);

truncatedCountPerToken = dict();
for iToken, (count, token) in enumerate(countTokens):
	print "%s\t%s" % (count, token);
	if iToken < TOP_WORDS_TO_SHOW:
		truncatedCountPerToken[token] = count;

# Generate a word cloud image
wordcloud = WordCloud(width=1000, height=1000).generate_from_frequencies(truncatedCountPerToken);

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# lower max_font_size
#wordcloud = WordCloud(max_font_size=40).generate(text)
#plt.figure()
#plt.imshow(wordcloud, interpolation="bilinear")
#plt.axis("off")
plt.show()

















