import requests
from telegram import Update
from telegram.ext import CallbackContext
import config

def search_google(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur Google.')
        return

    try:
        google_search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={config.GOOGLE_API_KEY}&cx={config.GOOGLE_CSE_ID}"
        response = requests.get(google_search_url)
        if response.status_code == 200:
            search_data = response.json()
            results = search_data.get('items', [])
            message = f"Résultats Google pour '{query}':\n"
            for item in results:
                title = item.get('title')
                link = item.get('link')
                snippet = item.get('snippet')
                message += f"\n*{title}*\n{link}\n_{snippet}_\n"
            update.message.reply_text(message, parse_mode='Markdown')
        else:
            update.message.reply_text("Erreur lors de l'accès à l'API Google.")
    except Exception as e:
        update.message.reply_text(f"Erreur Google: {str(e)}")