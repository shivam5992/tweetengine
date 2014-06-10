from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
# from textblob import TextBlob

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


import sys, codecs
from TwitterAPI import TwitterAPI, TwitterRestPager
from tweetprocess import *
from pprint import pprint
import json

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

def background_thread(pager):
    tweet_length = 0
    tweet_count = 0
    hashtags_count = 0
    user_count = 0
    mentions_count = 0
    negsentiment = 0
    possentiment = 0

    
    for item in pager.get_iterator():

        tweet_text = item['text'] if 'text' in item else item
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

                
        # blob = TextBlob(cleaned)
        # for sentence in blob.sentences:
        #   score = sentence.sentiment.polarity
        #   if score < 0:
        #     negsentiment += score
        #   elif score > 0:
        #     possentiment += score


        tweetify = {
         "original_tweet": tweet_text,
         "cleaned_tweet": cleaned_tweet,
         "positive_words": flat(pos_tracked),
         "negative_words": flat(neg_tracked),
         "total_positive_words": pos_score,
         "total_negative_words": neg_score,
         "tweet_count": tweet_count,
         "average_tweet_length": avg_tweet_length,
         "mentions": flat(mentions_tracker),
         "hashtags": flat(hashtags_tracker),
         "mentions_count": mentions_count,
         "hashtags_count": hashtags_count,
         "user_tracked": user_tracked,
         "user_count": user_count
        }

        json_encoded = json.dumps(tweetify)

        socketio.emit('my response',
                      {'data': 'Server generated event', 'jss': json_encoded },
                      namespace='/test')

@app.route('/d')
def d():
  return render_template('untitled.html')
@app.route('/d1')
def d1():
  return render_template('bul.html')

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
      tosearch = "#" + request.form['ht']
      pager = TwitterRestPager(api, 'search/tweets', {'q': tosearch, 'count': 1})

      ## Here kill any previously running thread
      p = Thread(target=background_thread, args = (pager,))
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


