import requests
from telegram import Update
from telegram.ext import CallbackContext
import logging
import os

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API key from environment variable or config file
LEAKCHECK_API_KEY = os.environ.get('LEAKCHECK_API_KEY')

def search_breaches(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une adresse email ou un nom d\'utilisateur pour la recherche.')
        return

    try:
        headers = {
            'Authorization': f'Bearer {LEAKCHECK_API_KEY}'
        }
        api_url = f"https://leakcheck.net/api?key={LEAKCHECK_API_KEY}&check={query}"
        response = requests.get(api_url, headers=headers)

        # Check for HTTP errors
        response.raise_for_status()

        breach_data = response.json()

        if breach_data['success']:
            breaches = breach_data['result']
            if breaches:
                message = f"Violations de données pour '{query}':\n"
                # Use a table to format the breaches
                for breach in breaches:
                    message += f"- {breach}\n"
                update.message.reply_text(message)
            else:
                update.message.reply_text(f"Aucune violation de données trouvée pour '{query}'.")
        else:
            update.message.reply_text(f"Erreur de l'API LeakCheck: {breach_data['error']}")

    except requests.exceptions.HTTPError as e:
        logger.error(f"Erreur HTTP lors de l'accès à l'API LeakCheck: {e}")
        update.message.reply_text(f"Erreur lors de l'accès à l'API LeakCheck: {str(e)}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'accès à l'API LeakCheck: {e}")
        update.message.reply_text(f"Erreur lors de l'accès à l'API LeakCheck: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        update.message.reply_text(f"Erreur inattendue : {str(e)}")