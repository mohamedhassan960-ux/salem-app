import requests

resp = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "qwen3-4b-cybersecurity-heretic",
        "messages": [{"role": "user", "content": "hello"}]
    },
    timeout=5
)
print("Response 400 details:", resp.text)
