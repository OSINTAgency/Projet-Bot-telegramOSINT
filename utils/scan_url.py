import requests
import json
from config import Config

def scan_url(url: str) -> str:
    headers = {
        'Authorization': f'Bearer {Config.URLDNA_API_KEY}',
    }
    params = {
        'url': url,
    }
    response = requests.get('https://api.urldna.io/analyze', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return format_analysis_result(data)
    else:
        return f"Erreur lors de l'analyse de l'URL {url}. Statut: {response.status_code}"

def format_analysis_result(data: dict) -> str:
    # Format the result in a user-friendly way
    result = "Résultat de l'analyse:\n"
    for key, value in data.items():
        result += f"{key}: {json.dumps(value, indent=2)}\n"
    return result