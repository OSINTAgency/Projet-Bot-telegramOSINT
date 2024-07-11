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

def search_whois(domain: str) -> dict:
    logger.info(f"Performing WHOIS search for domain: {domain}")
    try:
        domain_info = whois.whois(domain)
        logger.info(f"WHOIS search successful for domain: {domain}")
        return domain_info
    except whois.parser.PywhoisError as e:
        logger.error(f"WHOIS domain not found error: {e}")
        raise e
    except Exception as e:
        logger.error(f"General error in WHOIS search: {e}")
        raise e
