"""
SafeRoute Saheli — Geo-Fence Safe Zone Guard & Battery Optimizer Tests (Phase 30)
Validates circular geo-fence entry/exit, curfew violation triggers, and power-saving GPS throttling.
"""

import unittest
from datetime import datetime, timezone
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.routing import SafeZone
from backend.app.auth.jwt_handler import create_access_token
from backend.app.services.geofence_service import GeoFenceService


class GeoFenceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli User
        self.user = User(
            name="Radhika Nair",
            email="radhika@saheli.org",
            phone="+919876543221"
        )
        self.user.set_password("RadhikaPass#2026")
        db.session.add(self.user)
        db.session.commit()

        # JWT Auth
        self.token = create_access_token(identity=self.user.id, role="SAHELI")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Seed Safe Zones: Home & College
        self.home_zone = SafeZone(
            user_id=self.user.id,
            name="Home Haven",
            latitude=28.6139,
            longitude=77.2090,
            radius_meters=200.0,
            curfew_start_hour=22,  # 10 PM
            curfew_end_hour=5,     # 5 AM
            notify_guardians_on_arrival=True,
            is_active=True
        )

        self.campus_zone = SafeZone(
            user_id=self.user.id,
            name="Delhi University North Campus",
            latitude=28.6890,
            longitude=77.2110,
            radius_meters=500.0,
            curfew_start_hour=None,
            curfew_end_hour=None,
            is_active=True
        )

        db.session.add_all([self.home_zone, self.campus_zone])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_curfew_window_calculation(self):
        """Curfew evaluator correctly detects midnight-crossing windows (22:00 to 05:00)"""
        # Active hours: 22, 23, 00, 01, 02, 03, 04
        self.assertTrue(GeoFenceService.is_curfew_active(22, 5, 23))
        self.assertTrue(GeoFenceService.is_curfew_active(22, 5, 2))
        self.assertTrue(GeoFenceService.is_curfew_active(22, 5, 0))

        # Inactive hours: 05, 12, 18, 21
        self.assertFalse(GeoFenceService.is_curfew_active(22, 5, 5))
        self.assertFalse(GeoFenceService.is_curfew_active(22, 5, 14))
        self.assertFalse(GeoFenceService.is_curfew_active(22, 5, 21))

    def test_02_inside_safe_zone_power_saving(self):
        """User inside Home safe zone triggers battery-saving GPS throttling (120s interval)"""
        eval_dt = datetime(2026, 9, 27, 14, 30, tzinfo=timezone.utc)
        # Position 50m from home (within 200m radius)
        res = GeoFenceService.evaluate_position(
            user_id=self.user.id,
            latitude=28.6141,
            longitude=77.2091,
            battery_percent=85,
            current_dt=eval_dt
        )

        self.assertTrue(res['is_inside_safe_zone'])
        self.assertEqual(res['status'], 'INSIDE_SAFE_ZONE')
        self.assertIsNotNone(res['active_safe_zone'])
        self.assertEqual(res['active_safe_zone']['name'], 'Home Haven')
        self.assertEqual(res['recommended_gps_interval_ms'], 120000)
        self.assertEqual(res['battery_power_mode'], 'SAFE_HAVEN_POWER_SAVING')
        self.assertFalse(res['curfew_breached'])

    def test_03_inside_safe_zone_critical_battery_ultra_saver(self):
        """Critical battery (<=15%) inside safe zone throttles GPS to 5-minute ultra power saver"""
        eval_dt = datetime(2026, 9, 27, 16, 0, tzinfo=timezone.utc)
        res = GeoFenceService.evaluate_position(
            user_id=self.user.id,
            latitude=28.6139,
            longitude=77.2090,
            battery_percent=12,
            current_dt=eval_dt
        )
        self.assertTrue(res['is_inside_safe_zone'])
        self.assertEqual(res['recommended_gps_interval_ms'], 300000)
        self.assertEqual(res['battery_power_mode'], 'ULTRA_POWER_SAVING')

    def test_04_outside_safe_zone_normal_daylight(self):
        """User outside all safe zones in afternoon has standard transit tracking (25s) without curfew alerts"""
        eval_dt = datetime(2026, 9, 27, 15, 0, tzinfo=timezone.utc)
        # Location in Connaught Place, 3km away from home
        res = GeoFenceService.evaluate_position(
            user_id=self.user.id,
            latitude=28.6310,
            longitude=77.2190,
            battery_percent=70,
            current_dt=eval_dt
        )
        self.assertFalse(res['is_inside_safe_zone'])
        self.assertEqual(res['status'], 'OUTSIDE_SAFE_ZONE')
        self.assertFalse(res['curfew_breached'])
        self.assertEqual(res['recommended_gps_interval_ms'], 25000)
        self.assertEqual(res['battery_power_mode'], 'STANDARD_TRANSIT')

    def test_05_curfew_breach_late_night(self):
        """User outside safe zone during 23:30 night curfew triggers curfew breach and high alert 10s GPS stream"""
        eval_dt = datetime(2026, 9, 27, 23, 30, tzinfo=timezone.utc)
        res = GeoFenceService.evaluate_position(
            user_id=self.user.id,
            latitude=28.6350,
            longitude=77.2250,
            battery_percent=60,
            current_dt=eval_dt
        )
        self.assertFalse(res['is_inside_safe_zone'])
        self.assertTrue(res['curfew_breached'])
        self.assertIsNotNone(res['curfew_details'])
        self.assertEqual(res['curfew_details']['zone_name'], 'Home Haven')
        self.assertEqual(res['recommended_gps_interval_ms'], 10000)
        self.assertEqual(res['battery_power_mode'], 'HIGH_ALERT_TRACKING')

    def test_06_api_create_and_list_safe_zones(self):
        """POST and GET /api/geofence/safe-zones endpoints work properly with JWT authentication"""
        payload = {
            "name": "Co-Working Hub",
            "latitude": 28.6250,
            "longitude": 77.2180,
            "radius_meters": 180.0,
            "curfew_start_hour": 21,
            "curfew_end_hour": 6,
            "notify_guardians_on_arrival": True
        }
        create_resp = self.client.post('/api/geofence/safe-zones', json=payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 201)
        data = create_resp.get_json()
        self.assertTrue(data['success'])
        zone_id = data['safe_zone']['id']

        # List safe zones
        list_resp = self.client.get('/api/geofence/safe-zones', headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        list_data = list_resp.get_json()
        self.assertTrue(list_data['success'])
        self.assertEqual(list_data['count'], 3)  # 2 in setUp + 1 created

        # Delete safe zone
        del_resp = self.client.delete(f'/api/geofence/safe-zones/{zone_id}', headers=self.headers)
        self.assertEqual(del_resp.status_code, 200)

    def test_07_api_evaluate_geofence_position(self):
        """POST /api/geofence/evaluate returns real-time position assessment and power recommendations"""
        payload = {
            "latitude": 28.6140,
            "longitude": 77.2090,
            "battery_percent": 90
        }
        resp = self.client.post('/api/geofence/evaluate', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('evaluation', data)
        self.assertTrue(data['evaluation']['is_inside_safe_zone'])
        self.assertEqual(data['evaluation']['recommended_gps_interval_ms'], 120000)


if __name__ == '__main__':
    unittest.main()
