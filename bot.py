import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
from flask import Flask, request
import os
import requests
import json
from coinbase_commerce.client import Client
from urllib.parse import quote
from config import Config

# Importations des modules utils
from utils.breaches import search_breaches
from utils.whois import search_whois
from utils.nslookup import nslookup_query


# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser Flask
app = Flask(__name__)

# Initialiser le bot Telegram
bot = Bot(Config.TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/{}'.format(Config.TELEGRAM_BOT_TOKEN), methods=['POST'])
    def webhook():
        logger.info("Webhook POST request received")
        data = request.get_json(force=True)
        logger.info(f"Request data: {data}")
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        return 'ok'

# Définir l'URL du webhook
set_webhook_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/setWebhook?url={Config.APP_URL}/{Config.TELEGRAM_BOT_TOKEN}"
response = requests.get(set_webhook_url)
if response.status_code == 200:
    print("Webhook set successfully")
else:
    print(f"Failed to set webhook: {response.text}")

# Fonction de démarrage
def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bonjour! Utilisez /help pour voir les commandes disponibles.')

# Fonction d'aide
def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "/start - Démarre le bot\n"
        "/help - Affiche cette aide\n"
        "/search_twitter <query> - Recherche sur Twitter\n"
        "/search_whois <domain> - Recherche Whois pour un domaine\n"
        "/search_ip <ip_address> - Recherche d'informations sur une adresse IP\n"
        "/search_breaches <email> - Recherche de fuites de données pour une adresse email\n"
        "/host <domain> - Utilise l'outil host pour obtenir des informations DNS\n"
        "/nslookup <query> - Utilise l'outil nslookup pour obtenir des informations DNS\n"
        "/dnseum <query> - Utilise l'outil dnseum\n"
        "/tld_expand <query> - Utilise l'outil tld-expand pour obtenir des informations sur les TLD\n"
        "/pay_with_coinbase <amount> - Payer avec Coinbase Commerce\n"
    )
    update.message.reply_text(help_text)

# Commandes spécifiques
def search_twitter_command(update: Update, context: CallbackContext) -> None:
    search_twitter(update, context)

def search_whois_command(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received /search_whois command from {update.message.chat_id}")
    try:
        search_whois(update, context)
    except Exception as e:
        logging.error(f"Error in search_whois_command: {str(e)}")
        update.message.reply_text('Une erreur est survenue lors de l\'exécution de la commande /search_whois.')


def search_ip_command(update: Update, context: CallbackContext) -> None:
    search_ip(update, context)

def search_breaches_command(update: Update, context: CallbackContext) -> None:
    search_breaches(update, context)

def host_command(update: Update, context: CallbackContext) -> None:
    host_lookup(update, context)

def nslookup_command(update: Update, context: CallbackContext) -> None:
    nslookup_query(update, context)

def dnseum_command(update: Update, context: CallbackContext) -> None:
    dnseum_query(update, context)

def tld_expand_command(update: Update, context: CallbackContext) -> None:
    tld_expand_query(update, context)

# Fonction de paiement avec Coinbase Commerce
def pay_with_coinbase(update: Update, context: CallbackContext) -> None:
    amount = ' '.join(context.args)
    if not amount:
        update.message.reply_text('Veuillez fournir un montant pour le paiement.')
        return

    coinbase_client = Client(api_key=Config.COINBASE_COMMERCE_API_KEY)

    try:
        # Créer une charge pour le paiement
        charge = coinbase_client.charge.create(
            name='OSINT Bot Payment',
            description='Paiement pour les services OSINT Bot',
            local_price={
                'amount': amount,
                'currency': 'USD'
            },
            pricing_type='fixed_price',
            redirect_url=f"{Config.APP_URL}/success",
            cancel_url=f"{Config.APP_URL}/cancel",
        )

        update.message.reply_text(f"Veuillez procéder au paiement en cliquant sur le lien suivant : {charge['hosted_url']}")
    except Exception as e:
        update.message.reply_text(f"Erreur lors de la création de la charge de paiement : {str(e)}")

# Ajout des gestionnaires de commandes au dispatcher
dispatcher.add_handler(CommandHandler("start", start_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("search_twitter", search_twitter_command))
dispatcher.add_handler(CommandHandler("search_whois", search_whois_command))
dispatcher.add_handler(CommandHandler("search_ip", search_ip_command))
dispatcher.add_handler(CommandHandler("search_breaches", search_breaches_command))
dispatcher.add_handler(CommandHandler("host", host_command))
dispatcher.add_handler(CommandHandler("nslookup", nslookup_command))
dispatcher.add_handler(CommandHandler("dnseum", dnseum_command))
dispatcher.add_handler(CommandHandler("tld_expand", tld_expand_command))
dispatcher.add_handler(CommandHandler("pay_with_coinbase", pay_with_coinbase))

# Ajout d'un gestionnaire pour les erreurs
def error(update: Update, context: CallbackContext) -> None:
    """Log the error et notify the user."""
    logging.warning(f'Update "{update}" caused error "{context.error}"')
    update.message.reply_text('Une erreur est survenue. Veuillez réessayer plus tard.')

dispatcher.add_error_handler(error)

# Lancer l'application Flask
if __name__ == '__main__':
    # Configuration du logging pour voir les informations sur les erreurs
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
