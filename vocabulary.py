import csv
import nltk
from pprint import pprint

grouped_by_source = {}

with open('trump_tweets.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        text = row['text']
        platform = row['source']

        try:
            grouped_by_source[platform] = grouped_by_source[platform] + "".join(text)
        except KeyError:
            grouped_by_source[platform] = "".join(text)



# pprint(grouped_by_source)
tokenized = {}
tweet_tokenizer = nltk.tokenize.casual.TweetTokenizer()
random_punct = ["!", ",", ":", ".", "—", "&", "?", "\'", "\"", ")", "(", "’"]
stopwords = nltk.corpus.stopwords.words('english')

for key, value in grouped_by_source.items():
    #strip out stop words and random punctuation
    tokenized[key] = [w for w in tweet_tokenizer.tokenize(value) if w.lower() not in stopwords and w not in random_punct]

for key,value in tokenized.items():
    # bigrams = nltk.bigrams(value)
    # freq_dist_bigrams = nltk.FreqDist(bigrams)
    freq_dist = nltk.FreqDist(value)
    # pprint(key)
    pprint(freq_dist.most_common(10))
    # pprint(freq_dist_bigrams.most_common(10))
