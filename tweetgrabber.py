import tweepy  # https://github.com/tweepy/tweepy
import csv
import settings
import json
import re
from pymongo import MongoClient

# 200 is the maximum allowed count
Max_Tweet_Count = 200

def get_all_tweets(screen_name):
    # Twitter API credentials
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    # Twitter only allows access to a users most recent 3240 tweets per call
    # other limit see https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
                    #proxy = "http://yourproxy:port")  

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

        oldest = new_tweets[-1].id - 1

        # update the id of the oldest tweet less one
        #alltweets.extend(new_tweets)
        toList(new_tweets, alltweets)        
        print("...%s tweets downloaded so far" % (len(alltweets)))
        print("Oldest iud so far = %s" % (oldest))
        
    print("total tweets count =", len(alltweets))
    writeToFile(alltweets, screen_name)
    writeToDB(alltweets, screen_name)


def toList(new_tweets, alltweets):
    for tweet in new_tweets:
        item = {}
        cleaner_source = re.search("\>.+\<", tweet._json['source']).group(0)
        clean_source = cleaner_source[1: -1]
        item["source"] = clean_source
        item["id_str"] = tweet._json["id_str"]
        item["text"] = tweet._json["full_text"]
        item["created_at"] = tweet._json["created_at"]
        item["retweet_count"] = tweet._json["retweet_count"]
        item["in_reply_to_user_id_str"] = tweet._json["in_reply_to_user_id_str"]
        item["favorite_count"] = tweet._json["favorite_count"]
        item["is_retweet"] = tweet._json["retweeted"]
        alltweets.append(item)

def writeToFile(alltweets, screen_name):
    #write to a json file
    with open('%s_tweets.json' % screen_name, mode='w',
        newline='', encoding="utf-8") as f:
        json.dump(alltweets, f)
    

def writeToDB(alltweets, screen_name):
      # write to DB, however inert_many always throw exception
    # db = MongoClient('localhost', 27017).charon
    # db.trump_tweets.create_index("id_str", unique = True)
    # db.trump_tweets.insert_many(mylist, ordered=False)
    if screen_name == "realDonaldTrump":
        with MongoClient('localhost', 27017) as connection:
            db = connection["charon"]
            collection = db["trump_tweets"]
            collection.create_index("id_str", unique = True)
            for item in alltweets:
                try:
                    db.trump_tweets.insert_one(item)
                except:
                    print("Duplicate key")
        print("Total trump tweets in DB = ", collection.count_documents({}))


if __name__ == '__main__':
    # pass in the username of the account you want to download
    get_all_tweets("realDonaldTrump")