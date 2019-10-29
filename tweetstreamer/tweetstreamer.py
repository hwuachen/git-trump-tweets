import argparse
import datetime
import sys
import time
import settings
import json
#from output import Output
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from unidecode import unidecode
from pymongo import MongoClient
import re

class MyStreamListener(StreamListener):      
    def on_error(self, status):
        print("Error: ", status)

    def on_disconnect(self, notice):
        print("Disconnected: ", notice)
    
    def on_data(self, tweet):
        try:
            data = json.loads(tweet)
            if 'extended_tweet' in data:
                # print("Decoding extended tweet from Streaming API.")
                text = data['extended_tweet']['full_text']
            elif 'full_text' in data:
                # print("Decoding extended tweet from REST API.")
                text = data['full_text']
            else:
                #print("Decoding short tweet.")
                text = data['text']
           
            #source = re.search("\>.+\<", data['source']).group(0)
            source = data['source']
            id_str = data['id_str']
            screen_name = data['user']['screen_name']
            created_at = data['created_at']
            retweet_count = data['retweet_count']
            in_reply_to_user_id_str = data['in_reply_to_user_id_str']
            favorite_count = data['favorite_count']
            is_retweet = data['retweeted']          
            
            document_record = {'source':source, 'id_str': id_str, 'text':text, 
                    'created_at':created_at, 'retweet_count':retweet_count, 
                    'in_reply_to_user_id_str':in_reply_to_user_id_str,
                    'favorite_count':favorite_count,
                    'is_retweet':is_retweet }
            db = MongoClient('localhost', 27017).News

            if screen_name == 'realDonaldTrump':                
                db.trumptweet.insert_one(document_record)
                print("source = ", source)
                print("id_str = ", id_str)
                print("text= ", text)
                print("created_at = ", created_at)
                print("retweet_count = ", retweet_count)                                   
                print("in_reply_to_user_id_str= ", in_reply_to_user_id_str)
                print("favorite_count= ", favorite_count)
                print("is_retweet = ", is_retweet)
                print("screen_name = ", screen_name)

            elif screen_name == 'Sunny23112519':
                db.mytweet.insert_one(document_record)
                print("source = ", source)
                print("id_str = ", id_str)
                print("text= ", text)
                print("created_at = ", created_at)
                print("retweet_count = ", retweet_count)                                   
                print("in_reply_to_user_id_str= ", in_reply_to_user_id_str)
                print("favorite_count= ", favorite_count)
                print("is_retweet = ", is_retweet)
                print("screen_name = ", screen_name)

            # else:
            #     document_record = {'source':source, 'id_str': id_str, 'text':text, 
            #         'created_at':created_at, 'retweet_count':retweet_count, 
            #         'in_reply_to_user_id_str':in_reply_to_user_id_str,
            #         'favorite_count':favorite_count,
            #         'is_retweet':is_retweet }
            #     db.followers.insert_one(document_record)
            
            # print("source = ", source)
            # print("id_str = ", id_str)
            # print("text= ", text)
            # print("created_at = ", created_at)
            # print("retweet_count = ", retweet_count)                                   
            # print("in_reply_to_user_id_str= ", in_reply_to_user_id_str)
            # print("favorite_count= ", favorite_count)
            # print("is_retweet = ", is_retweet)
            # print("screen_name = ", screen_name)

        except KeyError:
            print("Malformed tweet: %s" % data)
    
        return True

def check_keys():
    if (not settings.CONSUMER_KEY) or (not settings.CONSUMER_SECRET) or (not settings.ACCESS_TOKEN) or \
            (not settings.ACCESS_SECRET):
        return False
    return True


def run_setup():
    print("Beginning setup process:")
    print("You will be prompted to enter in your API keys for Twitter.")
    print("WARNING: These will overwrite the existing values, if any exist.")
    settings.CONSUMER_KEY = input("Enter your Consumer Key: ")
    settings.CONSUMER_SECRET = input("Enter your Consumer Secret: ")
    settings.ACCESS_TOKEN = input("Enter your Access Token: ")
    settings.ACCESS_SECRET = input("Enter your Access Secret: ")
    print("Settings have been saved. Terminating...")
    modify_settings()
    sys.exit(0)


def modify_settings():
    f = open('settings.py', 'w')
    f.write('"""Twitter API Credentials"""\n')
    f.write("CONSUMER_KEY = \'" + settings.CONSUMER_KEY + "\'\n")
    f.write("CONSUMER_SECRET = '" + settings.CONSUMER_SECRET + "\'\n")
    f.write("ACCESS_TOKEN = \'" + settings.ACCESS_TOKEN + "\'\n")
    f.write("ACCESS_SECRET = \'" + settings.ACCESS_SECRET + "\'\n")
    f.write('\n')
    f.write('"""Default values used when filtering for specified tweets"""')
    f.write('"""Vowels used to select for any tweet"""\n')
    f.write('SEARCH_TERMS = ["a", "e", "i", "o", "u"]\n')
    f.write('\n')
    f.write('"""Search Language: Language filtered for specified tweets"""\n')
    f.write('SEARCH_LANG = ["en"]\n')
    f.write('\n')
    current_dt = datetime.datetime.now()
    f.write('API Credentials Updated: ' + current_dt.strftime('%m-%d-%Y %H:%M:%S'))


def parse_args():
    argpar = argparse.ArgumentParser(prog='Tweet Streamer',
                                     usage='Script designed to stream tweets using specified keywords')
    argpar.add_argument('-o', '--output', nargs='?', action='store', dest='output', default='output',
                        help='Saves tweets as specified file name')
    argpar.add_argument('-t', '--terse', action='store_true', dest='terse', default=False,
                        help='Disables outputting tweets to console')
    argpar.add_argument('-c', '--color', action='store_true', dest='color', default=False,
                        help='Enables colored text in console')
    argpar.add_argument('-v', '--version', help='Displays current version')
    argpar.add_argument('-k', '--keywords', nargs='+', type=str, action='store', dest='keywords',
                        default=settings.SEARCH_TERMS, help='Filter tweets by the specified keywords')
    argpar.add_argument('-l', '--language', nargs='+', type=str, action='store', dest='languages',
                        default=settings.SEARCH_LANG, help='Filter tweets by the specified language.')
    argpar.add_argument('-s', '--setup', action='store_true', dest='setup', default=False,
                        help='Begins the setup process')
    args = argpar.parse_args()
    return args


def main():
    args = parse_args()

    if not check_keys() or args.setup:
        run_setup()

    settings.SEARCH_TERMS = args.keywords
    settings.SEARCH_LANG = args.languages

    client  = MongoClient('localhost', 27017)
    print ('Connected successfully to MongoDB!')
    db=client["News"]

    try:
        while True:
            auth = OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
            auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
            print('Time (ms)\tDate Time\tUsername\tTweet')
            print('---------------------------------------------------------------')
            twitter_stream = Stream(auth=auth, listener=MyStreamListener(), tweet_mode='extended')
            # twitter_stream.filter(languages=settings.SEARCH_LANG, track=settings.SEARCH_TERMS)
            # twitter_stream.filter(languages=settings.SEARCH_LANG,follow=["25073877", "781935750183055361"])
            twitter_stream.filter(follow=["781935750183055361"])
    except Exception as e:
        print(str(e))
        time.sleep(5)
    except KeyboardInterrupt:
        print('Terminating Stream...')
        output_csv.__exit__()
        pass


if __name__ == '__main__':
    main()
