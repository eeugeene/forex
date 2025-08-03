# ===== dash_app/run_dash.py =====
#!/usr/bin/env python
"""
Standalone script to run the Dash analytics app
"""
import sys
import os

# Add the parent directory to Python path to import Django models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Now import and run the Dash app
from app import app

if __name__ == '__main__':
    print("Starting Dash Analytics Server...")
    print("Visit http://127.0.0.1:8050 to view the analytics dashboard")
    app.run_server(debug=True, host='127.0.0.1', port=8050)