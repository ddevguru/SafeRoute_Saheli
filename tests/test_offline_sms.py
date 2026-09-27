import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.emergency import EmergencyIncident

class OfflineSMSTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli
        self.user = User(
            name="Ananya Verma",
            email="ananya@saheli.org",
            phone="+919811122233"
        )
        self.user.set_password("AnanyaPass123!")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_twilio_form_encoded_sms_webhook(self):
        """Simulate incoming Twilio GSM SMS webhook when mobile data/Wi-Fi is offline"""
        data = {
            'From': '+919811122233',
            'Body': 'SR_SOS|+919811122233|28.6145|77.2095|TOUCH|85'
        }
        resp = self.client.post('/api/emergency/sms-webhook', data=data)
        self.assertEqual(resp.status_code, 200)
        xml = resp.get_data(as_text=True)
        self.assertIn('<Response>', xml)
        self.assertIn('SAFEROUTE SAHELI ALERT ACKNOWLEDGED', xml)
        self.assertIn('/track/', xml)

        # Check DB incident
        inc = EmergencyIncident.query.filter_by(user_id=self.user.id, status='ACTIVE').first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.trigger_type, 'SMS_TOUCH')
        self.assertAlmostEqual(float(inc.latitude), 28.6145)
        self.assertAlmostEqual(float(inc.longitude), 77.2095)
        self.assertEqual(inc.battery_percent, 85)

    def test_json_cellular_modem_webhook(self):
        """Direct JSON webhook from SIM800L cellular gateway bridge"""
        payload = {
            'from': '+919811122233',
            'body': 'SR_SOS|+919811122233|28.6200|77.2100|CLAP|90'
        }
        resp = self.client.post('/api/emergency/sms-webhook', json=payload)
        self.assertEqual(resp.status_code, 200)
        res_data = resp.get_json()
        self.assertTrue(res_data['success'])
        self.assertIn('tracking_url', res_data)
        self.assertIn('reply_sms', res_data)

    def test_unknown_number_sms_rejected(self):
        """SMS from unknown number returns 404"""
        data = {
            'From': '+919999999999',
            'Body': 'SR_SOS|+919999999999|28.6145|77.2095|TOUCH|80'
        }
        resp = self.client.post('/api/emergency/sms-webhook', data=data)
        self.assertEqual(resp.status_code, 404)
        res = resp.get_json()
        self.assertFalse(res['success'])

if __name__ == '__main__':
    unittest.main()
