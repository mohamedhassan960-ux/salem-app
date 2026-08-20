@echo off
set AUTH_ENABLED=false
set PYTHONUNBUFFERED=1
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --env-file .env
