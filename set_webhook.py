import requests
import os

# Remplacez par votre URL Vercel
vercel_app_url = "https://cyberdetectivebot.vercel.app/"

# Remplacez par votre token de bot Telegram
telegram_bot_token = os.getenv('7341170491:AAGVNu7Iq0xWbQbqvjxXBOQHVi4mOo2h7Pc')  # Ou remplacez par votre token directement

# L'URL de votre webhook
webhook_url = f"{vercel_app_url}/{telegram_bot_token}"

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
