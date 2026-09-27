import re
import secrets
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from backend.app.database import db
from backend.app.models.user import User, EmergencyContact, RefreshToken
from backend.app.models.admin import AuditLog
from backend.app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    jwt_required,
    roles_required
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
# In-memory OTP store for password reset simulation (in prod, backed by Redis)
otp_store = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new Saheli user account"""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    dob_str = data.get('date_of_birth')

    # Input Validations
    if not name or not email or not phone or not password:
        return jsonify({'success': False, 'error': 'Name, email, phone and password are required'}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({'success': False, 'error': 'Invalid email address format'}), 400

    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400

    if confirm_password and password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email is already registered'}), 409

    if User.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'error': 'Phone number is already registered'}), 409

    dob = None
    if dob_str:
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    user = User(
        name=name,
        email=email,
        phone=phone,
        date_of_birth=dob,
        emergency_blood_group=data.get('emergency_blood_group'),
        medical_notes=data.get('medical_notes'),
        profile_photo_url=data.get('profile_photo_url')
    )
    user.set_password(password)

    db.session.add(user)
    db.session.flush()

    audit = AuditLog(
        actor_type='USER',
        actor_id=user.id,
        action='USER_REGISTERED',
        resource='users',
        resource_id=user.id,
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    access_token = create_access_token(user.id, role='SAHELI')
    refresh_token = create_refresh_token(user.id, role='SAHELI')

    return jsonify({
        'success': True,
        'message': 'Account created successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login Saheli user"""
    data = request.get_json() or {}
    identifier = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'success': False, 'error': 'Email/Phone and password are required'}), 400

    user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'success': False, 'error': 'Account is deactivated'}), 403

    access_token = create_access_token(user.id, role='SAHELI')
    refresh_token = create_refresh_token(user.id, role='SAHELI')

    audit = AuditLog(
        actor_type='USER',
        actor_id=user.id,
        action='USER_LOGIN',
        resource='users',
        resource_id=user.id,
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Exchange valid refresh token for a new access token"""
    data = request.get_json() or {}
    token = data.get('refresh_token')
    if not token:
        return jsonify({'success': False, 'error': 'Refresh token is required'}), 400

    decoded = decode_token(token)
    if 'error' in decoded or decoded.get('type') != 'refresh':
        return jsonify({'success': False, 'error': 'Invalid or expired refresh token'}), 401

    user_id = decoded['sub']
    role = decoded.get('role', 'SAHELI')
    new_access_token = create_access_token(user_id, role=role)

    return jsonify({
        'success': True,
        'access_token': new_access_token
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current logged-in Saheli profile"""
    user = db.session.get(User, g.user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    return jsonify({'success': True, 'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@roles_required('SAHELI')
def update_profile():
    """Update profile details (name, blood group, medical notes, photo)"""
    user = db.session.get(User, g.user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()
    if 'emergency_blood_group' in data:
        user.emergency_blood_group = data['emergency_blood_group']
    if 'medical_notes' in data:
        user.medical_notes = data['medical_notes']
    if 'profile_photo_url' in data:
        user.profile_photo_url = data['profile_photo_url']

    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile updated successfully', 'user': user.to_dict()}), 200


@auth_bp.route('/privacy-settings', methods=['PUT'])
@jwt_required()
@roles_required('SAHELI')
def update_privacy_settings():
    """Update privacy settings (camera view permission, emergency override, audio)"""
    user = db.session.get(User, g.user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'guardian_camera' in data:
        user.privacy_guardian_camera = bool(data['guardian_camera'])
    if 'emergency_camera_override' in data:
        user.privacy_emergency_camera_override = bool(data['emergency_camera_override'])
    if 'audio_recording' in data:
        user.privacy_audio_recording = bool(data['audio_recording'])
    if 'live_location' in data:
        user.privacy_live_location = bool(data['live_location'])

    db.session.commit()
    return jsonify({'success': True, 'message': 'Privacy settings updated', 'privacy_settings': {
        'guardian_camera': user.privacy_guardian_camera,
        'emergency_camera_override': user.privacy_emergency_camera_override,
        'audio_recording': user.privacy_audio_recording,
        'live_location': user.privacy_live_location,
    }}), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change current user password with old password verification"""
    user = db.session.get(User, g.user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'success': False, 'error': 'Old and new passwords are required'}), 400

    if not user.check_password(old_password):
        return jsonify({'success': False, 'error': 'Incorrect current password'}), 401

    if len(new_password) < 8:
        return jsonify({'success': False, 'error': 'New password must be at least 8 characters'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed successfully'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send 6-digit password reset OTP to email or phone"""
    data = request.get_json() or {}
    identifier = data.get('email', '').strip().lower() or data.get('phone', '').strip()

    if not identifier:
        return jsonify({'success': False, 'error': 'Email or phone number is required'}), 400

    user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()
    if not user:
        # Avoid user enumeration in prod, but return success message
        return jsonify({'success': True, 'message': 'If that account exists, a 6-digit reset code has been sent'}), 200

    otp = f"{secrets.randbelow(900000) + 100000}"
    otp_store[user.email] = {'otp': otp, 'timestamp': datetime.now(timezone.utc)}

    return jsonify({
        'success': True,
        'message': f'Verification OTP sent to {identifier}',
        'debug_otp': otp  # Provided for test automation
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Verify OTP and update password"""
    data = request.get_json() or {}
    identifier = data.get('email', '').strip().lower()
    otp = str(data.get('otp', '')).strip()
    new_password = data.get('new_password', '')

    if not identifier or not otp or not new_password:
        return jsonify({'success': False, 'error': 'Email, OTP, and new password are required'}), 400

    record = otp_store.get(identifier)
    if not record or record['otp'] != otp:
        return jsonify({'success': False, 'error': 'Invalid or expired OTP'}), 400

    user = User.query.filter_by(email=identifier).first()
    if not user:
        return jsonify({'success': False, 'error': 'Account not found'}), 404

    if len(new_password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400

    user.set_password(new_password)
    del otp_store[identifier]
    db.session.commit()

    return jsonify({'success': True, 'message': 'Password reset successfully. Please login with your new password.'}), 200


# ============================================================================
# Emergency Contacts Endpoints
# ============================================================================
@auth_bp.route('/emergency-contacts', methods=['GET'])
@jwt_required()
@roles_required('SAHELI')
def get_emergency_contacts():
    """List all emergency contacts configured for current Saheli"""
    contacts = EmergencyContact.query.filter_by(user_id=g.user_id).order_by(EmergencyContact.priority_order).all()
    return jsonify({'success': True, 'contacts': [c.to_dict() for c in contacts]}), 200


@auth_bp.route('/emergency-contacts', methods=['POST'])
@jwt_required()
@roles_required('SAHELI')
def add_emergency_contact():
    """Add a new emergency contact"""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    relationship = data.get('relationship', 'Family').strip()

    if not name or not phone:
        return jsonify({'success': False, 'error': 'Name and phone are required'}), 400

    contact = EmergencyContact(
        user_id=g.user_id,
        name=name,
        phone=phone,
        relationship=relationship,
        priority_order=int(data.get('priority_order', 1)),
        notify_sms=bool(data.get('notify_sms', True)),
        notify_call=bool(data.get('notify_call', True))
    )
    db.session.add(contact)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Emergency contact added', 'contact': contact.to_dict()}), 201


@auth_bp.route('/emergency-contacts/<string:contact_id>', methods=['PUT'])
@jwt_required()
@roles_required('SAHELI')
def update_emergency_contact(contact_id):
    """Update existing emergency contact"""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=g.user_id).first()
    if not contact:
        return jsonify({'success': False, 'error': 'Contact not found'}), 404

    data = request.get_json() or {}
    if 'name' in data:
        contact.name = data['name'].strip()
    if 'phone' in data:
        contact.phone = data['phone'].strip()
    if 'relationship' in data:
        contact.relationship = data['relationship'].strip()
    if 'priority_order' in data:
        contact.priority_order = int(data['priority_order'])
    if 'notify_sms' in data:
        contact.notify_sms = bool(data['notify_sms'])
    if 'notify_call' in data:
        contact.notify_call = bool(data['notify_call'])

    db.session.commit()
    return jsonify({'success': True, 'contact': contact.to_dict()}), 200


@auth_bp.route('/emergency-contacts/<string:contact_id>', methods=['DELETE'])
@jwt_required()
@roles_required('SAHELI')
def delete_emergency_contact(contact_id):
    """Delete an emergency contact"""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=g.user_id).first()
    if not contact:
        return jsonify({'success': False, 'error': 'Contact not found'}), 404

    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contact removed'}), 200
