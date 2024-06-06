import tweepy
from telegram import Update
from telegram.ext import CallbackContext
import config

def search_twitter(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur Twitter.')
        return

    # Authentification Twitter
    auth = tweepy.OAuth1UserHandler(
        config.TWITTER_API_KEY,
        config.TWITTER_API_SECRET_KEY,
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    try:
        tweets = api.search_tweets(q=query, count=10)
        results = [f"Tweet de {tweet.user.screen_name}: {tweet.text}" for tweet in tweets]
        update.message.reply_text("\n\n".join(results))
    except Exception as e:
        update.message.reply_text(f"Erreur lors de la recherche Twitter: {str(e)}")
import requests
from telegram import Update
from telegram.ext import CallbackContext
import config
import json

def search_twitter(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur Twitter.')
        return

    try:
        twitter_api_url = f"https://api.twitter.com/2/tweets/search/recent?query={query}"
        headers = {"Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}"}
        response = requests.get(twitter_api_url, headers=headers)
        if response.status_code == 200:
            twitter_data = response.json()
            formatted_data = json.dumps(twitter_data, indent=2)
            update.message.reply_text(f"Résultats Twitter pour '{query}':\n{formatted_data}")
        else:
            update.message.reply_text("Erreur lors de l'accès à l'API Twitter.")
    except Exception as e:
        update.message.reply_text(f"Erreur Twitter: {str(e)}")
