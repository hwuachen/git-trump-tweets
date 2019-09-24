import twitter
import pprint
import csv
import re
import keys
'''
consumer_key = 'cDAgU4Z0rsozQdi42caQygH3p'
consumer_secret = 'SL8slK40itsXcKK2pQSVChzei7tzFlTLoKaUtT2Ws3iP79h1Df'
access_token = '781935750183055361-gzWtt0scWq9VvBEqI794gBqjIqOa9VB'
access_token_secret = 'A1fPWtmeEDh9MiMkGbGgm1JeHrhZ5fzx4CAbSgmbqdfCq'
'''
api = twitter.Api(consumer_key=CONSUMER_KEY,  # 'Your consumer key'
                  consumer_secret=CONSUMER_SECRET,  # 'your consumer secret',
                  access_token_key=ACCESS_TOKEN,  # 'your access token key',
                  access_token_secret=ACCESS_SECRET)  # 'your token secret'

all_statuses = []
# get statuses, will get 200 at a time, let's go fetch 2000
statuses = api.GetUserTimeline(screen_name="realDonaldTrump",
                exclude_replies=True, trim_user=True, include_rts=False, count=2)
all_statuses.extend(statuses)
pprint.pprint(statuses)

for i in range(0, 9):
    statuses = api.GetUserTimeline(screen_name='realDonaldTrump', exclude_replies=True,
                                   trim_user=True, include_rts=False, count=200, max_id=statuses[-1].id)
    # pprint.pprint(statuses)
    all_statuses.extend(statuses)


with open('trump_tweets.csv', 'w') as csvfile:
    fieldnames = ['id', 'text', 'source']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for status in all_statuses:
        # sources come in as "<a href=""http://twitter.com"" rel=""nofollow"">Twitter Web Client</a>" so let's just get
        # the good stuff out
        cleaner_source = re.search("\>.+\<", status.source).group(0)
        clean_source = cleaner_source[1: -1]
        writer.writerow(
            {'id': status.id, 'text': status.text, 'source': clean_source})

print("Your status has " + str(len(all_statuses)) + " items ")
