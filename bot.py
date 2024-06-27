import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
from flask import Flask, request
import os
import telegram
import whois
import requests
import json
from urllib.parse import quote
from queue import Queue

# Importer les fonctions utilitaires
from utils.twitter import search_twitter
from utils.whois import search_whois
from utils.ip import search_ip
from utils.breaches import search_breaches
from utils.search_engine import search_engine
from utils.financial import search_financial
from utils.news import search_news
from utils.host import host_lookup
from utils.nslookup import nslookup_query
from utils.dnseum import dnseum_query
from utils.bile_suite import bile_suite_query
from utils.tld_expand import tld_expand_query

# Initialiser Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Obtenir le token de bot à partir des variables d'environnement
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

app_url = os.getenv('APP_URL')  # Assurez-vous de définir cette variable dans vos environnements de déploiement
if not app_url:
    raise ValueError("APP_URL is not set in environment variables")

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

# Fonction de démarrage (renommée pour éviter les conflits)
def start_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Recherche Whois", callback_data='whois'),
            InlineKeyboardButton("Recherche Twitter", callback_data='twitter'),
        ],
        [
            InlineKeyboardButton("Recherche d'Actualités", callback_data='news'),
            InlineKeyboardButton("Recherche Financière", callback_data='financial')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        "Bonjour! Je suis votre bot OSINT. Voici quelques commandes pour commencer :\n"
        "Choisissez une option ci-dessous :"
    )
    update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Fonction de recherche WHOIS
def search_whois_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Usage: /search_whois <domain>')
        return

    domain = context.args[0]
    try:
        domain_info = whois.whois(domain)
        update.message.reply_text(f"Informations WHOIS pour {domain}:\n{domain_info}")
    except Exception as e:
        update.message.reply_text(f"Erreur lors de la recherche WHOIS: {str(e)}")

# Fonction pour gérer les boutons du clavier interactif
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    command = query.data

    if command == 'whois':
        query.edit_message_text(text="Utilisez la commande /search_whois <domain> pour effectuer une recherche Whois.")
    elif command == 'twitter':
        query.edit_message_text(text="Utilisez la commande /search_twitter <query> pour effectuer une recherche sur Twitter.")
    elif command == 'news':
        query.edit_message_text(text="Utilisez la commande /search_news <query> pour effectuer une recherche d'actualités.")
    elif command == 'financial':
        query.edit_message_text(text="Utilisez la commande /search_financial <company> pour effectuer une recherche financière.")
    elif command == 'search_ip':
        query.edit_message_text(text="Utilisez la commande /search_ip <ip_address> pour effectuer une recherche sur une adresse IP.")
    elif command == 'search_breaches':
        query.edit_message_text(text="Utilisez la commande /search_breaches <email> pour rechercher des fuites de données pour une adresse email.")
    elif command == 'search_engine':
        query.edit_message_text(text="Utilisez la commande /search_engine <query> pour rechercher sur les moteurs de recherche.")
    elif command == 'host':
        query.edit_message_text(text="Utilisez la commande /host <domain> pour obtenir des informations DNS avec l'outil host.")
    elif command == 'nslookup':
        query.edit_message_text(text="Utilisez la commande /nslookup <query> pour obtenir des informations DNS avec l'outil nslookup.")
    elif command == 'dnseum':
        query.edit_message_text(text="Utilisez la commande /dnseum <query> pour utiliser l'outil dnseum.")
    elif command == 'bile_suite':
        query.edit_message_text(text="Utilisez la commande /bile_suite <query> pour utiliser l'outil bile-suite.")
    elif command == 'tld_expand':
        query.edit_message_text(text="Utilisez la commande /tld_expand <query> pour obtenir des informations sur les TLD avec l'outil tld-expand.")
    elif command == 'report':
        query.edit_message_text(text="Utilisez la commande /report <query> pour générer un rapport détaillé.")
    elif command == 'history':
        query.edit_message_text(text="Utilisez la commande /history pour afficher l'historique de vos recherches.")
    elif command == 'subscribe':
        query.edit_message_text(text="Utilisez la commande /subscribe <query> pour vous abonner aux alertes pour une requête spécifique.")
    elif command == 'unsubscribe':
        query.edit_message_text(text="Utilisez la commande /unsubscribe <query> pour vous désabonner des alertes.")
    elif command == 'pay_with_crypto':
        query.edit_message_text(text="Utilisez la commande /pay_with_crypto <plan> pour procéder au paiement en crypto pour les fonctionnalités premium.")

# Fonction pour afficher l'aide
def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Voici les commandes disponibles:\n"
        "/start - Démarre le bot\n"
        "/help - Affiche cette aide\n"
        "/search <query> - Effectue une recherche OSINT\n"
        "/search_twitter <query> - Recherche sur Twitter\n"
        "/search_whois <domain> - Recherche Whois pour un domaine\n"
        "/search_ip <ip_address> - Recherche d'informations sur une adresse IP\n"
        "/search_breaches <email> - Recherche de fuites de données pour une adresse email\n"
        "/search_engine <query> - Recherche sur les moteurs de recherche\n"
        "/search_financial <company> - Recherche financière sur une entreprise\n"
        "/search_news <query> - Recherche d'actualités sur Google Actualités\n"
        "/host <domain> - Utilise l'outil host pour obtenir des informations DNS\n"
        "/nslookup <query> - Utilise l'outil nslookup pour obtenir des informations DNS\n"
        "/dnseum <query> - Utilise l'outil dnseum\n"
        "/bile_suite <query> - Utilise l'outil bile-suite\n"
        "/tld_expand <query> - Utilise l'outil tld-expand pour obtenir des informations sur les TLD\n"
        "/report <query> - Génère un rapport détaillé\n"
        "/history - Affiche l'historique de vos recherches\n"
        "/subscribe <query> - Abonnez-vous aux alertes pour une requête spécifique\n"
        "/unsubscribe <query> - Désabonnez-vous des alertes\n"
        "/pay_with_crypto <plan> - Procédez au paiement en crypto pour les fonctionnalités premium\n"
    )
    update.message.reply_text(help_text)

# Fonction pour démarrer le bot
def main() -> None:
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("search", search))
    dispatcher.add_handler(CommandHandler("search_whois", search_whois_command))
    dispatcher.add_handler(CommandHandler("search_twitter", search_twitter_command))
    dispatcher.add_handler(CommandHandler("search_news", search_news_command))
    dispatcher.add_handler(CommandHandler("search_financial", search_financial_command))
    dispatcher.add_handler(CommandHandler("search_ip", search_ip_command))
    dispatcher.add_handler(CommandHandler("search_breaches", search_breaches_command))
    dispatcher.add_handler(CommandHandler("search_engine", search))
    dispatcher.add_handler(CommandHandler("host", host_command))
    dispatcher.add_handler(CommandHandler("nslookup", nslookup_command))
    dispatcher.add_handler(CommandHandler("dnseum", dnseum_command))
    dispatcher.add_handler(CommandHandler("bile_suite", bile_suite_command))
    dispatcher.add_handler(CommandHandler("tld_expand", tld_expand_command))
    dispatcher.add_handler(CommandHandler("report", generate_report))
    dispatcher.add_handler(CommandHandler("history", show_history))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_alerts))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_alerts))
    dispatcher.add_handler(CommandHandler("pay_with_crypto", pay_with_crypto))

    # Démarrer le bot
    updater.start_polling()
    updater.idle()