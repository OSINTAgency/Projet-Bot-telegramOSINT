import logging
import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
from flask import Flask, request
import os
import telegram
import whois
import requests
import json
from coinbase_commerce.client import Client
from urllib.parse import quote
from queue import Queue

# Initialiser Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/{}'.format(config.TELEGRAM_BOT_TOKEN), methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Obtenir les configurations depuis config.py
bot_token = config.TELEGRAM_BOT_TOKEN
if not bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in config.py")

app_url = config.APP_URL
if not app_url:
    raise ValueError("APP_URL is not set in config.py")

# Définir l'URL du webhook
set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={app_url}/{bot_token}"
response = requests.get(set_webhook_url)
if response.status_code == 200:
    print("Webhook set successfully")
else:
    print(f"Failed to set webhook: {response.text}")

# Initialisation du bot
bot = telegram.Bot(token=bot_token)
dispatcher = Dispatcher(bot, None, workers=0)

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
        "/bile_suite <query> - Utilise l'outil bile-suite\n"
        "/tld_expand <query> - Utilise l'outil tld-expand pour obtenir des informations sur les TLD\n"
        "/pay_with_coinbase <amount> - Payer avec Coinbase Commerce\n"
    )
    update.message.reply_text(help_text)

# Commandes spécifiques
def search_twitter_command(update: Update, context: CallbackContext) -> None:
    search_twitter(update, context)

def search_whois_command(update: Update, context: CallbackContext) -> None:
    search_whois(update, context)

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

def bile_suite_command(update: Update, context: CallbackContext) -> None:
    bile_suite_query(update, context)

def tld_expand_command(update: Update, context: CallbackContext) -> None:
    tld_expand_query(update, context)

# Fonction de paiement avec Coinbase Commerce
def pay_with_coinbase(update: Update, context: CallbackContext) -> None:
    amount = ' '.join(context.args)
    if not amount:
        update.message.reply_text('Veuillez fournir un montant pour le paiement.')
        return
    
    coinbase_client = Client(api_key=config.COINBASE_API_KEY)
    
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
            redirect_url=f"{app_url}/success",
            cancel_url=f"{app_url}/cancel",
        )
        
        update.message.reply_text(f"Veuillez procéder au paiement en cliquant sur le lien suivant : {charge['hosted_url']}")
    except Exception as e:
        update.message.reply_text(f"Erreur lors de la création de la charge de paiement : {str(e)}")

# Initialisation du dispatcher
dispatcher.add_handler(CommandHandler("start", start_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("search_twitter", search_twitter_command))
dispatcher.add_handler(CommandHandler("search_whois", search_whois_command))
dispatcher.add_handler(CommandHandler("search_ip", search_ip_command))
dispatcher.add_handler(CommandHandler("search_breaches", search_breaches_command))
dispatcher.add_handler(CommandHandler("host", host_command))
dispatcher.add_handler(CommandHandler("nslookup", nslookup_command))
dispatcher.add_handler(CommandHandler("dnseum", dnseum_command))
dispatcher.add_handler(CommandHandler("bile_suite", bile_suite_command))
dispatcher.add_handler(CommandHandler("tld_expand", tld_expand_command))
dispatcher.add_handler(CommandHandler("pay_with_coinbase", pay_with_coinbase))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))