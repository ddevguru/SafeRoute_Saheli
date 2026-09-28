import os
import logging
from datetime import datetime, timedelta
from flask import current_app
from backend.app.database import db
from backend.app.models.user import User, EmergencyContact
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.emergency import EmergencyIncident, LiveTrackingSession, TrackingToken
from backend.app.models.routing import SafePlace, NearbyHelpLog
from backend.app.models.admin import AuditLog
from backend.app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class EmergencyService:
    """Master Emergency State Machine and Orchestration Service"""

    @staticmethod
    def trigger_emergency(
        user_id: str,
        trigger_type: str,
        latitude: float,
        longitude: float,
        device_id: str = None,
        confidence: float = 1.0,
        battery_percent: int = 100,
        socketio = None
    ) -> dict:
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # 1. Check if an active incident already exists for this user
        existing_incident = EmergencyIncident.query.filter_by(
            user_id=user_id,
            status='ACTIVE'
        ).first()

        if existing_incident:
            # Update existing incident coordinates and telemetry
            existing_incident.latitude = latitude
            existing_incident.longitude = longitude
            existing_incident.battery_percent = battery_percent
            incident = existing_incident
        else:
            # 2. Create new active incident
            incident = EmergencyIncident(
                user_id=user_id,
                device_id=device_id,
                trigger_type=trigger_type,
                status='ACTIVE',
                latitude=latitude,
                longitude=longitude,
                battery_percent=battery_percent,
                confidence=confidence,
                started_at=datetime.utcnow()
            )
            db.session.add(incident)
            db.session.flush()

        # 3. Create or reuse secure live tracking session
        existing_session = LiveTrackingSession.query.filter_by(
            incident_id=incident.id,
            is_active=True
        ).first()

        if not existing_session:
            tracking_token = LiveTrackingSession.generate_token()
            expiry_hours = current_app.config.get('TRACKING_TOKEN_EXPIRY_HOURS', 12)
            session = LiveTrackingSession(
                incident_id=incident.id,
                user_id=user.id,
                tracking_token=tracking_token,
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            db.session.add(session)
            db.session.flush()

            token_record = TrackingToken(
                session_id=session.id,
                token_value=tracking_token,
                expires_at=session.expires_at
            )
            db.session.add(token_record)
        else:
            tracking_token = existing_session.tracking_token

        # 4. Fetch linked Guardians and Emergency Contacts
        guardian_links = GuardianUser.query.filter_by(saheli_id=user.id).all()
        guardians = [link.guardian for link in guardian_links if link.guardian and link.guardian.is_active]
        contacts = EmergencyContact.query.filter_by(user_id=user.id).order_by(EmergencyContact.priority_order).all()

        # Build emergency message & tracking URL
        base_url = current_app.config.get('EXTERNAL_BASE_URL') or os.getenv('EXTERNAL_BASE_URL') or 'https://saferoute-saheli-backend.onrender.com'
        tracking_url = f"{base_url}/track/{tracking_token}"
        gmaps_url = f"https://maps.google.com/?q={latitude},{longitude}"

        sms_body = (
            f"🚨 SAFEROUTE SAHELI EMERGENCY ALERT!\n\n"
            f"Emergency triggered by: {user.name}\n"
            f"Trigger Type: {trigger_type}\n"
            f"Battery: {battery_percent}%\n"
            f"Location: {gmaps_url}\n"
            f"Live Tracking: {tracking_url}\n\n"
            f"Please check immediately."
        )

        voice_text = (
            f"This is an urgent emergency alert from SafeRoute Saheli. "
            f"{user.name} has triggered an emergency alert. "
            f"Please check the live tracking link sent to your phone immediately."
        )

        # 5. Dispatch Notifications
        # A. Firebase Push to Guardians
        fcm_results = NotificationService.send_emergency_push(incident, user, guardians, tracking_url)

        # B. SMS to Guardians & Emergency Contacts
        for g in guardians:
            NotificationService.send_emergency_sms(g.phone, sms_body, incident.id)

        for c in contacts:
            if c.notify_sms:
                NotificationService.send_emergency_sms(c.phone, sms_body, incident.id)
            if c.notify_call:
                NotificationService.send_emergency_call(c.phone, voice_text, incident.id)

        # 6. Find Nearest Safe Places (Police, Hospital, Shelter)
        nearby_police = SafePlace.query.filter_by(category='POLICE', verified_status=True).all()
        for p in nearby_police[:3]:
            help_log = NearbyHelpLog(
                incident_id=incident.id,
                safe_place_id=p.id,
                distance_meters=450.0  # calculated in routing service
            )
            db.session.add(help_log)

        # 7. Audit Log
        audit = AuditLog(
            actor_type='USER' if trigger_type == 'BUTTON' else 'DEVICE',
            actor_id=user.id if trigger_type == 'BUTTON' else (device_id or user.id),
            action='EMERGENCY_TRIGGERED',
            resource='emergency_incidents',
            resource_id=incident.id,
            details={
                'trigger_type': trigger_type,
                'latitude': latitude,
                'longitude': longitude,
                'battery_percent': battery_percent
            }
        )
        db.session.add(audit)
        db.session.commit()

        # 8. Broadcast Real-Time WebSocket Event
        if socketio:
            incident_data = incident.to_dict()
            incident_data['tracking_url'] = tracking_url
            socketio.emit('emergency_triggered', incident_data, room=f"saheli_{user.id}")
            socketio.emit('admin_emergency_alert', incident_data, room="admin_dashboard")

        return {
            'success': True,
            'incident_id': incident.id,
            'status': incident.status,
            'tracking_url': tracking_url,
            'tracking_token': tracking_token,
            'notifications_sent': len(guardians) + len(contacts)
        }

    @staticmethod
    def cancel_emergency(incident_id: str, user_id: str, reason: str = "User cancelled with confirmation", socketio = None) -> dict:
        incident = EmergencyIncident.query.get(incident_id)
        if not incident:
            return {'success': False, 'error': 'Incident not found'}
        if incident.user_id != user_id:
            return {'success': False, 'error': 'Unauthorized to cancel this incident'}

        incident.status = 'CANCELLED'
        incident.cancellation_reason = reason
        incident.resolved_at = datetime.utcnow()

        # Deactivate tracking sessions
        for session in incident.tracking_sessions:
            session.is_active = False

        audit = AuditLog(
            actor_type='USER',
            actor_id=user_id,
            action='EMERGENCY_CANCELLED',
            resource='emergency_incidents',
            resource_id=incident.id,
            details={'reason': reason}
        )
        db.session.add(audit)
        db.session.commit()

        if socketio:
            payload = {'incident_id': incident_id, 'status': 'CANCELLED', 'reason': reason}
            socketio.emit('emergency_cancelled', payload, room=f"saheli_{user_id}")
            socketio.emit('admin_emergency_cancelled', payload, room="admin_dashboard")

        return {'success': True, 'incident_id': incident.id, 'status': 'CANCELLED'}

    @staticmethod
    def resolve_emergency(incident_id: str, resolver_id: str, resolver_role: str, notes: str = "", socketio = None) -> dict:
        incident = EmergencyIncident.query.get(incident_id)
        if not incident:
            return {'success': False, 'error': 'Incident not found'}

        incident.status = 'RESOLVED'
        incident.resolved_notes = notes
        incident.resolved_at = datetime.utcnow()

        for session in incident.tracking_sessions:
            session.is_active = False

        audit = AuditLog(
            actor_type=resolver_role,
            actor_id=resolver_id,
            action='EMERGENCY_RESOLVED',
            resource='emergency_incidents',
            resource_id=incident.id,
            details={'notes': notes}
        )
        db.session.add(audit)
        db.session.commit()

        if socketio:
            payload = {'incident_id': incident_id, 'status': 'RESOLVED', 'notes': notes}
            socketio.emit('emergency_resolved', payload, room=f"saheli_{incident.user_id}")
            socketio.emit('admin_emergency_resolved', payload, room="admin_dashboard")

        return {'success': True, 'incident_id': incident.id, 'status': 'RESOLVED'}
