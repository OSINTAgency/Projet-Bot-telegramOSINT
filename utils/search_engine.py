import requests
from telegram import Update
from telegram.ext import CallbackContext
import config

def search_engine(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur les moteurs de recherche.')
        return

    try:
        search_api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={config.GOOGLE_API_KEY}&cx={config.CUSTOM_SEARCH_ENGINE_ID}"
        response = requests.get(search_api_url)
        if response.status_code == 200:
            search_data = response.json()
            formatted_data = json.dumps(search_data, indent=2)
            update.message.reply_text(f"Résultats de la recherche pour '{query}':\n{formatted_data}")
        else:
            update.message.reply_text("Erreur lors de l'accès à l'API de recherche Google.")
    except Exception as e:
        update.message.reply_text(f"Erreur de recherche Google: {str(e)}")
