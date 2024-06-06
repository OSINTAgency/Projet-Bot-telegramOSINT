import requests
from telegram import Update
from telegram.ext import CallbackContext
import config

def search_breaches(update: Update, context: CallbackContext) -> None:
    email = ' '.join(context.args)
    if not email:
        update.message.reply_text('Veuillez fournir une adresse email pour la recherche de fuites de données.')
        return

    try:
        hibp_api_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"hibp-api-key": config.HIBP_API_KEY}
        response = requests.get(hibp_api_url, headers=headers)
        if response.status_code == 200:
            breach_data = response.json()
            formatted_data = json.dumps(breach_data, indent=2)
            update.message.reply_text(f"Données compromises pour '{email}':\n{formatted_data}")
        elif response.status_code == 404:
            update.message.reply_text("Aucune fuite de données trouvée pour cet email.")
        else:
            update.message.reply_text(f"Erreur HIBP: {response.status_code}")
    except Exception as e:
        update.message.reply_text(f"Erreur HIBP: {str(e)}")
