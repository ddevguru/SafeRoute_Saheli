"""
SafeRoute Saheli — Cryptographic Evidence Chain-of-Custody & Merkle Integrity Tests (Phase 29)
Validates digital forensics ledger, deterministic Merkle root generation, and tamper detection.
"""

import unittest
from datetime import datetime, timezone
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.evidence import CameraSnapshot, AudioRecording
from backend.app.models.location import LocationHistory
from backend.app.auth.jwt_handler import create_access_token
from backend.app.services.evidence_chain_service import EvidenceChainService


class EvidenceChainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Saheli User
        self.user = User(
            name="Tanvi Sen",
            email="tanvi@saheli.org",
            phone="+919876543220"
        )
        self.user.set_password("TanviPass#2026")
        db.session.add(self.user)
        db.session.commit()

        # JWT Auth
        self.token = create_access_token(identity=self.user.id, role="SAHELI")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Seed Paired Devices
        self.cam_device = Device(
            device_id="SAHELI-CAM-001",
            device_type="ESP32_CAM",
            assigned_user_id=self.user.id
        )
        self.cam_device.set_secret("cam_secret_2026")

        self.wearable_device = Device(
            device_id="SAHELI-WEARABLE-001",
            device_type="ESP32_WEARABLE",
            assigned_user_id=self.user.id
        )
        self.wearable_device.set_secret("wearable_secret_2026")

        db.session.add_all([self.cam_device, self.wearable_device])
        db.session.commit()

        # Seed Emergency Incident
        self.incident = EmergencyIncident(
            user_id=self.user.id,
            device_id=self.wearable_device.device_id,
            trigger_type="TOUCH",
            status="ACTIVE",
            latitude=28.6139,
            longitude=77.2090,
            battery_percent=89,
            confidence=1.0,
            started_at=datetime.now(timezone.utc)
        )
        db.session.add(self.incident)
        db.session.commit()

        # Seed Evidence Items
        self.snap1 = CameraSnapshot(
            incident_id=self.incident.id,
            device_id=self.cam_device.id,
            user_id=self.user.id,
            image_url="http://uploads/camera/snap1.jpg",
            file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            file_size_bytes=142000,
            latitude=28.6139,
            longitude=77.2090,
            captured_at=datetime.now(timezone.utc)
        )
        self.snap2 = CameraSnapshot(
            incident_id=self.incident.id,
            device_id=self.cam_device.id,
            user_id=self.user.id,
            image_url="http://uploads/camera/snap2.jpg",
            file_hash="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
            file_size_bytes=158000,
            latitude=28.6140,
            longitude=77.2092,
            captured_at=datetime.now(timezone.utc)
        )
        self.audio1 = AudioRecording(
            incident_id=self.incident.id,
            device_id=self.wearable_device.id,
            user_id=self.user.id,
            storage_url="http://uploads/audio/clip1.wav",
            file_hash="4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865",
            file_size_bytes=64000,
            duration_seconds=5,
            trigger_type="SCREAM_ANOMALY",
            recorded_at=datetime.now(timezone.utc)
        )
        self.loc1 = LocationHistory(
            user_id=self.user.id,
            latitude=28.6139,
            longitude=77.2090,
            accuracy=4.2,
            recorded_at=datetime.now(timezone.utc)
        )
        self.loc2 = LocationHistory(
            user_id=self.user.id,
            latitude=28.6142,
            longitude=77.2094,
            accuracy=3.8,
            recorded_at=datetime.now(timezone.utc)
        )

        db.session.add_all([self.snap1, self.snap2, self.audio1, self.loc1, self.loc2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_merkle_tree_deterministic_integrity(self):
        """Identical evidence leaves produce identical Merkle root, altering one bit completely alters root"""
        leaves = [
            "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
            "fcba040ac3f9a44c0483564ec79be631f92e0074191e6398d1eac45d8a212042",
            "ea093313d83228b5e2017da49aad8519d4796321cd4000d14ca41f57249c5762"
        ]

        root1 = EvidenceChainService.compute_merkle_root(leaves)
        root2 = EvidenceChainService.compute_merkle_root(leaves)
        self.assertEqual(root1, root2)
        self.assertEqual(len(root1), 64)

        # Tampered leaf
        tampered_leaves = list(leaves)
        tampered_leaves[1] = "fcba040ac3f9a44c0483564ec79be631f92e0074191e6398d1eac45d8a212043"
        tampered_root = EvidenceChainService.compute_merkle_root(tampered_leaves)
        self.assertNotEqual(root1, tampered_root)

    def test_02_generate_chain_of_custody_manifest(self):
        """Generates certified manifest containing all evidence artifacts with cryptographic signature"""
        manifest = EvidenceChainService.generate_chain_of_custody(self.incident.id)

        self.assertEqual(manifest['incident_id'], self.incident.id)
        self.assertEqual(manifest['status'], 'CERTIFIED_VALID')
        self.assertEqual(manifest['evidence_summary']['camera_snapshots_count'], 2)
        self.assertEqual(manifest['evidence_summary']['audio_recordings_count'], 1)
        self.assertEqual(manifest['evidence_summary']['gps_points_count'], 2)
        self.assertEqual(manifest['evidence_summary']['total_blocks'], 6)  # 1 genesis + 2 snaps + 1 audio + 2 locs
        self.assertEqual(len(manifest['merkle_root']), 64)
        self.assertEqual(len(manifest['cryptographic_signature']), 64)

    def test_03_verify_unaltered_manifest_succeeds(self):
        """Unaltered manifest successfully passes cryptographic integrity verification"""
        manifest = EvidenceChainService.generate_chain_of_custody(self.incident.id)
        result = EvidenceChainService.verify_manifest(manifest)

        self.assertTrue(result['is_valid'])
        self.assertTrue(result['merkle_root_match'])
        self.assertTrue(result['signature_match'])
        self.assertEqual(result['status'], 'TAMPER_FREE_VERIFIED')
        self.assertEqual(result['total_blocks_verified'], 6)

    def test_04_tampered_manifest_fails_verification(self):
        """Modifying an evidence artifact hash causes verification to fail with INTEGRITY_COMPROMISED"""
        manifest = EvidenceChainService.generate_chain_of_custody(self.incident.id)

        # Maliciously tamper with snapshot block hash
        manifest['chain_blocks'][1]['sha256_hash'] = "0000000000000000000000000000000000000000000000000000000000000000"

        result = EvidenceChainService.verify_manifest(manifest)
        self.assertFalse(result['is_valid'])
        self.assertFalse(result['merkle_root_match'])
        self.assertEqual(result['status'], 'INTEGRITY_COMPROMISED')

    def test_05_tampered_signature_fails_verification(self):
        """Altered digital signature fails verification"""
        manifest = EvidenceChainService.generate_chain_of_custody(self.incident.id)
        manifest['cryptographic_signature'] = "deadbeef" * 8

        result = EvidenceChainService.verify_manifest(manifest)
        self.assertFalse(result['is_valid'])
        self.assertFalse(result['signature_match'])
        self.assertEqual(result['status'], 'INTEGRITY_COMPROMISED')

    def test_06_api_get_chain_of_custody_endpoint(self):
        """GET /api/evidence/<incident_id>/chain-of-custody returns 200 with certified manifest"""
        resp = self.client.get(f'/api/evidence/{self.incident.id}/chain-of-custody', headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('manifest', data)
        self.assertEqual(data['manifest']['incident_id'], self.incident.id)

    def test_07_api_verify_manifest_endpoint(self):
        """POST /api/evidence/verify-manifest returns 200 for valid manifest and 400 for tampered manifest"""
        manifest = EvidenceChainService.generate_chain_of_custody(self.incident.id)

        # 1. Valid Manifest
        resp = self.client.post('/api/evidence/verify-manifest', json={'manifest': manifest})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['verification']['is_valid'])

        # 2. Tampered Manifest
        manifest['chain_blocks'][0]['sha256_hash'] = "ff" * 32
        resp2 = self.client.post('/api/evidence/verify-manifest', json={'manifest': manifest})
        self.assertEqual(resp2.status_code, 400)
        data2 = resp2.get_json()
        self.assertFalse(data2['verification']['is_valid'])


if __name__ == '__main__':
    unittest.main()
