import requests

token = "7686619121:AAEUTTGCO6gd5BLUXqzLJOqwgoCRztuIhGI"


def notify_user(message, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response