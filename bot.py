from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import config
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

def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "Bonjour! Je suis votre bot OSINT. Voici quelques commandes pour commencer :\n"
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
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "Voici une liste des commandes disponibles :\n"
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
    )
    update.message.reply_text(help_message)

def main() -> None:
    updater = Updater(config.TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("search_twitter", search_twitter))
    dispatcher.add_handler(CommandHandler("search_whois", search_whois))
    dispatcher.add_handler(CommandHandler("search_ip", search_ip))
    dispatcher.add_handler(CommandHandler("search_breaches", search_breaches))
    dispatcher.add_handler(CommandHandler("search_engine", search_engine))
    dispatcher.add_handler(CommandHandler("search_financial", search_financial))
    dispatcher.add_handler(CommandHandler("search_news", search_news))
    dispatcher.add_handler(CommandHandler("host", host_lookup))
    dispatcher.add_handler(CommandHandler("nslookup", nslookup_query))
    dispatcher.add_handler(CommandHandler("dnseum", dnseum_query))
    dispatcher.add_handler(CommandHandler("bile_suite", bile_suite_query))
    dispatcher.add_handler(CommandHandler("tld_expand", tld_
