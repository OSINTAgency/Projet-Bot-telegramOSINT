import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from flask import Flask, request
import os
import requests
import json
import whois
from urllib.parse import quote
from config import Config

# Importations des modules utils
from utils.breaches import search_breaches
from utils.whois import search_whois, is_valid_domain
from utils.scan_url import scan_url  # Importation de la fonction scan_url


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
    bot.set_my_commands([
        BotCommand("start", "Démarrer le bot"),
        BotCommand("help", "Afficher les commandes disponibles"),
        BotCommand("search_breaches", "Rechercher des violations de données"),
        BotCommand("search_ip", "Rechercher des informations sur une adresse IP"),
        BotCommand("search_whois", "Rechercher des informations WHOIS"),
        BotCommand("search_twitter", "Recherche sur Twitter"),
        BotCommand("pay_with_coinbase", "Payer avec Coinbase Commerce"),
        BotCommand("scan_url", "Analyser une URL")  # Ajout de la commande scan_url
    ])

    keyboard = [
        [InlineKeyboardButton("Rechercher des violations de données", callback_data='/search_breaches')],
        [InlineKeyboardButton("Rechercher des informations WHOIS", callback_data='/search_whois')],
        [InlineKeyboardButton("Recherche sur Twitter", callback_data='/search_twitter')],
        [InlineKeyboardButton("Analyser une URL", callback_data='/scan_url')],  # Ajout du bouton scan_url
        [InlineKeyboardButton("Payer avec Coinbase Commerce", callback_data='/pay_with_coinbase')],
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
        "/search_breaches <email> - Recherche de fuites de données pour une adresse email\n"
        "/pay_with_coinbase <amount> - Payer avec Coinbase Commerce\n"
        "/scan_url <URL> - Recherche les informations sur l'url\n"
    )
    update.message.reply_text(help_text)

# Commandes spécifiques
def search_twitter_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur Twitter.\nUsage: /search_twitter <query>')
        return

    try:
        tweets = search_twitter(query)
        if tweets:
            message = f"Résultats de la recherche Twitter pour '{query}':\n"
            for tweet in tweets:
                message += f"- @{tweet['user']}: {tweet['text']}\n"
            update.message.reply_text(message)
        else:
            update.message.reply_text(f"Aucun résultat trouvé pour '{query}'.")
    except Exception as e:
        update.message.reply_text(f"Erreur lors de la recherche sur Twitter: {str(e)}")

# Fonction pour analyser les URLs avec urlDNA
def scan_url_command(update: Update, context: CallbackContext) -> None:
    url = ' '.join(context.args)
    if not url:
        update.message.reply_text('Veuillez fournir une URL pour l\'analyser.\nUsage: /scan_url <url>')
        return

    try:
        result = scan_url(url)  # Utilisation de la fonction scan_url importée
        update.message.reply_text(result)
    except Exception as e:
        update.message.reply_text(f"Erreur lors de l'analyse de l'URL: {str(e)}")

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
        domain_info = search_whois(domain)
        formatted_info = json.dumps(domain_info, indent=2)
        logger.info(f"Whois info for {domain}: {formatted_info}")
        update.message.reply_text(f"Whois Data pour '{domain}':\n{formatted_info}")
    except whois.parser.PywhoisError as e:  # Gérer les erreurs spécifiques de Whois
        logger.error(f"Domain not found: {e}")
        update.message.reply_text(f"Nom de domaine introuvable: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur lors de la recherche Whois: {e}")
        update.message.reply_text(f"Erreur Whois: {str(e)}")

def search_breaches_command(update: Update, context: CallbackContext) -> None:
    search_breaches(update, context)

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
dispatcher.add_handler(CommandHandler("search_breaches", search_breaches_command))
dispatcher.add_handler(CommandHandler("pay_with_coinbase", pay_with_coinbase))
dispatcher.add_handler(CommandHandler("scan_url", scan_url_command))  # Ajout du gestionnaire de commande pour scan_url

# Ajout d'un gestionnaire pour les erreurs
def error(update: Update, context: CallbackContext) -> None:
    """Log the error et notify the user."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')
    update.message.reply_text('Une erreur est survenue. Veuillez réessayer plus tard.')

dispatcher.add_error_handler(error)

# Lancer l'application Flask
if __name__ == '__main__':
    # Configuration du logging pour voir les informations sur les erreurs
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
                        level=logging.INFO)

    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))