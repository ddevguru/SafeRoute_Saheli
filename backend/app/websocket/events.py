import logging
from flask import request
from flask_socketio import emit, join_room, leave_room
from backend.app.auth.jwt_handler import decode_token

logger = logging.getLogger(__name__)

def register_socketio_events(socketio):
    """Register all Socket.IO real-time event listeners and room dispatchers"""

    @socketio.on('connect')
    def handle_connect():
        auth = request.args.get('token')
        if not auth and hasattr(request, 'headers'):
            auth = request.headers.get('Authorization', '').replace('Bearer ', '')

        if auth:
            decoded = decode_token(auth)
            if 'error' not in decoded:
                user_id = decoded['sub']
                role = decoded.get('role', 'SAHELI')
                logger.info(f"Socket connected: User {user_id} Role {role}")
                emit('connection_established', {'status': 'AUTHENTICATED', 'user_id': user_id, 'role': role})
                return

        logger.info(f"Anonymous socket connected: {request.sid}")
        emit('connection_established', {'status': 'ANONYMOUS', 'sid': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Socket disconnected: {request.sid}")

    @socketio.on('join_user_room')
    def handle_join_user(data):
        user_id = data.get('user_id')
        if user_id:
            room = f"saheli_{user_id}"
            join_room(room)
            logger.info(f"SID {request.sid} joined user room: {room}")
            emit('room_joined', {'room': room}, to=request.sid)

    @socketio.on('join_guardian_room')
    def handle_join_guardian(data):
        guardian_id = data.get('guardian_id')
        saheli_ids = data.get('saheli_ids', [])
        for sid in saheli_ids:
            room = f"saheli_{sid}"
            join_room(room)
            logger.info(f"Guardian {guardian_id} joined room: {room}")
        emit('room_joined', {'rooms': [f"saheli_{sid}" for sid in saheli_ids]}, to=request.sid)

    @socketio.on('join_admin_room')
    def handle_join_admin(data):
        token = data.get('token')
        if token:
            decoded = decode_token(token)
            if decoded.get('role') == 'ADMIN':
                join_room('admin_dashboard')
                logger.info(f"Admin joined admin_dashboard: {request.sid}")
                emit('room_joined', {'room': 'admin_dashboard'}, to=request.sid)

    @socketio.on('ping_status')
    def handle_ping():
        emit('pong_status', {'server_status': 'ONLINE'})

    @socketio.on('join_audio_room')
    def handle_join_audio(data):
        """Join real-time ambient acoustic listening room for an active emergency"""
        incident_id = data.get('incident_id')
        token = data.get('token')
        if not incident_id:
            emit('audio_error', {'error': 'incident_id required'})
            return

        room = f"audio_stream_{incident_id}"
        join_room(room)
        logger.info(f"SID {request.sid} joined live audio room: {room}")
        emit('audio_room_joined', {'room': room, 'incident_id': incident_id}, to=request.sid)

    @socketio.on('stream_audio_chunk')
    def handle_stream_audio_chunk(data):
        """Rebroadcast raw PCM / encoded audio chunk from wearable mic to authorized listeners"""
        incident_id = data.get('incident_id')
        chunk = data.get('chunk')  # Base64 or binary audio payload
        if incident_id and chunk:
            room = f"audio_stream_{incident_id}"
            emit('audio_chunk_received', {
                'incident_id': incident_id,
                'chunk': chunk,
                'sample_rate': data.get('sample_rate', 16000),
                'timestamp': data.get('timestamp')
            }, room=room, include_self=False)

    @socketio.on('leave_audio_room')
    def handle_leave_audio(data):
        """Leave live acoustic room"""
        incident_id = data.get('incident_id')
        if incident_id:
            room = f"audio_stream_{incident_id}"
            leave_room(room)
            emit('audio_room_left', {'room': room}, to=request.sid)

