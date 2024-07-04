# utils/dnseum.py
from telegram import Update
from telegram.ext import CallbackContext
import dns.resolver

def dnseum_query(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour dnseum.')
        return

    try:
        # Use dnspython to perform a DNS lookup
        answers = dns.resolver.query(query, 'A')
        ip_address = answers[0].to_text()
        update.message.reply_text(f"Résultats de dnseum pour '{query}':\n"
                                   f"IP: {ip_address}")
    except dns.resolver.NXDOMAIN:
        update.message.reply_text(f"Résultats de dnseum pour '{query}': Domain not found.")
    except Exception as e:
        update.message.reply_text(f"Une erreur s'est produite: {e}")