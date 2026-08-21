"""
Controlled End-to-End Chat Test (Strictly 3 Requests Maximum)
Medical RAG: Oxygen (أوكسجين)
Source Document: WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Verifies real HTTP flow through FastAPI TestClient:
Request 1: Arabic Supported Medical Inquiry
Request 2: English Supported Medical Inquiry
Request 3: Negative Control / Misinformation (Deterministic Circuit Breaker)
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

TEST_REQUESTS = [
    {
        "num": 1,
        "name": "Arabic Supported Medical Inquiry",
        "query": "ما هي العلاجات الدوائية الموصى بها في الخط الأول للإقلاع عن التدخين؟",
    },
    {
        "num": 2,
        "name": "English Supported Medical Inquiry",
        "query": "What is the evidence regarding combination nicotine replacement therapy vs monotherapy?",
    },
    {
        "num": 3,
        "name": "Negative Control / Misinformation Inquiry",
        "query": "هل السجائر الإلكترونية والفيب وسيلة علاجية معتمدة رسمياً في دليل منظمة الصحة 2024؟",
    },
]

print("================================================================================")
print("CONTROLLED LIVE E2E GENERATION TEST (STRICT 3-REQUEST LIMIT)")
print("================================================================================")

results = []

for req in TEST_REQUESTS:
    print(f"\n--- REQUEST {req['num']}/3: {req['name']} ---")
    print(f"Query: {req['query']}")
    
    t0 = time.perf_counter()
    resp = client.post("/api/v1/chat", json={"query": req["query"]})
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    
    print(f"HTTP Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Latency: {latency_ms} ms (Pipeline latency: {data.get('latency_ms')} ms)")
        print(f"Contract State: {data.get('contract_state')}")
        print(f"Safety Status: {data.get('safety_status')}")
        print(f"Grounded: {data.get('grounded')}")
        print(f"Provider: {data.get('provider')} | Model: {data.get('model')}")
        print(f"Citations Count: {len(data.get('citations', []))}")
        for c in data.get("citations", []):
            print(f"  - [{c.get('title')}] (Chunk: {c.get('chunk_id')})")
        print(f"Answer:\n{data.get('answer')}")
        results.append({
            "request_num": req["num"],
            "name": req["name"],
            "query": req["query"],
            "http_status": resp.status_code,
            "latency_ms": latency_ms,
            "contract_state": data.get("contract_state"),
            "safety_status": data.get("safety_status"),
            "grounded": data.get("grounded"),
            "provider": data.get("provider"),
            "model": data.get("model"),
            "citations_count": len(data.get("citations", [])),
            "citations": data.get("citations", []),
            "answer_preview": data.get("answer", "")[:150],
        })
    else:
        print(f"Error {resp.status_code}: {resp.text}")
        results.append({
            "request_num": req["num"],
            "name": req["name"],
            "query": req["query"],
            "http_status": resp.status_code,
            "error": resp.text,
        })

print("\n================================================================================")
print("SUMMARY OF 3 E2E REQUESTS:")
print(json.dumps(results, indent=2, ensure_ascii=False))
