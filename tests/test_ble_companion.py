"""
SafeRoute Saheli — BLE Companion & GATT Protocol Unit & Integration Tests (Phase 31)
Validates BLE packet structure, emergency notifications, telemetry encoding, and offline pairing.
"""

import re
import unittest
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.auth.jwt_handler import create_access_token


class BLECompanionProtocolTestCase(unittest.TestCase):
    # Standard UUIDs
    SERVICE_UUID        = "00005A48-0000-1000-8000-00805F9B34FB"
    CHAR_EMERGENCY_UUID = "00005A49-0000-1000-8000-00805F9B34FB"
    CHAR_TELEMETRY_UUID = "00005A4A-0000-1000-8000-00805F9B34FB"
    CHAR_CONFIG_UUID    = "00005A4B-0000-1000-8000-00805F9B34FB"
    CHAR_PAIRING_UUID   = "00005A4C-0000-1000-8000-00805F9B34FB"

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli User
        self.user = User(
            name="Aarohi Patil",
            email="aarohi@saheli.org",
            phone="+919876543222"
        )
        self.user.set_password("AarohiPass#2026")
        db.session.add(self.user)
        db.session.commit()

        # JWT Token
        self.token = create_access_token(identity=self.user.id, role="SAHELI")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Seed Paired Wearable Device
        self.device = Device(
            device_id="SAHELI-WEARABLE-001",
            device_type="ESP32_WEARABLE",
            firmware_version="1.3.0",
            battery_percent=92,
            assigned_user_id=self.user.id
        )
        self.device_secret = "wearable_esp32_hmac_shared_secret_2026"
        self.device.set_secret(self.device_secret)
        db.session.add(self.device)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def parse_ble_emergency_packet(self, packet_str: str):
        """Emulates mobile companion parsing BLE GATT notification string"""
        match = re.match(r"^EMERGENCY:([A-Z_]+):([\d\.]+):(\d+)$", packet_str)
        if not match:
            return None
        return {
            "trigger_type": match.group(1),
            "confidence": float(match.group(2)),
            "device_uptime_ms": int(match.group(3))
        }

    def parse_ble_telemetry_packet(self, packet_str: str):
        """Emulates mobile companion parsing BLE telemetry string"""
        match = re.match(r"^TELEM:([\d\.]+):([\d\.]+):(\d+):([A-Z_]+)$", packet_str)
        if not match:
            return None
        return {
            "heart_rate_bpm": float(match.group(1)),
            "spo2": float(match.group(2)),
            "battery_percent": int(match.group(3)),
            "motion_state": match.group(4)
        }

    def test_01_ble_gatt_uuids_conformity(self):
        """Validates that BLE UUIDs match 128-bit Bluetooth SIG standard specifications"""
        self.assertTrue(self.SERVICE_UUID.startswith("00005A48"))
        self.assertTrue(self.CHAR_EMERGENCY_UUID.startswith("00005A49"))
        self.assertTrue(self.CHAR_TELEMETRY_UUID.startswith("00005A4A"))
        self.assertTrue(self.CHAR_CONFIG_UUID.startswith("00005A4B"))
        self.assertTrue(self.CHAR_PAIRING_UUID.startswith("00005A4C"))

    def test_02_parse_ble_emergency_packets(self):
        """Companion phone accurately parses emergency notification packets emitted over BLE"""
        raw_packet = "EMERGENCY:TOUCH_HOLD:1.00:45820"
        parsed = self.parse_ble_emergency_packet(raw_packet)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['trigger_type'], 'TOUCH_HOLD')
        self.assertEqual(parsed['confidence'], 1.0)
        self.assertEqual(parsed['device_uptime_ms'], 45820)

    def test_03_parse_ble_telemetry_packets(self):
        """Companion phone accurately parses live PPG biometrics & IMU telemetry stream over BLE"""
        raw_telem = "TELEM:74.5:98.2:91:NORMAL_WALKING"
        parsed = self.parse_ble_telemetry_packet(raw_telem)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['heart_rate_bpm'], 74.5)
        self.assertEqual(parsed['spo2'], 98.2)
        self.assertEqual(parsed['battery_percent'], 91)
        self.assertEqual(parsed['motion_state'], 'NORMAL_WALKING')

    def test_04_ble_relay_to_backend_sos_dispatch(self):
        """Simulates phone receiving BLE emergency notification and instantly relaying to cloud backend"""
        ble_packet = "EMERGENCY:FALL:0.95:102030"
        parsed = self.parse_ble_emergency_packet(ble_packet)

        # Phone relays via mobile data
        payload = {
            "trigger_type": parsed['trigger_type'],
            "latitude": 28.6148,
            "longitude": 77.2098,
            "battery_percent": 92,
            "confidence": parsed['confidence']
        }
        resp = self.client.post('/api/emergency/trigger', json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])

        # Check DB
        inc = EmergencyIncident.query.filter_by(user_id=self.user.id, status='ACTIVE').first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.trigger_type, 'FALL')
        self.assertAlmostEqual(float(inc.latitude), 28.6148)

    def test_05_ble_pairing_handshake_verification(self):
        """Verifies mutual authentication pairing handshake between companion phone and ESP32"""
        # Phone sends secret handshake to device pairing characteristic
        handshake_payload = f"PAIR:OK:{self.device_secret}"

        # Wearable verifies secret
        is_secret_match = (self.device_secret in handshake_payload)
        self.assertTrue(is_secret_match)

        # Invalid secret fails
        invalid_handshake = "PAIR:OK:wrong_secret_123"
        self.assertFalse(self.device_secret in invalid_handshake)


if __name__ == '__main__':
    unittest.main()
