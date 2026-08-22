@echo off
cd /d "c:\Users\moham\OneDrive\Apps\اوكسجين"
set AUTH_ENABLED=true
set OXYGEN_API_KEY=oxg_s4W_vK8L9mN2pQ5rT1xY7zB0cD3eF6gH
set LLM_PROVIDER=gemini
set GEMINI_MODEL=gemini-2.5-flash
set CORS_ORIGINS=*
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

