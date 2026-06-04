"""Vercel serverless entry point for FastAPI"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from _main import app

# Vercel requires a handler variable pointing to the ASGI app
handler = app
