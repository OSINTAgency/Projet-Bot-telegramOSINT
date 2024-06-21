import whois
from telegram import Update
from telegram.ext import CallbackContext

def search_whois(update: Update, context: CallbackContext) -> None:
    domain = ' '.join(context.args)
    if not domain:
        update.message.reply_text('Veuillez fournir un domaine pour la recherche Whois.')
        return

    try:
        domain_info = whois.whois(domain)
        update.message.reply_text(f"Whois Data pour '{domain}':\n{domain_info}")
    except AttributeError as attr_err:
        update.message.reply_text(f"Erreur d'attribut Whois: {str(attr_err)}")
    except Exception as e:
        update.message.reply_text(f"Erreur Whois: {str(e)}")