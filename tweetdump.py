#!/usr/bin/env python
# encoding: utf-8
import tweepy  # https://github.com/tweepy/tweepy
import csv
import keys
import json
import re
from pymongo import MongoClient

# 200 is the maximum allowed count

#Issue 1 - every connection  download different number of tweets


Max_Tweet_Count = 200

def get_all_tweets(screen_name):
    # Twitter API credentials
    # consumer_key = 'your key'
    # consumer_secret = 'your secret'
    # access_token = 'your token'
    # access_token_secret = 'your token secret'
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    # Twitter only allows access to a users most recent 3240 tweets
    # with this method
    # authorize twitter, initialize tweepy
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # save the id of the oldest tweet less one
    oldest = 0

    # keep grabbing tweets until there are no tweets left to grab
    while True:
        new_tweets = []
        print("getting tweets before %s" % (oldest))
        # all subsequent requests use the max_id param to prevent duplicates
        if oldest == 0:
            new_tweets = api.user_timeline(screen_name=screen_name,
                                           count=Max_Tweet_Count,
                                           tweet_mode="extended")
        else:
            new_tweets = api.user_timeline(screen_name=screen_name,
                                           count=Max_Tweet_Count,
                                           max_id=oldest,
                                           tweet_mode="extended")
        if (len(new_tweets) <= 0):
            break        
        # update the id of the oldest tweet less one
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        print("...%s tweets downloaded so far" % (len(alltweets)))
        print("Oldest iud so far = %s" % (oldest))
        
    print("total tweets count =", len(alltweets))
    write_Tweets(alltweets, screen_name)


def write_Tweets(alltweets, screen_name):
    mylist = []
    for tweet in alltweets:
        a = {}
        cleaner_source = re.search("\>.+\<", tweet._json['source']).group(0)
        clean_source = cleaner_source[1: -1]
        a["source"] = clean_source
        a["id_str"] = tweet._json["id_str"]
        a["text"] = tweet._json["full_text"]
        a["created_at"] = tweet._json["created_at"]
        a["retweet_count"] = tweet._json["retweet_count"]
        a["in_reply_to_user_id_str"] = tweet._json["in_reply_to_user_id_str"]
        a["favorite_count"] = tweet._json["favorite_count"]
        a["is_retweet"] = tweet._json["retweeted"]
        mylist.append(a)

    #write to a file
    with open('%s_tweets.json' % screen_name, mode='w',
        newline='', encoding="utf-8") as f:
        json.dump(mylist, f)
    
    # write to DB, however inert_many always throw exception
    # db = MongoClient('localhost', 27017).charon
    # db.trump_tweets.create_index("id_str", unique = True)
    # db.trump_tweets.insert_many(mylist, ordered=False)
    with MongoClient('localhost', 27017) as connection:
        db = connection["charon"]
        collection = db["trump_tweets"]
        collection.create_index("id_str", unique = True)
        for item in mylist:
            try:
                db.trump_tweets.insert_one(item)
            except:
                print("Duplicate key")
    
    print("Total trump tweets in DB = ", collection.count_documents({}))

if __name__ == '__main__':
    # pass in the username of the account you want to download
    get_all_tweets("realDonaldTrump")
        
