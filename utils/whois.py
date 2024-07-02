import whois
from telegram import Update
from telegram.ext import CallbackContext
import logging
import re

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_domain(domain: str) -> bool:
    # Validate domain name format
    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,6}$"
    )
    return domain_pattern.match(domain) is not None

def search_whois(update: Update, context: CallbackContext) -> None:
    logger.info("Entered search_whois function")
    domain = ' '.join(context.args)
    logger.info(f"Domain to search: {domain}")
    if not domain:
        update.message.reply_text('Veuillez fournir un domaine pour la recherche Whois.')
        logger.warning("No domain provided for Whois search")
        return

    if not is_valid_domain(domain):
        update.message.reply_text('Nom de domaine invalide. Veuillez fournir un nom de domaine valide.')
        logger.warning(f"Invalid domain format: {domain}")
        return

    try:
        domain_info = whois.whois(domain)
        formatted_info = format_whois_info(domain_info)
        logger.info(f"Whois info for {domain}: {formatted_info}")
        update.message.reply_text(f"Whois Data pour '{domain}':\n{formatted_info}")
    except Exception as e:
        logger.error(f"Erreur lors de la recherche Whois: {e}")
        update.message.reply_text(f"Erreur Whois: {str(e)}")

def format_whois_info(domain_info) -> str:
    info = []
    for key, value in domain_info.items():
        if isinstance(value, list):
            value = ', '.join(value)
        info.append(f"{key}: {value}")
    return '\n'.join(info)
    