import subprocess
from telegram import Update
from telegram.ext import CallbackContext

def nslookup_query(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Veuillez fournir une requête pour nslookup.')
        return

    try:
        result = subprocess.run(['nslookup', query], capture_output=True, text=True)
        update.message.reply_text(f"Résultats de nslookup pour '{query}':\n{result.stdout}")
    except Exception as e:
        update.message.reply_text(f"Erreur nslookup: {str(e)}")
