import unittest
import json
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User, EmergencyContact
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import DeviceToken

class Phase2AuthGuardianTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_saheli_registration_and_duplicates(self):
        payload = {
            'name': 'Kavita Verma',
            'email': 'kavita@safe.in',
            'phone': '+919811122233',
            'password': 'SecurePassword@2026',
            'confirm_password': 'SecurePassword@2026',
            'emergency_blood_group': 'B+',
            'medical_notes': 'Allergic to penicillin'
        }
        res = self.client.post('/api/auth/register', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['emergency_blood_group'], 'B+')

        # Test duplicate email
        res_dup_email = self.client.post('/api/auth/register', json=payload)
        self.assertEqual(res_dup_email.status_code, 409)
        self.assertIn('Email is already registered', res_dup_email.get_json()['error'])

        # Test duplicate phone with different email
        payload2 = dict(payload)
        payload2['email'] = 'other_email@safe.in'
        res_dup_phone = self.client.post('/api/auth/register', json=payload2)
        self.assertEqual(res_dup_phone.status_code, 409)
        self.assertIn('Phone number is already registered', res_dup_phone.get_json()['error'])

    def test_saheli_profile_and_privacy_settings(self):
        user = User(name='Deepa', email='deepa@safe.in', phone='+919844455566')
        user.set_password('DeepaPass@2026')
        db.session.add(user)
        db.session.commit()

        login_res = self.client.post('/api/auth/login', json={'email': 'deepa@safe.in', 'password': 'DeepaPass@2026'})
        token = login_res.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Update Profile
        update_payload = {
            'name': 'Deepa Sen',
            'emergency_blood_group': 'AB+',
            'medical_notes': 'Asthma inhaler in purse'
        }
        res_up = self.client.put('/api/auth/profile', json=update_payload, headers=headers)
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()['user']['name'], 'Deepa Sen')
        self.assertEqual(res_up.get_json()['user']['emergency_blood_group'], 'AB+')

        # Update Privacy Settings
        privacy_payload = {
            'guardian_camera': False,
            'emergency_camera_override': True,
            'audio_recording': True,
            'live_location': True
        }
        res_priv = self.client.put('/api/auth/privacy-settings', json=privacy_payload, headers=headers)
        self.assertEqual(res_priv.status_code, 200)
        priv_data = res_priv.get_json()['privacy_settings']
        self.assertFalse(priv_data['guardian_camera'])
        self.assertTrue(priv_data['emergency_camera_override'])

    def test_password_change_and_forgot_reset_flow(self):
        user = User(name='Sneha', email='sneha@safe.in', phone='+919855566677')
        user.set_password('OldPassword@123')
        db.session.add(user)
        db.session.commit()

        login_res = self.client.post('/api/auth/login', json={'email': 'sneha@safe.in', 'password': 'OldPassword@123'})
        token = login_res.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Change Password with wrong old password
        res_wrong = self.client.post('/api/auth/change-password', json={
            'old_password': 'WrongPassword!',
            'new_password': 'NewPassword@456'
        }, headers=headers)
        self.assertEqual(res_wrong.status_code, 401)

        # Change Password successfully
        res_change = self.client.post('/api/auth/change-password', json={
            'old_password': 'OldPassword@123',
            'new_password': 'NewPassword@456'
        }, headers=headers)
        self.assertEqual(res_change.status_code, 200)

        # Verify login with new password
        res_new_login = self.client.post('/api/auth/login', json={'email': 'sneha@safe.in', 'password': 'NewPassword@456'})
        self.assertEqual(res_new_login.status_code, 200)

        # Forgot Password OTP & Reset Flow
        res_forgot = self.client.post('/api/auth/forgot-password', json={'email': 'sneha@safe.in'})
        self.assertEqual(res_forgot.status_code, 200)
        otp = res_forgot.get_json()['debug_otp']

        # Reset Password using OTP
        res_reset = self.client.post('/api/auth/reset-password', json={
            'email': 'sneha@safe.in',
            'otp': otp,
            'new_password': 'ResetBrandNewPass@789'
        })
        self.assertEqual(res_reset.status_code, 200)

        # Verify login with reset password
        res_reset_login = self.client.post('/api/auth/login', json={'email': 'sneha@safe.in', 'password': 'ResetBrandNewPass@789'})
        self.assertEqual(res_reset_login.status_code, 200)

    def test_emergency_contacts_crud(self):
        user = User(name='Meera', email='meera@safe.in', phone='+919866677788')
        user.set_password('MeeraPass@123')
        db.session.add(user)
        db.session.commit()

        login_res = self.client.post('/api/auth/login', json={'email': 'meera@safe.in', 'password': 'MeeraPass@123'})
        token = login_res.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Add Emergency Contact
        contact_payload = {
            'name': 'Rajesh Verma (Father)',
            'phone': '+919811199999',
            'relationship': 'Father',
            'priority_order': 1,
            'notify_sms': True,
            'notify_call': True
        }
        res_add = self.client.post('/api/auth/emergency-contacts', json=contact_payload, headers=headers)
        self.assertEqual(res_add.status_code, 201)
        contact_id = res_add.get_json()['contact']['id']

        # 2. List Contacts
        res_list = self.client.get('/api/auth/emergency-contacts', headers=headers)
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.get_json()['contacts']), 1)

        # 3. Update Contact
        res_up = self.client.put(f'/api/auth/emergency-contacts/{contact_id}', json={'priority_order': 2}, headers=headers)
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()['contact']['priority_order'], 2)

        # 4. Delete Contact
        res_del = self.client.delete(f'/api/auth/emergency-contacts/{contact_id}', headers=headers)
        self.assertEqual(res_del.status_code, 200)

        res_list_after = self.client.get('/api/auth/emergency-contacts', headers=headers)
        self.assertEqual(len(res_list_after.get_json()['contacts']), 0)

    def test_guardian_linking_many_to_many_and_permissions(self):
        # 1. Create Saheli 1 (Aarohi) and Saheli 2 (Bhavna)
        s1 = User(name='Aarohi', email='aarohi@safe.in', phone='+919877711111')
        s1.set_password('AarohiPass@123')
        s2 = User(name='Bhavna', email='bhavna@safe.in', phone='+919877722222')
        s2.set_password('BhavnaPass@123')
        db.session.add_all([s1, s2])
        db.session.commit()

        # Login Aarohi
        s1_token = self.client.post('/api/auth/login', json={'email': 'aarohi@safe.in', 'password': 'AarohiPass@123'}).get_json()['access_token']
        # Login Bhavna
        s2_token = self.client.post('/api/auth/login', json={'email': 'bhavna@safe.in', 'password': 'BhavnaPass@123'}).get_json()['access_token']

        # 2. Aarohi adds Guardian (Sharmila - Mother)
        g_payload = {
            'name': 'Sharmila Devi',
            'relationship': 'Mother',
            'phone': '+919877733333',
            'email': 'sharmila@guardian.in',
            'username': 'sharmila_mom',
            'password': 'MomPassword@2026',
            'can_view_location': True,
            'can_view_camera': True,
            'emergency_override_camera': True,
            'is_primary': True
        }
        res_add_g1 = self.client.post('/api/guardians', json=g_payload, headers={'Authorization': f'Bearer {s1_token}'})
        self.assertEqual(res_add_g1.status_code, 201)
        guardian_id = res_add_g1.get_json()['guardian']['id']

        # 3. Bhavna ALSO links the SAME Guardian (Many-to-Many: One guardian monitors multiple daughters/users!)
        g_payload2 = {
            'name': 'Sharmila Devi',
            'relationship': 'Aunt',
            'phone': '+919877733333',
            'email': 'sharmila@guardian.in',
            'can_view_location': True
        }
        res_add_g2 = self.client.post('/api/guardians', json=g_payload2, headers={'Authorization': f'Bearer {s2_token}'})
        self.assertEqual(res_add_g2.status_code, 201)

        # 4. Guardian logs in independently
        res_glogin = self.client.post('/api/guardians/login', json={'username': 'sharmila_mom', 'password': 'MomPassword@2026'})
        self.assertEqual(res_glogin.status_code, 200)
        g_token = res_glogin.get_json()['access_token']
        g_headers = {'Authorization': f'Bearer {g_token}'}

        # 5. Guardian fetches monitored Saheli list -> MUST SEE BOTH Aarohi AND Bhavna!
        res_slist = self.client.get('/api/guardians/saheli-list', headers=g_headers)
        self.assertEqual(res_slist.status_code, 200)
        sahelis = res_slist.get_json()['sahelis']
        self.assertEqual(len(sahelis), 2)
        names = [s['name'] for s in sahelis]
        self.assertIn('Aarohi', names)
        self.assertIn('Bhavna', names)

        # 6. Guardian registers FCM Push Token
        res_token = self.client.post('/api/guardians/device-token', json={
            'fcm_token': 'fcm_guardian_token_xyz_98765',
            'platform': 'ANDROID'
        }, headers=g_headers)
        self.assertEqual(res_token.status_code, 200)

        # Verify token in DB
        db_token = DeviceToken.query.filter_by(fcm_token='fcm_guardian_token_xyz_98765').first()
        self.assertIsNotNone(db_token)
        self.assertEqual(db_token.guardian_id, guardian_id)

    def test_unauthorized_and_role_access_prevention(self):
        # Create Saheli & Guardian
        s = User(name='Tara', email='tara@safe.in', phone='+919899900011')
        s.set_password('TaraPass@123')
        g = Guardian(name='Ramesh', relationship='Uncle', phone='+919899900022', email='ramesh@test.in', username='ramesh_u')
        g.set_password('RameshPass@123')
        db.session.add_all([s, g])
        db.session.commit()

        s_token = self.client.post('/api/auth/login', json={'email': 'tara@safe.in', 'password': 'TaraPass@123'}).get_json()['access_token']
        g_token = self.client.post('/api/guardians/login', json={'username': 'ramesh_u', 'password': 'RameshPass@123'}).get_json()['access_token']

        # Guardian attempts to access Saheli-only endpoint (/api/auth/emergency-contacts) -> 403 Forbidden!
        res_g_denied = self.client.get('/api/auth/emergency-contacts', headers={'Authorization': f'Bearer {g_token}'})
        self.assertEqual(res_g_denied.status_code, 403)

        # Saheli attempts to access Guardian-only endpoint (/api/guardians/saheli-list) -> 403 Forbidden!
        res_s_denied = self.client.get('/api/guardians/saheli-list', headers={'Authorization': f'Bearer {s_token}'})
        self.assertEqual(res_s_denied.status_code, 403)

if __name__ == '__main__':
    unittest.main()
