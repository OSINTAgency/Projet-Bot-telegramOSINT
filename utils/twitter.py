import requests
from telegram import Update
from telegram.ext import CallbackContext
import config
import json

def search_twitter(update: Update, context: CallbackContext) -> None:
    """
    Recherche de tweets récents sur Twitter correspondant à une requête donnée.
    
    Args:
        update (Update): L'objet Update contenant les informations de la requête.
        context (CallbackContext): Le contexte de la commande contenant les arguments.
    """
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur Twitter.')
        return

    try:
        # URL de l'API Twitter pour la recherche de tweets récents
        twitter_api_url = f"https://api.twitter.com/2/tweets/search/recent?query={query}"
        headers = {"Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}"}
        
        # Effectuer la requête à l'API Twitter
        response = requests.get(twitter_api_url, headers=headers)
        response.raise_for_status()
        
        # Traitement de la réponse
        twitter_data = response.json()
        if 'data' in twitter_data:
            results = [f"Tweet de {tweet['author_id']}: {tweet['text']}" for tweet in twitter_data['data']]
            update.message.reply_text("\n\n".join(results))
        else:
            update.message.reply_text(f"Aucun résultat trouvé pour '{query}'.")
    except requests.exceptions.RequestException as e:
        update.message.reply_text(f"Erreur lors de l'accès à l'API Twitter: {str(e)}")
    except Exception as e:
        update.message.reply_text(f"Erreur Twitter: {str(e)}")