import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.admin import AdminUser, AuditLog
from backend.app.models.device import Device
from backend.app.auth.jwt_handler import create_access_token

class SecurityComplianceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli
        self.user = User(name="Test Saheli", email="saheli@example.com", phone="+919000000001")
        self.user.set_password("SaheliSecure@123")
        db.session.add(self.user)

        # Seed Admin
        self.admin = AdminUser(username="sec_admin", email="admin@saheli.org", role="ADMIN")
        self.admin.set_password("AdminComplex#2026")
        db.session.add(self.admin)

        # Seed Device
        self.device = Device(device_id="DEV-SEC-01", device_type="WEARABLE_ESP32", assigned_user_id=self.user.id)
        self.device.set_secret("secure_hw_key_999")
        db.session.add(self.device)
        db.session.commit()

        self.user_token = create_access_token(self.user.id, role='SAHELI')
        self.admin_token = create_access_token(self.admin.id, role='ADMIN')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_security_headers_present(self):
        """All HTTP responses must include enterprise security compliance headers"""
        resp = self.client.get('/api/health')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(resp.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertIn('max-age', resp.headers.get('Strict-Transport-Security', ''))
        self.assertEqual(resp.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    def test_rbac_unauthenticated_denied(self):
        """Unauthenticated requests to admin endpoints are blocked (401)"""
        resp = self.client.get('/api/admin/dashboard')
        self.assertEqual(resp.status_code, 401)

    def test_rbac_saheli_role_forbidden_from_admin(self):
        """Saheli users cannot access administrative command center (403)"""
        headers = {'Authorization': f"Bearer {self.user_token}"}
        resp = self.client.get('/api/admin/dashboard', headers=headers)
        self.assertEqual(resp.status_code, 403)

    def test_rbac_admin_role_granted(self):
        """Authenticated Admin users have full dashboard access"""
        headers = {'Authorization': f"Bearer {self.admin_token}"}
        resp = self.client.get('/api/admin/dashboard', headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('metrics', data)

    def test_password_bcrypt_hashing_and_verification(self):
        """Passwords must never be stored plaintext and must be verified using bcrypt"""
        self.assertTrue(self.user.check_password("SaheliSecure@123"))
        self.assertFalse(self.user.check_password("WrongPassword!"))
        self.assertNotEqual(self.user.password_hash, "SaheliSecure@123")
        self.assertTrue(self.user.password_hash.startswith("$2b$") or self.user.password_hash.startswith("$2a$"))

    def test_hardware_device_secret_authentication(self):
        """Hardware devices verify secrets with cryptographic comparison"""
        self.assertTrue(self.device.verify_secret("secure_hw_key_999"))
        self.assertFalse(self.device.verify_secret("wrong_secret_key"))

    def test_audit_log_persisted(self):
        """Audit log creation and retrieval"""
        log = AuditLog(
            actor_type='ADMIN',
            actor_id=self.admin.id,
            action='SECURITY_POLICY_UPDATE',
            resource='security',
            details={'ip': '127.0.0.1', 'policy': 'STRICT_SSL'}
        )
        db.session.add(log)
        db.session.commit()

        headers = {'Authorization': f"Bearer {self.admin_token}"}
        resp = self.client.get('/api/admin/audit-logs', headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['audit_logs']), 1)
        self.assertEqual(data['audit_logs'][0]['action'], 'SECURITY_POLICY_UPDATE')

if __name__ == '__main__':
    unittest.main()
