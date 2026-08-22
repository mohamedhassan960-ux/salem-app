import requests
import json
import time

BACKEND_URL = "https://salem-backend.vercel.app"
FRONTEND_URL = "https://frontend-gray-gamma-76.vercel.app"

import sys
sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("STARTING PRODUCTION SYSTEM INTEGRITY TEST")
print("="*60)

# 1. Test Backend Health Endpoints
print("\n[1/4] Checking Cloud Backend Health Endpoints...")
for ep in ["/health", "/ready", "/api/v1/health/rag", "/api/v1/diagnostic"]:
    url = f"{BACKEND_URL}{ep}"
    try:
        r = requests.get(url, timeout=10)
        print(f"  ✓ GET {ep} -> HTTP {r.status_code}")
    except Exception as e:
        print(f"  ✗ GET {ep} FAILED: {e}")

# 2. Test Frontend Live Availability
print("\n[2/4] Checking Frontend Production URL...")
try:
    rf = requests.get(FRONTEND_URL, timeout=10)
    print(f"  ✓ GET {FRONTEND_URL} -> HTTP {rf.status_code} (HTML length: {len(rf.text)})")
except Exception as e:
    print(f"  ✗ Frontend check failed: {e}")

# 3. Test Live End-to-End Chat & Evidence Grounding
print("\n[3/4] Testing Live Clinical Query & Evidence Grounding...")
query = "أنا بدخن علبة سجاير في اليوم وبصحى الصبح أول حاجة بولع سيجارة، محتاج خطة علاجية مخصصة للإقلاع"
payload = {
    "query": query,
    "conversation_history": []
}

t0 = time.time()
try:
    rc = requests.post(f"{BACKEND_URL}/api/v1/chat", json=payload, timeout=45)
    elapsed = time.time() - t0
    print(f"  ✓ POST /api/v1/chat -> HTTP {rc.status_code} in {elapsed:.2f}s")
    
    if rc.status_code == 200:
        data = rc.json()
        ans = data.get("answer", "")
        cits = data.get("citations", [])
        state = data.get("contract_state")
        grounded = data.get("grounded")
        
        print(f"  ✓ Contract State: {state}")
        print(f"  ✓ Grounded: {grounded}")
        print(f"  ✓ Citations Count: {len(cits)}")
        print(f"  ✓ Answer Preview:\n    {ans[:250]}...")
        
        # Verify evidence viewer properties
        if cits:
            first_c = cits[0]
            print("\n[4/4] Verifying Evidence Viewer Data Structure on Live Response:")
            print(f"  ✓ Citation ID: {first_c.get('citation_id')}")
            print(f"  ✓ Document Title: {first_c.get('source', {}).get('title')}")
            print(f"  ✓ Organization: {first_c.get('source', {}).get('organization')}")
            print(f"  ✓ Official URL: {first_c.get('source', {}).get('url')}")
            orig = first_c.get("evidence", {}).get("original_text", "")
            high = first_c.get("evidence", {}).get("highlight_text")
            print(f"  ✓ Original Verbatim Text Length: {len(orig)}")
            print(f"  ✓ Highlight verified in original: {high in orig if high else 'None (Clean text)'}")
except Exception as e:
    print(f"  ✗ Live chat test failed: {e}")

print("\n" + "="*60)
print("✅ SYSTEM INTEGRITY TEST COMPLETE")
print("="*60)
