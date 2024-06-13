import requests
import config
import json

def get_access_token():
    url = "https://api.sendpulse.com/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": config.SENDPULSE_API_ID,
        "client_secret": config.SENDPULSE_API_SECRET
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response_data = response.json()
    return response_data['access_token']

def send_message(chat_id, text):
    token = get_access_token()
    url = f"https://api.sendpulse.com/chatbot/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()
