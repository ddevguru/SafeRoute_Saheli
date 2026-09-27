"""
SafeRoute Saheli — Root Application Entrypoint for Gunicorn & Cloud Deployments
"""

import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import create_app, socketio

env_name = os.getenv('FLASK_ENV', 'production')
app = create_app(env_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    socketio.run(app, host=host, port=port, debug=app.config.get('DEBUG', False), allow_unsafe_werkzeug=True)
