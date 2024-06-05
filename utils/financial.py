import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CallbackContext

def search_financial(update: Update, context: CallbackContext) -> None:
    company_name = ' '.join(context.args)
    if not company_name:
        update.message.reply_text('Veuillez fournir un nom d\'entreprise pour la recherche financière.')
        return

    try:
        search_url = f"https://www.societe.com/cgi-bin/search?champs={company_name}"
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', {'class': 'link'})
            if results:
                message = f"Rés