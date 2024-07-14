import requests
import os

# Remplacez par votre URL Heroku
heroku_app_url = "https://cyberdetectivebot-44a828f078dc.herokuapp.com/"
5
# Remplacez par votre token de bot Telegram
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Ou remplacez par votre token directement 
if not telegram_bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

# L'URL de votre webhook
webhook_url = f"{heroku_app_url}{telegram_bot_token}"

# URL de l'API Telegram pour définir le webhook
set_webhook_url = f"https://api.telegram.org/bot{telegram_bot_token}/setWebhook?url={webhook_url}"

# Envoyer la requête pour définir le webhook
response = requests.get(set_webhook_url)

# Vérifiez la réponse
if response.status_code == 200:
    print("Webhook configuré avec succès")
else:
    print(f"Erreur lors de la configuration du webhook: {response.status_code}")
    print(response.json())
