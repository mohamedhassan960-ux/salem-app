@echo off
title Oxygen Medical RAG Explorer
echo ========================================================
echo   Launching Oxygen Medical RAG Explorer Dashboard...
echo ========================================================
cd /d "%~dp0"
python -m streamlit run app_rag_explorer.py --server.port=8501 --server.headless=false
pause
