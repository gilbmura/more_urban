#!/usr/bin/env python3
"""
NYC Taxi Analytics - Main Application Entry Point
This file serves as a backup entry point for Render deployment.
It imports the Flask app from the backend module.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Flask app from backend
from backend.app import app

if __name__ == "__main__":
    # This will only run if the file is executed directly
    # In production, Gunicorn will import this module
    port = int(os.getenv("PORT", 3000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true")
    
    print(f"Starting NYC Taxi Analytics API on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
