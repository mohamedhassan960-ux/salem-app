"""
Detect provider by testing the API key against known endpoints.
Key is read from environment variable only — never printed.
"""
import os
import requests

key = os.environ.get("_TEMP_API_KEY", "")
if not key:
    print("ERROR: _TEMP_API_KEY not set")
    exit(1)

print(f"Key configured: YES | Length: {len(key)} chars")

endpoints = [
    {
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1/models",
        "headers": {"Authorization": f"Bearer {key}"},
    },
    {
        "name": "Mistral AI",
        "url": "https://api.mistral.ai/v1/models",
        "headers": {"Authorization": f"Bearer {key}"},
    },
    {
        "name": "Together AI",
        "url": "https://api.together.xyz/v1/models",
        "headers": {"Authorization": f"Bearer {key}"},
    },
    {
        "name": "Cohere",
        "url": "https://api.cohere.ai/v1/models",
        "headers": {"Authorization": f"Bearer {key}"},
    },
    {
        "name": "AI21 Labs",
        "url": "https://api.ai21.com/studio/v1/models",
        "headers": {"Authorization": f"Bearer {key}"},
    },
    {
        "name": "Cerebras AI",
        "url": "https://api.cerebras.ai/v1/models",
        "headers": {"Authorization": f"Bearer {key}"},
    },
]

print("\nTesting endpoints...")
for ep in endpoints:
    try:
        r = requests.get(ep["url"], headers=ep["headers"], timeout=6)
        print(f"  [{ep['name']}] Status: {r.status_code} -> {'VALID KEY!' if r.status_code == 200 else r.text[:80]}")
    except Exception as e:
        print(f"  [{ep['name']}] ERROR: {e}")
