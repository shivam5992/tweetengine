from gevent import monkey
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
from textblob import TextBlob
from threading import *
import sys, codecs, re
from TwitterAPI import TwitterAPI, TwitterRestPager
from tweetprocess import *
from pprint import pprint
import json

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
monkey.patch_all()

def cleaned(text):
    text = improve_repeated(remove_url(escape(text)))
    text = remove_special(text)
    text = str(re.sub(' +',' ',text))
    return text

def track_words(text):
    for word in text.split():
        if word.lower() in positives:
            pos_tracked.append(word)
        elif word.lower() in negatives:
            neg_tracked.append(word)

def flat(lis):
    return list(set(lis))

def roundoff(data):
  return "%.2f" % data

def lexical_density(text):
  consider = ['JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS', 'NNPS', 'RB', 'RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']
  blob = TextBlob(text)
  nlex = 0
  n = len(blob.words)
  for tags in blob.tags:
    if str(tags[1]) in consider:
      nlex += 1
  ld = (float(nlex)/n) * 100
  return "%.2f" % ld, nlex

def horizon(text):
  return len(re.findall("\d+", text))

def background_thread(r):
    tweet_length, tweet_count = 0, 0
    hashtags_count, user_count = 0, 0
    mentions_count, negsentiment, possentiment = 0, 0, 0
    retweets, hc = 0, 0

    for item in r:
        tweet_text = item['text'] if 'text' in item else item
        if type(tweet_text) != dict:
          tweet_text = tweet_text.encode("utf-8").decode("ascii","ignore")
          cleaned_tweet = cleaned(tweet_text)
          track_words(cleaned_tweet)
          pos_score, neg_score = len(pos_tracked), len(neg_tracked)

          tweet_count += 1
          tweet_length += len(cleaned_tweet)
          avg_tweet_length = tweet_length/tweet_count

          for tags in item['entities']['hashtags']:
              if tags['text'] not in hashtags_tracker:
                  hashtags_tracker.append(tags['text'])

          for tags in item['entities']['user_mentions']:
              if tags['screen_name'] not in mentions_tracker:
                  mentions_tracker.append(tags['screen_name'])

          hashtags_count = len(hashtags_tracker)
          mentions_count = len(mentions_tracker)

          if item['user']['name'] not in user_tracked:
              user_tracked.append(item['user']['name'])
          user_count = len(user_tracked)
          blob = TextBlob(cleaned_tweet)

          word_count = len(blob.words)
                  
          for sentence in blob.sentences:
            score = sentence.sentiment.polarity
            if score < 0:
              negsentiment += score
            elif score > 0:
              possentiment += score

          sentiment_polarity = possentiment + negsentiment
          sentiment_polarity = "%.2f" % float(sentiment_polarity)
          
          possentimentres = roundoff(possentiment)
          negsentimentres = roundoff(negsentiment)  

          S = tweet_count
          L = tweet_length
          CLI = 0.058 * L - 0.296 * S - 15.8
          CLI = roundoff(CLI)

          chrs = tweet_length
          wds = word_count
          snts = tweet_count
          ARI = 4.71 * ( float(chrs)/wds ) + 0.5 * ( float(wds)/snts ) - 21.43
          ARI = roundoff(ARI)

          optimism =  roundoff(float(pos_score)/word_count)
          pessimism = roundoff(float(neg_score)/word_count)

          if item['retweeted'] == True:
            retweets += 1

          ld, nlex = lexical_density(cleaned_tweet)
          loc = item['user']['location']
          hc += horizon(cleaned_tweet)

          tweetify = {
           "original_tweet": tweet_text,
           "cleaned_tweet": cleaned_tweet,
           "positive_words": flat(pos_tracked),
           "negative_words": flat(neg_tracked),
           "optimism": optimism,
           "pessimism": pessimism,
           "tweet_count": tweet_count,
           "average_tweet_length": avg_tweet_length,
           "mentions": flat(mentions_tracker),
           "hashtags": flat(hashtags_tracker),
           "mentions_count": mentions_count,
           "hashtags_count": hashtags_count,
           "user_tracked": user_tracked,
           "user_count": user_count,
           "sentiment_polarity":sentiment_polarity,
           "positivity": possentimentres,
           "negativity": negsentimentres,
           "CLI1":CLI,
           "ARI1":ARI,
           "word_count":word_count,
           "retweets":retweets,
           "lexical":ld,
           "location1":loc,
           "horizon":hc,
           "lwd":nlex
          }

          json_encoded = json.dumps(tweetify)
          socketio.emit('my response',
                        {'data': 'Server generated event', 'jss': json_encoded }, namespace='/test')

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
      tosearch = "#" + request.form['ht']
      r = api.request('statuses/filter', {'track': tosearch})
      p = Thread(target=background_thread, args = (r,))
      p.start()
      return render_template('index.html', tag = tosearch, home=False)
    return render_template('index.html', home=True, tag=None)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    positives = open("data/positives.txt").read().split()
    negatives = open("data/negatives.txt").read().split()
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    data = open("tokens.txt").read().split("\n")
    consumer_key = data[0]
    consumer_secret = data[1]
    access_token_key = data[2]
    access_token_secret = data[3]
    api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
    pos_tracked, neg_tracked = [], []
    hashtags_tracker, mentions_tracker = [], []
    user_tracked = []
    socketio.run(app)


