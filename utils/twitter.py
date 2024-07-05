import requests
from telegram import Update
from telegram.ext import CallbackContext
import config
import json
import tweepy

        def search_twitter(query: str, count: int = 10) -> list:
            consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
            consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)

            tweets = api.search_tweets(q=query, count=count)
            return [{"text": tweet.text, "user": tweet.user.screen_name} for tweet in tweets]