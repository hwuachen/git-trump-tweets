#!/usr/bin/env python
# encoding: utf-8
import tweepy  # https://github.com/tweepy/tweepy
import csv
import keys

# 200 is the maximum allowed count
Max_Tweet_Count = 200


def get_all_tweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets
    # with this method

    # authorize twitter, initialize tweepy
    # Twitter API credentials
    # consumer_key = 'your key'
    # consumer_secret = 'your secret'
    # access_token = 'your token'
    # access_token_secret = 'your token secret'

    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_key, keys.access_secret)

    # make initial request for most recent tweets
    # (200 is the maximum allowed count)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    new_tweets = api.user_timeline(
        screen_name=screen_name, count=Max_Tweet_Count, tweet_mode="extended")

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(
            screen_name=screen_name, count=Max_Tweet_Count,
            max_id=oldest, tweet_mode="extended")

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at,
                  tweet.full_text.encode("utf-8")]
                 for tweet in alltweets]

    # write the csv
    with open('%s_tweets.csv' % screen_name, mode='w',
              newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(['id_str', 'created_at', 'full_text'])
        # for record in outtweets:
        #    writer.writerow(record)
        writer.writerows(outtweets)


if __name__ == '__main__':
    # pass in the username of the account you want to download
    get_all_tweets("realDonaldTrump")
