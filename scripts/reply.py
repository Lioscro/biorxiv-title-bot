import os
import random

import tweepy
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from generate import generate_and_decode
from tweet import authenticate, format_tweet

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

# Mentions should be of the following form.
# [category] seed
# and @biorxivbot somewhere

def parse_tweet(tweet):
    # split by space
    split = tweet.strip().split(' ')

    # parse
    category = None
    seed_words = []
    for word in split:
        if word.startswith('[') and word.endswith(']'):
            category = word[1:-1]
        elif word.startswith(('@', '#')):
            continue
        else:
            seed_words.append(word)

    # if tweet contains brackets, but category couldn't be parsed,
    # raise exception
    if ('[' in tweet or ']' in tweet) and category is None:
        raise Exception('Failed to parse category.')

    return category, ' '.join(seed_words)

def fetch_mentions(api):
    # Get most recent tweet's datetime
    last_tweet_datetime = api.user_timeline(count=1)[0].created_at

    fetched = []
    count = 20
    max_id = None
    done = False
    while not done:
        mentions = api.mentions_timeline(max_id=max_id, count=count)
        # Fetch mentions that were made after the last reply, and ignore
        # any replies.
        for mention in mentions:
            if mention.created_at >= last_tweet_datetime and mention.in_reply_to_status_id is None:
                fetched.append(mention)
            else:
                done = True
                break
        if len(mentions) < count:
            break
        max_id = str(mentions[-1].id - 1)

    return fetched

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('model_dir')
    args = parser.parse_args()
    data_dir = args.data_dir
    model_dir = args.model_dir

    with open(os.path.join(data_dir, 'categories.txt'), 'r') as f:
        categories = [line.strip() for line in f if not line.isspace()]
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

    for mention in fetch_mentions(api):
        try:
            category, seed = parse_tweet(mention.text)
            category, generated = generate_and_decode(
                model, tokenizer, category, seed
            )
            reply = format_tweet(tags.get(category), generated)
        except:
            reply = (
                'I couldn\'t understand that. Try mentioning me again in this '
                'format: "[Optional category] Some seed phrase". See '
                'https://github.com/Lioscro/biorxiv-title-bot/blob/main/data/categories.txt '
                'for category options.'
            )
        try:
            api.update_status(
                reply,
                in_reply_to_status_id=mention.id_str,
                auto_populate_reply_metadata=True,
            )
        except:
            pass
