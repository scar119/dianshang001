import requests

def call_moonshot_sync(content: str):
    api_key = os.getenv("MOONSHOT_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            "1+1等于几"
        ],
        "temperature": 0.3,
    }
    response = requests.post("https://api.moonshot.cn/v1/chat/completions", json=payload, headers=headers)
    return response.json()
