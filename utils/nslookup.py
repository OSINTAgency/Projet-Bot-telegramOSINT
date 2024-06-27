import subprocess
from telegram import Update
from telegram.ext import CallbackContext
import logging
import re

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_query(query: str) -> bool:
    # Validate domain name or IP address format
    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,6}$"
    )
    ip_pattern = re.compile(
        r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    )
    return domain_pattern.match(query) is not None or ip_pattern.match(query) is not None

def nslookup_query(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour nslookup.')
        return

    if not is_valid_query(query):
        update.message.reply_text('Requête invalide. Veuillez fournir un nom de domaine ou une adresse IP valide.')
        return

    try:
        result = subprocess.run(['nslookup', query], capture_output=True, text=True, check=True)
        update.message.reply_text(f"Résultats de nslookup pour '{query}':\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur nslookup: {e}")
        update.message.reply_text(f"Erreur lors de l'exécution de nslookup: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        update.message.reply_text(f"Erreur inattendue : {str(e)}")
