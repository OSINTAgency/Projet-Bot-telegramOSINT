import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CallbackContext

def search_financial(update: Update, context: CallbackContext) -> None:
    company = ' '.join(context.args)
    if not company:
        update.message.reply_text('Veuillez fournir un nom d\'entreprise pour la recherche financière.')
        return

    try:
        search_url = f"https://www.societe.com/cgi-bin/search?champs={company}"
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result')
            formatted_results = "\n".join([result.get_text(strip=True) for result in results])
            update.message.reply_text(f"Résultats financiers pour '{company}':\n{formatted_results}")
        else:
            update.message.reply_text("Erreur lors de l'accès à societe.com.")
    except Exception as e:
        update.message.reply_text(f"Erreur financière: {str(e)}")
