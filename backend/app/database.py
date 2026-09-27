import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_uuid() -> str:
    """Generate RFC 4122 compliant UUID v4 string"""
    return str(uuid.uuid4())
