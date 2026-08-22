import requests
import json
import time

import sys
import os

backend_url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BACKEND_URL", "https://tahoe-calculator-bowling-groundwater.trycloudflare.com")
backend_url = backend_url.rstrip("/")

test_queries = [
    {
        "num": 1,
        "title": "Arabic Supported Medical Query",
        "query": "ما هي العلاجات الدوائية الموصى بها في الخط الأول للإقلاع عن التدخين؟"
    },
    {
        "num": 2,
        "title": "English Supported Medical Query",
        "query": "What is the evidence regarding combination nicotine replacement therapy vs monotherapy?"
    },
    {
        "num": 3,
        "title": "Negative Control / Misinformation (Abstention)",
        "query": "هل السجائر الإلكترونية والفيب وسيلة علاجية معتمدة رسمياً في دليل منظمة الصحة 2024؟"
    }
]

print("================================================================================")
print("LIVE ONLINE E2E CHAT VERIFICATION (PUBLIC CLOUD HTTPS)")
print("================================================================================")

for t in test_queries:
    num = t["num"]
    title = t["title"]
    query = t["query"]
    print(f"\n--- TEST {num}/3: {title} ---")
    print("Query:", query)
    t0 = time.perf_counter()
    r = requests.post(f"{backend_url}/api/v1/chat", json={"query": query}, timeout=45)
    lat = round((time.perf_counter() - t0) * 1000, 2)
    print(f"HTTP Status: {r.status_code} ({lat}ms)")
    if r.status_code == 200:
        data = r.json()
        print("Contract State:", data.get("contract_state"))
        print("Safety Status:", data.get("safety_status"))
        print("Grounded:", data.get("grounded"))
        print(f"Provider: {data.get('provider')} | Model: {data.get('model')}")
        print("Citations Count:", len(data.get("citations", [])))
        for c in data.get("citations", []):
            print(f"  - [{c.get('title')}] (Page {c.get('physical_page_start')})")
        print("\nAnswer:\n" + str(data.get("answer", "")))
    else:
        print("Error:", r.text)

print("\n================================================================================")
print("COMPLETED 3-REQUEST LIVE ONLINE VERIFICATION")
print("================================================================================")
