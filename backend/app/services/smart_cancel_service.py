"""
SafeRoute Saheli — Smart Cancel Watchdog Service
Manages the 15-second multi-modal verification grace window and Covert Duress Security Protocol.
"""

import logging
from datetime import datetime
from flask import current_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import GuardianUser
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.admin import AuditLog
from backend.app.services.notification_service import NotificationService
from ai_ml.models.false_alarm_filter import get_false_alarm_filter, FalseAlarmFilter

logger = logging.getLogger(__name__)

class SmartCancelService:
    """
    Orchestrates post-trigger false alarm evaluation and deceptive duress disarming.
    """

    @staticmethod
    def evaluate_incident(
        incident_id: str,
        motion_samples=None,
        heart_rate_bpm: float = 75.0,
        baseline_bpm: float = 75.0,
        stress_score: float = 20.0,
        speech_transcript: str = None,
        entered_pin: str = None
    ) -> dict:
        incident = EmergencyIncident.query.get(incident_id)
        if not incident:
            return {'success': False, 'error': 'Incident not found'}

        elapsed = (datetime.utcnow() - incident.started_at).total_seconds() if incident.started_at else 0.0

        user = User.query.get(incident.user_id)
        expected_pin = getattr(user, 'safety_pin', '1234') or '1234'
        duress_pin = getattr(user, 'duress_pin', None)

        filter_engine = get_false_alarm_filter()
        assessment = filter_engine.assess_false_alarm(
            motion_samples=motion_samples,
            heart_rate_bpm=heart_rate_bpm,
            baseline_bpm=baseline_bpm,
            stress_score=stress_score,
            speech_transcript=speech_transcript,
            entered_pin=entered_pin,
            expected_pin=expected_pin,
            duress_pin=duress_pin,
            elapsed_seconds=elapsed,
            trigger_type=incident.trigger_type
        )

        return {
            'success': True,
            'incident_id': incident.id,
            'incident_status': incident.status,
            'assessment': assessment
        }

    @staticmethod
    def process_smart_cancel(
        incident_id: str,
        user_id: str,
        entered_pin: str,
        speech_transcript: str = None,
        motion_samples=None,
        heart_rate_bpm: float = 75.0,
        socketio = None
    ) -> dict:
        incident = EmergencyIncident.query.get(incident_id)
        if not incident:
            return {'success': False, 'error': 'Incident not found'}

        if incident.user_id != user_id:
            return {'success': False, 'error': 'Unauthorized to cancel this incident'}

        if incident.status not in {'ACTIVE', 'ACTIVE_ESCALATED', 'DURESS_ESCALATED'}:
            return {'success': False, 'error': f'Incident cannot be cancelled from state {incident.status}'}

        user = User.query.get(user_id)
        expected_pin = getattr(user, 'safety_pin', '1234') or '1234'
        duress_pin = getattr(user, 'duress_pin', None)

        elapsed = (datetime.utcnow() - incident.started_at).total_seconds() if incident.started_at else 0.0
        filter_engine = get_false_alarm_filter()

        assessment = filter_engine.assess_false_alarm(
            motion_samples=motion_samples,
            heart_rate_bpm=heart_rate_bpm,
            speech_transcript=speech_transcript,
            entered_pin=entered_pin,
            expected_pin=expected_pin,
            duress_pin=duress_pin,
            elapsed_seconds=elapsed,
            trigger_type=incident.trigger_type
        )

        # 1. COVERT DURESS ESCALATION
        if assessment['is_duress']:
            logger.warning(f"COVERT DURESS DETECTED for incident {incident_id} by user {user_id}")
            incident.status = 'DURESS_ESCALATED'
            incident.cancellation_reason = 'COVERT DURESS CODE ENTERED — User under duress or physical coercion'
            
            # Audit log for forensics
            audit = AuditLog(
                actor_type='USER',
                actor_id=user_id,
                action='DURESS_ESCALATION_TRIGGERED',
                resource='emergency_incidents',
                resource_id=incident.id,
                details={'reason': 'Covert duress PIN entered', 'entered_pin': '***'}
            )
            db.session.add(audit)
            db.session.commit()

            # Covert push notification to all linked guardians
            guardian_links = GuardianUser.query.filter_by(saheli_id=user.id).all()
            for link in guardian_links:
                if link.guardian:
                    NotificationService.send_fcm_notification(
                        user_id=link.guardian.id,
                        title="🚨 SILENT DURESS EMERGENCY",
                        body=f"URGENT: {user.name} entered the Covert Duress PIN! Coercion suspected. Contact emergency services immediately!",
                        data={
                            'type': 'SILENT_DURESS',
                            'incident_id': incident.id,
                            'latitude': str(incident.latitude),
                            'longitude': str(incident.longitude)
                        }
                    )

            if socketio:
                socketio.emit('admin_silent_duress_alert', {
                    'incident_id': incident.id,
                    'user_id': user.id,
                    'user_name': user.name,
                    'latitude': float(incident.latitude),
                    'longitude': float(incident.longitude),
                    'status': 'DURESS_ESCALATED'
                }, room='admin_dashboard')

            # Deceptive response: Shows success to the attacker while notifying responders
            return {
                'success': True,
                'status': 'CANCELLED',
                'is_duress': True,
                'display_message': 'Emergency Alert Disarmed Successfully',
                'deceptive_mode': True
            }

        # 2. VALID NORMAL CANCELLATION
        if assessment['is_pin_valid'] and assessment['pin_status'] == 'VALID_CANCEL':
            incident.status = 'CANCELLED_FALSE_ALARM'
            incident.cancellation_reason = 'User authenticated cancellation PIN (False Alarm)'
            incident.resolved_at = datetime.utcnow()

            # Deactivate tracking sessions
            for session in incident.tracking_sessions:
                session.is_active = False

            audit = AuditLog(
                actor_type='USER',
                actor_id=user_id,
                action='EMERGENCY_SMART_CANCELLED',
                resource='emergency_incidents',
                resource_id=incident.id,
                details={'reason': 'False alarm verified by PIN', 'false_alarm_prob': assessment['false_alarm_probability']}
            )
            db.session.add(audit)
            db.session.commit()

            if socketio:
                payload = {'incident_id': incident.id, 'status': 'CANCELLED_FALSE_ALARM'}
                socketio.emit('emergency_cancelled', payload, room=f"saheli_{user_id}")
                socketio.emit('admin_emergency_cancelled', payload, room='admin_dashboard')

            return {
                'success': True,
                'status': 'CANCELLED_FALSE_ALARM',
                'is_duress': False,
                'display_message': 'Alert disarmed. Logged as false alarm.',
                'assessment': assessment
            }

        # 3. INVALID PIN
        return {
            'success': False,
            'error': 'Incorrect cancellation PIN',
            'is_pin_valid': False,
            'pin_status': assessment['pin_status'],
            'remaining_grace_seconds': assessment['grace_window']['remaining_seconds']
        }

    @staticmethod
    def get_verification_status(incident_id: str) -> dict:
        incident = EmergencyIncident.query.get(incident_id)
        if not incident:
            return {'success': False, 'error': 'Incident not found'}

        elapsed = (datetime.utcnow() - incident.started_at).total_seconds() if incident.started_at else 0.0
        remaining = max(0.0, FalseAlarmFilter.DEFAULT_GRACE_WINDOW_SECONDS - elapsed)

        return {
            'success': True,
            'incident_id': incident.id,
            'status': incident.status,
            'elapsed_seconds': round(elapsed, 1),
            'remaining_grace_seconds': round(remaining, 1),
            'window_expired': elapsed >= FalseAlarmFilter.DEFAULT_GRACE_WINDOW_SECONDS
        }
