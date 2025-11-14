"""
Vercel Serverless Function entry point
Flask app wrapper for Vercel
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a WSGI application
# Flask app is already a WSGI application, so we can export it directly
application = app

