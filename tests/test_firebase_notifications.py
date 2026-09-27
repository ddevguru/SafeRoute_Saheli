import unittest
import json
from datetime import datetime
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import DeviceToken
from backend.app.models.emergency import EmergencyIncident, EmergencyNotification, NotificationLog
from backend.app.auth.jwt_handler import create_access_token
from backend.app.services.notification_service import NotificationService
from backend.app.notification.firebase_admin_client import FirebaseAdminClient

class TestFirebaseNotifications(unittest.TestCase):
    """
    Automated Unit & Integration Test Suite for Phase 4:
    Firebase Cloud Messaging (FCM) & Multi-Tier Notifications
    """

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Seed Saheli User
        self.saheli = User(
            name="Riya Sharma",
            email="riya.sharma@example.com",
            phone="+919876543210"
        )
        self.saheli.set_password("SaheliPass@2026")
        db.session.add(self.saheli)

        # Seed Guardian
        self.guardian = Guardian(
            name="Sunita Sharma",
            relationship="Mother",
            phone="+919876500000",
            email="sunita.guardian@example.com",
            username="sunita_mother"
        )
        self.guardian.set_password("GuardianPass@2026")
        db.session.add(self.guardian)
        db.session.flush()

        # Link Guardian to Saheli
        self.link = GuardianUser(
            saheli_id=self.saheli.id,
            guardian_id=self.guardian.id,
            relationship_label="Mother",
            can_view_location=True,
            can_view_camera=True,
            emergency_override_camera=True,
            is_primary=True
        )
        db.session.add(self.link)
        db.session.commit()

        # Auth Tokens
        self.saheli_token = create_access_token(self.saheli.id, role='SAHELI')
        self.guardian_token = create_access_token(self.guardian.id, role='GUARDIAN')
        self.saheli_headers = {'Authorization': f"Bearer {self.saheli_token}"}
        self.guardian_headers = {'Authorization': f"Bearer {self.guardian_token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_firebase_client_mock_initialization(self):
        """Verify FirebaseAdminClient operates safely in test / mock environment"""
        FirebaseAdminClient.initialize(self.app.config)
        self.assertTrue(FirebaseAdminClient._initialized)
        self.assertTrue(FirebaseAdminClient._is_mock)

        res = FirebaseAdminClient.send_push(
            token="test-token-fcm-123456",
            title="Test Title",
            body="Test Message Body",
            data={"key": "value"}
        )
        self.assertTrue(res['success'])
        self.assertEqual(res['status'], 'DELIVERED')
        self.assertTrue(res['is_mock'])

    def test_device_token_registration_and_listing(self):
        """Test POST and GET /api/notifications/tokens for Saheli and Guardian"""
        # 1. Register Saheli Token
        res_saheli = self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'saheli-fcm-token-android-111',
            'platform': 'ANDROID'
        }, headers=self.saheli_headers)
        self.assertEqual(res_saheli.status_code, 200)
        self.assertTrue(res_saheli.get_json()['success'])

        # 2. Register Guardian Token
        res_guardian = self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'guardian-fcm-token-ios-222',
            'platform': 'IOS'
        }, headers=self.guardian_headers)
        self.assertEqual(res_guardian.status_code, 200)
        self.assertTrue(res_guardian.get_json()['success'])

        # 3. List Saheli Tokens
        res_list = self.client.get('/api/notifications/tokens', headers=self.saheli_headers)
        self.assertEqual(res_list.status_code, 200)
        tokens = res_list.get_json()['tokens']
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0]['fcm_token'], 'saheli-fcm-token-android-111')
        self.assertEqual(tokens[0]['platform'], 'ANDROID')

        # 4. List Guardian Tokens
        res_g_list = self.client.get('/api/notifications/tokens', headers=self.guardian_headers)
        self.assertEqual(res_g_list.status_code, 200)
        g_tokens = res_g_list.get_json()['tokens']
        self.assertEqual(len(g_tokens), 1)
        self.assertEqual(g_tokens[0]['fcm_token'], 'guardian-fcm-token-ios-222')
        self.assertEqual(g_tokens[0]['platform'], 'IOS')

    def test_device_token_revocation(self):
        """Test DELETE /api/notifications/tokens deactivates tokens upon logout"""
        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'token-to-revoke-999',
            'platform': 'ANDROID'
        }, headers=self.saheli_headers)

        res_del = self.client.delete('/api/notifications/tokens', json={
            'fcm_token': 'token-to-revoke-999'
        }, headers=self.saheli_headers)
        self.assertEqual(res_del.status_code, 200)

        # Ensure token is now inactive in DB
        t = DeviceToken.query.filter_by(fcm_token='token-to-revoke-999').first()
        self.assertIsNotNone(t)
        self.assertFalse(t.is_active)

    def test_send_test_push_dispatch(self):
        """Test POST /api/notifications/test sends simulated push to registered tokens"""
        # Register a token first
        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'active-qa-token-555',
            'platform': 'ANDROID'
        }, headers=self.saheli_headers)

        res = self.client.post('/api/notifications/test', json={
            'title': 'Test Push',
            'body': 'Testing payload delivery'
        }, headers=self.saheli_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()['success'])
        self.assertEqual(res.get_json()['summary']['success_count'], 1)

    def test_emergency_push_notification_dispatch(self):
        """
        Verify Requirement 23 & 48:
        High-priority emergency push sent to linked guardians with required title, body, and payload.
        """
        # 1. Register guardian FCM token
        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'mother-emergency-fcm-token-777',
            'platform': 'ANDROID'
        }, headers=self.guardian_headers)

        # 2. Create emergency incident
        incident = EmergencyIncident(
            user_id=self.saheli.id,
            trigger_type='TOUCH',
            status='ACTIVE',
            latitude=28.6139,
            longitude=77.2090,
            battery_percent=85,
            confidence=1.0,
            started_at=datetime.utcnow()
        )
        db.session.add(incident)
        db.session.commit()

        # 3. Dispatch emergency push
        tracking_url = "https://saheli.safe/track/test-token-secure"
        tracking_token = "test-token-secure"
        results = NotificationService.sendEmergencyPush(
            incident=incident,
            user=self.saheli,
            guardians=[self.guardian],
            tracking_url=tracking_url,
            tracking_token=tracking_token
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'DELIVERED')
        self.assertEqual(results[0]['guardian_id'], self.guardian.id)

        # 4. Verify DB records
        notif = EmergencyNotification.query.filter_by(incident_id=incident.id).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.channel, 'FCM')
        self.assertEqual(notif.recipient_id, self.guardian.id)

        log = NotificationLog.query.filter_by(incident_id=incident.id, channel='FCM').first()
        self.assertIsNotNone(log)
        payload = json.loads(log.payload)
        self.assertEqual(payload['title'], "🚨 Emergency Alert")
        self.assertIn("Riya Sharma has triggered an emergency", payload['body'])
        self.assertEqual(payload['data']['tracking_token'], "test-token-secure")
        self.assertEqual(payload['data']['trigger_type'], "TOUCH")

    def test_battery_warning_and_critical_escalation(self):
        """
        Verify Requirement 48:
        - Low battery (20%) notifies user.
        - Critical battery (8%) escalates to notify both user and guardian!
        """
        # Register tokens for both
        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'saheli-battery-token-111',
            'platform': 'ANDROID'
        }, headers=self.saheli_headers)

        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'guardian-battery-token-222',
            'platform': 'IOS'
        }, headers=self.guardian_headers)

        # 1. Normal low battery (20%)
        res_warn = NotificationService.sendBatteryWarning(self.saheli.id, battery_percent=20)
        self.assertEqual(len(res_warn), 1)
        self.assertEqual(res_warn[0]['recipient'], 'USER')

        # 2. Critical battery (8%) - escalates to guardian
        res_crit = NotificationService.sendBatteryWarning(self.saheli.id, battery_percent=8)
        self.assertEqual(len(res_crit), 1)

        # Verify guardian alert log was recorded
        g_log = NotificationLog.query.filter_by(channel='FCM_GUARDIAN_ALERT').first()
        self.assertIsNotNone(g_log)
        payload = json.loads(g_log.payload)
        self.assertIn("critically low", payload['body'])

    def test_route_deviation_notification(self):
        """Verify Requirement 32 & 48: Route deviation notification"""
        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'saheli-deviation-token-333',
            'platform': 'ANDROID'
        }, headers=self.saheli_headers)

        res = NotificationService.sendRouteDeviation(
            user_id=self.saheli.id,
            route_id="route-cp-safe-01",
            deviation_meters=145.5,
            alternative_route_summary="Via Barakhamba Road Safe Zone"
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['status'], 'DELIVERED')

    def test_device_offline_notification(self):
        """Verify Requirement 48 & 68: Device offline notification"""
        self.client.post('/api/notifications/tokens', json={
            'fcm_token': 'saheli-offline-token-444',
            'platform': 'ANDROID'
        }, headers=self.saheli_headers)

        res = NotificationService.sendDeviceOffline(
            user_id=self.saheli.id,
            device_id="ESP32-WEARABLE-001",
            last_seen=datetime.utcnow().isoformat()
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['status'], 'DELIVERED')

    def test_get_notification_logs_api(self):
        """Test GET /api/notifications/logs"""
        # Generate an SMS log
        NotificationService.send_emergency_sms(
            recipient_phone="+919876543210",
            message_text="Emergency Test SMS",
            incident_id="test-inc-001"
        )

        res = self.client.get('/api/notifications/logs', headers=self.saheli_headers)
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()['logs']
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['channel'], 'SMS')

if __name__ == '__main__':
    unittest.main()
