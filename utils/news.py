# utils/news.py

import requests
from telegram import Update
from telegram.ext import CallbackContext
import config

def search_news(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche de nouvelles.')
        return

    try:
        # Exemple de recherche d'actualités avec une API publique
        # Remplacez par l'API de votre choix
        news_api_url = f"https://newsapi.org/v2/everything?q={query}&apiKey={config.NEWS_API_KEY}"
        response = requests.get(news_api_url)
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])
            if articles:
                formatted_articles = '\n\n'.join([f"{article['title']}\n{article['url']}" for article in articles[:5]])
                update.message.reply_text(f"Résultats de la recherche de nouvelles pour '{query}':\n{formatted_articles}")
            else:
                update.message.reply_text(f"Aucun résultat trouvé pour '{query}'.")
        else:
            update.message.reply_text("Erreur lors de l'accès à l'API des nouvelles.")
    except Exception as e:
        update.message.reply_text(f"Erreur de recherche de nouvelles: {str(e)}")