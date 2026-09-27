from functools import wraps
from datetime import datetime, timedelta, timezone
import jwt
from flask import request, jsonify, current_app, g
from backend.app.models.user import User, RefreshToken
from backend.app.models.guardian import Guardian
from backend.app.models.admin import AdminUser, AuditLog
from backend.app.database import db

def create_access_token(identity: str, role: str, extra_claims: dict = None) -> str:
    """Generate signed JWT access token"""
    now = datetime.now(timezone.utc)
    payload = {
        'sub': identity,
        'role': role,
        'iat': now,
        'exp': now + current_app.config['JWT_EXPIRATION_DELTA']
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

def create_refresh_token(identity: str, role: str) -> str:
    """Generate signed JWT refresh token"""
    now = datetime.now(timezone.utc)
    payload = {
        'sub': identity,
        'role': role,
        'type': 'refresh',
        'iat': now,
        'exp': now + current_app.config['JWT_REFRESH_EXPIRATION_DELTA']
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

def decode_token(token: str) -> dict:
    """Decode and validate JWT token signature and expiration"""
    try:
        return jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': 'TOKEN_EXPIRED'}
    except jwt.InvalidTokenError:
        return {'error': 'INVALID_TOKEN'}

def jwt_required(optional: bool = False):
    """Decorator to protect endpoints with JWT authentication"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                if optional:
                    g.current_user = None
                    g.current_role = None
                    return fn(*args, **kwargs)
                return jsonify({'success': False, 'error': 'Authorization header is missing'}), 401
            
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'success': False, 'error': 'Invalid Authorization header format'}), 401
            
            token = parts[1]
            decoded = decode_token(token)
            if 'error' in decoded:
                return jsonify({'success': False, 'error': decoded['error']}), 401
            
            g.user_id = decoded.get('sub')
            g.current_role = decoded.get('role')
            g.claims = decoded
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def roles_required(*allowed_roles):
    """Decorator enforcing role-based access control (RBAC)"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(g, 'current_role') or g.current_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': f'Access forbidden: Required role in {allowed_roles}, got {getattr(g, "current_role", None)}'
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
