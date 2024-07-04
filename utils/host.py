import subprocess
from telegram import Update
from telegram.ext import CallbackContext

def host_lookup(update: Update, context: CallbackContext) -> None:
    domain = ' '.join(context.args)
    if not domain:
        update.message.reply_text('Veuillez fournir un domaine pour la recherche avec host.')
        return

    try:
        result = subprocess.run(['host', domain], capture_output=True, text=True)
        update.message.reply_text(f"Résultats de host pour '{domain}':\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        update.message.reply_text(f"Erreur host: {e.stderr}") # Use stderr for more specific error message
    except Exception as e:
        update.message.reply_text(f"Erreur host: {str(e)}") # Keep general Exception block for unknown errors