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


class MyStreamListener(StreamListener):
    #on_status is shaddow by on_data
    def on_status(self, status):
        try:
            if hasattr(status, 'retweeted_status'):
                try:
                    tweet = status.retweeted_status.extended_tweet["full_text"]
                except:
                    tweet = status.retweeted_status.text
            else:
                try:
                    tweet = status.extended_tweet["full_text"]
                except AttributeError:
                    tweet = status.text

            tweet = tweet.replace(',', '')
            tweet = tweet.replace('\n', ' ')
            tweet = unidecode(tweet)

            username = status.user.screen_name
            time_ms = status.timestamp_ms
            print("on_status time_ms = ", time_ms)
            print("on_status username=", username)
            print("on_status tweet=", tweet)
            # output_csv.write_tweet(time_ms, username, tweet)
            # output_csv.print_tweet(time_ms, username, tweet)
        except KeyError as e:
            print(str(e))

        return True     

    def on_error(self, status):
        print("Error: ", status)

    def on_disconnect(self, notice):
        print("Disconnected: ", notice)
    
    def on_data(self, data):
        try:
            j = json.loads(data)
            if "delete" not in j:
                if j.get('source'):
                    print("source = ", j['source'])
                else:
                    print("source = None", j['source'])
                print("id_str = ", j['id_str'])
                print("text = ", j['text'])
                print("created_at = ", j['created_at'])
                if j.get('retweeted_status'):
                    print("in_reply_to_user_id_str = ", j['retweeted_status']['in_reply_to_user_id_str'])
                else:
                    print("in_reply_to_user_id_str = None")
                print("on_data favorite_count = ", j['favorite_count'])
                print("on_data retweeted = ", j['retweeted'])
                # screen_name = 'test'
                # with open('%s_tweets.txt' % screen_name, mode='w', newline='', encoding="utf-8") as f:
                #         json.dump(j, f)
        except KeyError as e:
            print(str(e))
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

    global output_csv
    # output_csv = Output(args.output, args.color, args.terse)
    settings.SEARCH_TERMS = args.keywords
    settings.SEARCH_LANG = args.languages
    # output_csv.print_banner()

    try:
        while True:
            auth = OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
            auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
            print('Time (ms)\tDate Time\tUsername\tTweet')
            print('---------------------------------------------------------------')
            twitter_stream = Stream(auth=auth, listener=MyStreamListener(), tweet_mode='extended')
            twitter_stream.filter(languages=settings.SEARCH_LANG, track=settings.SEARCH_TERMS)
    except Exception as e:
        print(str(e))
        time.sleep(5)
    except KeyboardInterrupt:
        print('Terminating Stream...')
        output_csv.__exit__()
        pass


if __name__ == '__main__':
    main()
