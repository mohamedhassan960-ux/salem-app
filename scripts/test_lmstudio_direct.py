import os
import requests
import json

base_url = "http://localhost:1234/v1"
url = f"{base_url}/chat/completions"
headers = {"Content-Type": "application/json"}
payload = {
    "model": "google/gemma-4-e4b",
    "messages": [
        {"role": "system", "content": "You are a helpful medical assistant. Speak in warm Egyptian Arabic."},
        {"role": "user", "content": "ما هو دواء الفارينيكلين باختصار؟"}
    ],
    "temperature": 0.0,
    "max_tokens": 300
}

r = requests.post(url, headers=headers, json=payload, timeout=60)
print("Status:", r.status_code)
print("Raw response:", r.text)
