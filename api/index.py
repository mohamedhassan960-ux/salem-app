"""
Vercel Serverless Function Entrypoint — Oxygen Medical RAG
Exports the FastAPI application instance for Vercel Python Runtime.
"""

import os
import sys

# Ensure repository root and scripts directory are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from api.main import app
