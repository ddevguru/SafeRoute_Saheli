import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app, socketio

env_name = os.getenv('FLASK_ENV', 'development')
app = create_app(env_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    print(f"==================================================")
    print(f"  SAFEROUTE SAHELI ENTERPRISE BACKEND SERVER      ")
    print(f"  'Stay Connected. Stay Aware. Stay Safe.'        ")
    print(f"  Mode: {env_name.upper()} | Port: {port}          ")
    print(f"==================================================")
    socketio.run(app, host=host, port=port, debug=app.config.get('DEBUG', False), allow_unsafe_werkzeug=True)
