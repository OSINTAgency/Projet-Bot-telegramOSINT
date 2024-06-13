# Importation des modules nécessaires de la bibliothèque Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Importation des configurations et des clés API
import config

# Importation des fonctions de recherche OSINT définies dans les modules utils
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

# Importation des bibliothèques supplémentaires nécessaires
import requests
import json
from sendpulse import send_message

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
    data = query.data
    chat_id = update.effective_chat.id

    if data == 'whois':
        send_message(chat_id, "Entrez le domaine pour la recherche Whois : /search_whois <domain>")
    elif data == 'twitter':
        send_message(chat_id, "Entrez la requête pour la recherche sur Twitter : /search_twitter <query>")
    elif data == 'news':
        send_message(chat_id, "Entrez la requête pour la recherche d'actualités : /search_news <query>")
    elif data == 'financial':
        send_message(chat_id, "Entrez le nom de l'entreprise pour la recherche financière : /search_financial <company>")

# Fonction pour afficher les commandes disponibles
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "Voici une liste des commandes disponibles :\n"
        "/start - Démarre le bot\n"
        "/help - Affiche cette aide\n"
        "/search_whois <domain> - Recherche Whois pour un domaine\n"
        "/search_twitter <query> - Recherche sur Twitter\n"
        "/search_news <query> - Recherche d'actualités\n"
        "/search_financial <company> - Recherche financière sur une entreprise\n"
    )
    update.message.reply_text(help_message)

# Fonction pour effectuer une recherche Whois
def search_whois(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir un domaine pour la recherche Whois.')
        return

    try:
        domain_info = whois.whois(query)
        response_message = (
            f"Informations WHOIS pour {query}:\n"
            f"Domain Name: {domain_info.domain_name}\n"
            f"Registrar: {domain_info.registrar}\n"
            f"Creation Date: {domain_info.creation_date}\n"
            f"Expiration Date: {domain_info.expiration_date}\n"
            f"Name Servers: {', '.join(domain_info.name_servers)}\n"
        )
        update.message.reply_text(response_message)
    except Exception as e:
        update.message.reply_text(f"Erreur lors de la recherche WHOIS : {str(e)}")

# Fonction pour effectuer une recherche sur Twitter
def search_twitter(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour la recherche sur Twitter.')
        return

    try:
        twitter_api_url = f"https://api.twitter.com/2/tweets/search/recent?query={query}"
        headers = {"Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}"}
        response = requests.get(twitter_api_url, headers=headers)
        if response.status_code == 200:
            twitter_data = response.json()
            formatted_data = json.dumps(twitter_data, indent=2)
            update.message.reply_text(f"Résultats Twitter pour '{query}':\n{formatted_data}")
        else:
            update.message.reply_text("Erreur lors de l'accès à l'API Twitter.")
    except Exception as e:
        update.message.reply_text(f"Erreur Twitter: {str(e)}")

# Fonction principale pour démarrer le bot
def main() -> None:
    updater = Updater(config.TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("search_whois", search_whois))
    dispatcher.add_handler(CommandHandler("search_twitter", search_twitter))
    dispatcher.add_handler(CommandHandler("search_news", search_news))
    dispatcher.add_handler(CommandHandler("search_financial", search_financial))
    dispatcher.add_handler(CommandHandler("search_ip", search_ip))
    dispatcher.add_handler(CommandHandler("search_breaches", search_breaches))
    dispatcher.add_handler(CommandHandler("search_engine", search_engine))
    dispatcher.add_handler(CommandHandler("host", host_lookup))
    dispatcher.add_handler(CommandHandler("nslookup", nslookup_query))
    dispatcher.add_handler(CommandHandler("dnseum", dnseum_query))
    dispatcher.add_handler(CommandHandler("bile_suite", bile_suite_query))
    dispatcher.add_handler(CommandHandler("tld_expand", tld_expand_query))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
