import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from flask import Flask, request
import os
import requests
import json
from coinbase_commerce.client import Client  # This import is potentially unused
from urllib.parse import quote
from config import Config

# Importations des modules utils
from utils.breaches import search_breaches
from utils.whois import search_whois, is_valid_domain # Import is_valid_domain
from utils.nslookup import nslookup_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Affiche les logs dans la console
        logging.FileHandler('bot.log')  # Enregistre les logs dans un fichier
    ]
)

logger = logging.getLogger(__name__)

# Initialiser Flask
app = Flask(__name__)

# Initialiser le bot Telegram avec Updater
updater = Updater(Config.TELEGRAM_BOT_TOKEN)
dispatcher = updater.dispatcher
bot = updater.bot

# Définir les commandes et obtenir le clavier interactif
def set_commands_and_keyboard(bot):
    # Définir les commandes pour l'autosaisie
    bot.set_my_commands([
        BotCommand("start", "Démarrer le bot"),
        BotCommand("help", "Afficher les commandes disponibles"),
        BotCommand("search_breaches", "Rechercher des violations de données"),
        BotCommand("search_ip", "Rechercher des informations sur une adresse IP"),
        BotCommand("search_whois", "Rechercher des informations WHOIS"),
        BotCommand("search_twitter", "Recherche sur Twitter"),
        BotCommand("host", "Utilise l'outil host"),
        BotCommand("nslookup", "Utilise l'outil nslookup"),
        BotCommand("dnseum", "Utilise l'outil dnseum"),
        BotCommand("tld_expand", "Utilise l'outil tld-expand"),
        BotCommand("pay_with_coinbase", "Payer avec Coinbase Commerce"),
    ])

    # Créer un clavier interactif pour les fonctions principales
    keyboard = [
        [InlineKeyboardButton("Rechercher des violations de données", callback_data='search_breaches')],
        [InlineKeyboardButton("Rechercher des informations sur une adresse IP", callback_data='search_ip')],
        [InlineKeyboardButton("Rechercher des informations WHOIS", callback_data='search_whois')],
        [InlineKeyboardButton("Recherche sur Twitter", callback_data='search_twitter')],
        [InlineKeyboardButton("Utiliser l'outil host", callback_data='host')],
        [InlineKeyboardButton("Utiliser l'outil nslookup", callback_data='nslookup')],
        [InlineKeyboardButton("Utiliser l'outil dnseum", callback_data='dnseum')],
        [InlineKeyboardButton("Utiliser l'outil tld-expand", callback_data='tld_expand')],
        [InlineKeyboardButton("Payer avec Coinbase Commerce", callback_data='pay_with_coinbase')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup

reply_markup = set_commands_and_keyboard(bot)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/{}'.format(Config.TELEGRAM_BOT_TOKEN), methods=['POST'])
def webhook():
    logger.info("Webhook POST request received")
    try:
        data = request.get_json(force=True)
        logger.info(f"Request data: {data}")
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
    return 'ok'

# Définir l'URL du webhook
set_webhook_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/setWebhook?url={Config.APP_URL}/{Config.TELEGRAM_BOT_TOKEN}"
response = requests.get(set_webhook_url)
if response.status_code == 200:
    print("Webhook set successfully")
else:
    print(f"Failed to set webhook: {response.text}")

# Fonction de démarrage améliorée avec clavier interactif
def start_command(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "👋 Bonjour et bienvenue sur CyberDetectiveBot! 🕵️‍♂️\n\n"
        "Ce bot vous permet de réaliser des recherches OSINT directement depuis Telegram.\n\n"
        "Utilisez les boutons ci-dessous pour commencer."
    )
    update.message.reply_text(welcome_message, reply_markup=reply_markup)


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
    search_twitter(update, context)  # search_twitter not defined

def search_whois_command(update: Update, context: CallbackContext) -> None:
    logger.info("Entered search_whois function")
    domain = ' '.join(context.args)
    logger.info(f"Domain to search: {domain}")

    if not domain:
        update.message.reply_text('Veuillez fournir un domaine pour la recherche Whois.\nUsage: /search_whois <domain>')
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
    except whois.parser.PywhoisError as e:  # Gérer les erreurs spécifiques de Whois
        logger.error(f"Domain not found: {e}")
        update.message.reply_text(f"Nom de domaine introuvable: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur lors de la recherche Whois: {e}")
        update.message.reply_text(f"Erreur Whois: {str(e)}")

def search_ip_command(update: Update, context: CallbackContext) -> None:
    search_ip(update, context)  # search_ip not defined

def search_breaches_command(update: Update, context: CallbackContext) -> None:
    search_breaches(update, context)

def host_command(update: Update, context: CallbackContext) -> None:
    host_lookup(update, context)  # host_lookup not defined

def nslookup_command(update: Update, context: CallbackContext) -> None:
    nslookup_query(update, context)

def dnseum_command(update: Update, context: CallbackContext) -> None:
    dnseum_query(update, context)  # dnseum_query not defined

def tld_expand_command(update: Update, context: CallbackContext) -> None:
    tld_expand_query(update, context)  # tld_expand_query not defined

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
    logger.warning(f'Update "{update}" caused error "{context.error}"')
    update.message.reply_text('Une erreur est survenue. Veuillez réessayer plus tard.')

dispatcher.add_error_handler(error)

# Lancer l'application Flask
if __name__ == '__main__':
    # Configuration du logging pour voir les informations sur les erreurs
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))