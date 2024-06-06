import requests
from telegram import Update
from telegram.ext import CallbackContext

def search_ip(update: Update, context: CallbackContext) -> None:
    ip_address = ' '.join(context.args)
    if not ip_address:
        update.message.reply_text('Veuillez fournir une adresse IP pour la recherche.')
        return

    try:
        ip_api_url = f"https://ipinfo.io/{ip_address}/json"
        response = requests.get(ip_api_url)
        if response.status_code == 200:
            ip_data = response.json()
            formatted_data = json.dumps(ip_data, indent=2)
            update.message.reply_text(f"Informations IP pour '{ip_address}':\n{formatted_data}")
        else:
            update.message.reply_text("Erreur lors de l'accès à l'API IPinfo.")
    except Exception as e:
        update.message.reply_text(f"Erreur IP: {str(e)}")
