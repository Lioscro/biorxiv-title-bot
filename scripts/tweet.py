import os
import random

import tweepy
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from generate import generate_and_decode

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

def format_tweet(tags, generated):
    # Tags aren't working great right now turn off.
    # return f'{generated} {tags}' if category else generated
    print(generated)
    return generated

def authenticate(consumer_key, consumer_secret, access_key, access_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return auth, api

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('model_dir')
    parser.add_argument('-c')
    parser.add_argument('-s')
    parser.add_argument('-t')
    args = parser.parse_args()
    data_dir = args.data_dir
    model_dir = args.model_dir
    category = args.c
    seed = args.s
    tweet_id = args.t

    with open(os.path.join(data_dir, 'categories.txt'), 'r') as f:
        categories = [line.strip() for line in f if not line.isspace()]
    if category and category not in categories:
        raise Exception(f'Unknown category: {category}')
    with open(os.path.join(data_dir, 'tags.txt'), 'r') as f:
        tags = {
            category: ts
            for category, ts in zip(categories, [line.strip() for line in f])
        }

    auth, api = authenticate(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
    )

    model = GPT2LMHeadModel.from_pretrained(model_dir)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    category = category or random.choice(categories)
    category, generated = generate_and_decode(
        model, tokenizer, category, seed
    )
    tweet = format_tweet(tags.get(category), generated)
    if tweet_id:
        api.update_status(
            tweet,
            in_reply_to_status_id=tweet_id,
            auto_populate_reply_metadata=True,
        )
    else:
        api.update_status(tweet)
