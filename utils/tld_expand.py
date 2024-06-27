import json
import requests
from telegram import Update
from telegram.ext import CallbackContext, Updater, CommandHandler

# Fonction pour gérer la commande tld_expand
def tld_expand_query(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour tld-expand.')
        return

    try:
        # Exemple d'API pour obtenir des informations sur les TLD
        tld_expand_api_url = f"https://api.tldexpand.com/v1/info/{query}"
        response = requests.get(tld_expand_api_url)
        if response.status_code == 200:
            tld_data = response.json()
            formatted_data = json.dumps(tld_data, indent=2)
            update.message.reply_text(f"Informations sur le TLD '{query}':\n{formatted_data}")
        else:
            update.message.reply_text(f"Erreur lors de l'accès à l'API tld-expand: {response.status_code}")
    except Exception as e:
        update.message.reply_text(f"Erreur tld-expand: {str(e)}")

# Fonction de démarrage du bot
def main() -> None:
    # Initialiser l'updater et le dispatcher
    updater = Updater("7341170491:AAGVNu7Iq0xWbQbqvjxXBOQHVi4mOo2h7Pc")
    dispatcher = updater.dispatcher

    # Ajout des handlers pour les commandes
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("search_twitter", search_twitter))
    dispatcher.add_handler(CommandHandler("search_whois", search_whois))
    dispatcher.add_handler(CommandHandler("search_ip", search_ip))
    dispatcher.add_handler(CommandHandler("search_breaches", search_breaches))
    dispatcher.add_handler(CommandHandler("search_engine", search_engine))
    dispatcher.add_handler(CommandHandler("search_financial", search_financial))
    dispatcher.add_handler(CommandHandler("host", host_lookup))
    dispatcher.add_handler(CommandHandler("nslookup", nslookup_query))
    dispatcher.add_handler(CommandHandler("dnseum", dnseum_query))
    dispatcher.add_handler(CommandHandler("tld_expand", tld_expand_query))

    # Démarrer le bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
