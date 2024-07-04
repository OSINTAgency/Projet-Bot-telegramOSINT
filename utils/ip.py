import requests
from telegram import Update
from telegram.ext import CallbackContext
import json
import re

def is_valid_ip(ip_address: str) -> bool:
    # Valider le format de l'adresse IP (IPv4 et IPv6)
    ip_pattern = re.compile(
        r"^(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}|"
        r"(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|"
        r"(?:[a-fA-F0-9]{1,4}:){1,7}:|"
        r"(?:[a-fA-F0-9]{1,4}:){1,6}:[a-fA-F0-9]{1,4}|"
        r"(?:[a-fA-F0-9]{1,4}:){1,5}(?::[a-fA-F0-9]{1,4}){1,2}|"
        r"(?:[a-fA-F0-9]{1,4}:){1,4}(?::[a-fA-F0-9]{1,4}){1,3}|"
        r"(?:[a-fA-F0-9]{1,4}:){1,3}(?::[a-fA-F0-9]{1,4}){1,4}|"
        r"(?:[a-fA-F0-9]{1,4}:){1,2}(?::[a-fA-F0-9]{1,4}){1,5}|"
        r"[a-fA-F0-9]{1,4}:(?:(?::[a-fA-F0-9]{1,4}){1,6})|"
        r":(?:(?::[a-fA-F0-9]{1,4}){1,7}|:))$"
    )
    return ip_pattern.match(ip_address) is not None

def search_ip(update: Update, context: CallbackContext) -> None:
    ip_address = ' '.join(context.args)
    if not ip_address:
        update.message.reply_text('Veuillez fournir une adresse IP pour la recherche.')
        return

    if not is_valid_ip(ip_address):
        update.message.reply_text('Adresse IP invalide. Veuillez fournir une adresse IP valide.')
        return

    try:
        ip_api_url = f"https://ipinfo.io/{ip_address}/json"
        response = requests.get(ip_api_url)
        response.raise_for_status()
        ip_data = response.json()
        formatted_data = json.dumps(ip_data, indent=2)
        update.message.reply_text(f"Informations IP pour '{ip_address}':\n{formatted_data}")
    except requests.RequestException as e:
        update.message.reply_text(f"Erreur lors de l'accès à l'API IPinfo: {str(e)}")
    except json.JSONDecodeError:
        # Essayer d'obtenir le message d'erreur à partir du contenu de la réponse
        error_message = response.text if response.text else "Erreur de décodage JSON inconnue."
        update.message.reply_text(f"Erreur de décodage JSON des données de l'API: {error_message}")
    except Exception as e:
        update.message.reply_text(f"Erreur inattendue : {str(e)}")
