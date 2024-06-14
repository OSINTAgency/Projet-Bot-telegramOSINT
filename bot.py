from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
from flask import Flask, request
import os
import telegram
import whois
import requests
import json

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

app = Flask(__name__)

# Obtenir le token de bot à partir des variables d'environnement
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

bot = telegram.Bot(token=bot_token)
dispatcher = Dispatcher(bot, None, workers=0)

# Fonction start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bonjour! Je suis votre bot.')

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

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search_whois", search_whois_command))

# Route pour le webhook
@app.route(f'/{bot_token}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Fonction pour obtenir le token d'authentification de SendPulse
def get_sendpulse_token():
    url = "https://api.sendpulse.com/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv('SENDPULSE_ID'),
        "client_secret": os.getenv('SENDPULSE_SECRET')
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json().get("access_token")

# Fonction pour envoyer des emails via SendPulse
def send_email_via_sendpulse(subject, body, recipient_email):
    token = get_sendpulse_token()
    if not token:
        return {"result": False, "error": "Unable to get token"}

    url = "https://api.sendpulse.com/smtp/emails"
    payload = {
        "email": {
            "html": body,
            "text": body,
            "subject": subject,
            "from": {
                "name": os.getenv('SENDPULSE_FROM_NAME'),
                "email": os.getenv('SENDPULSE_FROM_EMAIL')
            },
            "to": [
                {
                    "name": "Recipient Name",
                    "email": recipient_email
                }
            ]
        }
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

# Commande Telegram pour envoyer des emails
def send_email(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 3:
        update.message.reply_text('Usage: /send_email <email> <subject> <body>')
        return

    recipient_email = context.args[0]
    subject = context.args[1]
    body = ' '.join(context.args[2:])
    
    response = send_email_via_sendpulse(subject, body, recipient_email)
    
    if response.get("result"):
        update.message.reply_text(f"Email envoyé à {recipient_email}")
    else:
        update.message.reply_text(f"Erreur lors de l'envoi de l'email: {response}")

# Commande par défaut pour afficher la liste des commandes lorsque l'utilisateur tape /
def default_command(update: Update, context: CallbackContext) -> None:
    help_command(update, context)

# Fonction pour démarrer le bot et afficher le clavier interactif avec les options de commande
def start(update: Update, context: CallbackContext) -> None:
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

# Fonction pour effectuer une recherche générique OSINT
def search(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour la recherche.")
        return

    results = search_engine(query)
    update.message.reply_text(f"Résultats de la recherche pour '{query}':\n{results}")

# Fonctions de recherche spécifiques
def search_twitter_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour la recherche sur Twitter.")
        return
    search_twitter(update, context, query)

def search_whois_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir un domaine pour la recherche Whois.")
        return
    search_whois(update, context, query)

def search_ip_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une adresse IP pour la recherche.")
        return
    search_ip(update, context, query)

def search_breaches_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une adresse email pour la recherche de fuites de données.")
        return
    search_breaches(update, context, query)

def search_news_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour la recherche d'actualités.")
        return
    search_news(update, context, query)

def search_financial_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une entreprise pour la recherche financière.")
        return
    search_financial(update, context, query)

def host_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir un domaine pour l'outil host.")
        return
    host_lookup(update, context, query)

def nslookup_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour l'outil nslookup.")
        return
    nslookup_query(update, context, query)

def dnseum_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour l'outil dnseum.")
        return
    dnseum_query(update, context, query)

def bile_suite_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour l'outil bile-suite.")
        return
    bile_suite_query(update, context, query)

def tld_expand_command(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text("Veuillez fournir une requête pour l'outil tld-expand.")
        return
    tld_expand_query(update, context, query)

def generate_report(update: Update, context: CallbackContext) -> None:
    # Implémentation de la génération de rapport
    update.message.reply_text("Fonction de génération de rapport non encore implémentée.")

def show_history(update: Update, context: CallbackContext) -> None:
    # Implémentation de l'affichage de l'historique
    update.message.reply_text("Fonction d'affichage de l'historique non encore implémentée.")

def subscribe_alerts(update: Update, context: CallbackContext) -> None:
    # Implémentation de l'abonnement aux alertes
    update.message.reply_text("Fonction d'abonnement aux alertes non encore implémentée.")

def unsubscribe_alerts(update: Update, context: CallbackContext) -> None:
    # Implémentation du désabonnement aux alertes
    update.message.reply_text("Fonction de désabonnement aux alertes non encore implémentée.")

def pay_with_crypto(update: Update, context: CallbackContext) -> None:
    # Implémentation du paiement en crypto
    update.message.reply_text("Fonction de paiement en crypto non encore implémentée.")

# Fonction principale pour démarrer le bot
def main() -> None:
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
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

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
