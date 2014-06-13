import sys, codecs, re
from textblob import TextBlob

from TwitterAPI import TwitterAPI, TwitterRestPager
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
data = open("tokens.txt").read().split("\n")
consumer_key = data[0]
consumer_secret = data[1]
access_token_key = data[2]
access_token_secret = data[3]
api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
pager = TwitterRestPager(api, 'search/tweets', {'q': 'modi', 'count': 1})

r = api.request('statuses/filter', {'track': 'modi'})

# def lexical_density(text):
# 	consider = ['JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS', 'NNPS', 'RB', 'RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']
# 	blob = TextBlob(text)
# 	nlex = 0
# 	n = len(blob.words)
# 	for tags in blob.tags:
# 		if str(tags[1]) in consider:
# 			nlex += 1
# 	ld = (float(nlex)/n) * 100
# 	return "%.2f" % ld

def hc(text):
	import re
	print len(re.findall("\d+", text))

print hc("hello modi ji you are awesome WC2014")

# for item in r:
# 	print "", item['user']['location']