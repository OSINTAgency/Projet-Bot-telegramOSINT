import sys
sys.path.append('../Pastepwnd')  # Assurez-vous que le chemin est correct

from pastepwnd import PastePwnd
import requests
from telegram import Update
from telegram.ext import CallbackContext
import logging
import os

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser PastePwnd
pastepwnd = PastePwnd()

def search_breaches(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une adresse email ou un nom d\'utilisateur pour la recherche.')
        return

    try:
        # Utiliser PastePwnd pour rechercher des violations
        breaches = pastepwnd.search(query)

        if breaches:
            message = f"Violations de données pour '{query}':\n"
            for breach in breaches:
                message += f"- {breach}\n"
            update.message.reply_text(message)
        else:
            update.message.reply_text(f"Aucune violation de données trouvée pour '{query}'.")

    except Exception as e:
        logger.error(f"Erreur lors de l'accès à PastePwnd: {e}")
        update.message.reply_text(f"Erreur lors de l'accès à PastePwnd: {str(e)}")