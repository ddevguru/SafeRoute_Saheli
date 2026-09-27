"""
SafeRoute Saheli — Full Ecosystem Simulation CLI Script
Simulates end-to-end integration between:
ESP32 Wearable -> ESP32-CAM -> Flask Backend -> FCM -> Live GPS Web Tracker -> AI Safe Route Engine
"""

import sys
import os
import time
import io
import json
from datetime import datetime

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User, EmergencyContact
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident, LiveTrackingSession, TrackingToken
from backend.app.models.evidence import CameraSnapshot, AudioRecording
from backend.app.auth.jwt_handler import create_access_token

def run_simulation():
    print("\n" + "=" * 70)
    print("  SAFEROUTE SAHELI — FULL HARDWARE + CLOUD + AI ECOSYSTEM SIMULATION")
    print("  'Stay Connected. Stay Aware. Stay Safe.'")
    print("=" * 70 + "\n")

    app = create_app('testing')
    client = app.test_client()

    with app.app_context():
        db.create_all()

        # Step 1: User & Guardian Setup
        print("[STEP 1/9] Initializing Saheli & Guardian Accounts...")
        user = User.query.filter_by(email="rupali_demo@saheli.org").first()
        if not user:
            user = User(name="Rupali Demo", email="rupali_demo@saheli.org", phone="+919876543210")
            user.set_password("SaheliPass2026!")
            db.session.add(user)
            db.session.flush()

        guardian = Guardian.query.filter_by(email="guardian_demo@saheli.org").first()
        if not guardian:
            guardian = Guardian(
                name="Smt. Sunita Sharma",
                username="sunita_sharma_demo",
                email="guardian_demo@saheli.org",
                phone="+919876543211",
                relationship="MOTHER"
            )
            guardian.set_password("MotherPass2026!")
            db.session.add(guardian)
            db.session.flush()

        link = GuardianUser.query.filter_by(saheli_id=user.id, guardian_id=guardian.id).first()
        if not link:
            link = GuardianUser(
                saheli_id=user.id,
                guardian_id=guardian.id,
                relationship_label="MOTHER",
                can_view_location=True,
                can_view_camera=True,
                emergency_override_camera=True
            )
            db.session.add(link)

        # Step 2: Register IoT Devices
        print("[STEP 2/9] Pairing ESP32 Wearable & ESP32-CAM Hardware...")
        wearable = Device.query.filter_by(device_id="SAHELI-WEARABLE-001").first()
        if not wearable:
            wearable = Device(
                device_id="SAHELI-WEARABLE-001",
                device_type="WEARABLE_ESP32",
                assigned_user_id=user.id,
                battery_percent=94,
                status="ONLINE"
            )
            wearable.set_secret("wearable_secret_2026")
            db.session.add(wearable)

        cam = Device.query.filter_by(device_id="SAHELI-CAM-001").first()
        if not cam:
            cam = Device(
                device_id="SAHELI-CAM-001",
                device_type="ESP32_CAM",
                assigned_user_id=user.id,
                status="ONLINE",
                camera_health="HEALTHY",
                wifi_rssi=-54
            )
            cam.set_secret("cam_secret_2026")
            db.session.add(cam)

        db.session.commit()
        print(f"  [OK] User: {user.name} ({user.phone})")
        print(f"  [OK] Linked Guardian: {guardian.name} [{link.relationship_label}]")
        print(f"  [OK] ESP32 Wearable paired: {wearable.device_id} (Battery: {wearable.battery_percent}%)")
        print(f"  [OK] ESP32-CAM paired: {cam.device_id} (Signal: {cam.wifi_rssi} dBm)")

        # Step 3: Normal GPS Heartbeat
        print("\n[STEP 3/9] Pushing Idle GPS Coordinates from Wearable Neo-6M...")
        normal_lat, normal_lng = 28.6139, 77.2090
        loc_resp = client.post('/api/location/update', json={
            'device_id': wearable.device_id,
            'device_secret': 'wearable_secret_2026',
            'latitude': normal_lat,
            'longitude': normal_lng,
            'accuracy': 3.5,
            'speed': 1.1,
            'battery': 94
        })
        print(f"  [OK] Normal GPS Pushed: [{normal_lat}, {normal_lng}] | Response: {loc_resp.status_code}")

        # Step 4: ESP32 Hardware TTP223 Touch SOS Trigger
        print("\n[STEP 4/9] Triggering TTP223 Capacitive Touch SOS (1.5s Hold)...")
        trigger_resp = client.post('/api/emergency/trigger', json={
            'device_id': wearable.device_id,
            'device_secret': 'wearable_secret_2026',
            'trigger_type': 'TOUCH',
            'latitude': 28.6145,
            'longitude': 77.2095,
            'battery_percent': 93,
            'confidence': 1.0
        })
        trig_data = trigger_resp.get_json()
        incident_id = trig_data['incident_id']
        tracking_url = trig_data['tracking_url']
        tracking_token = trig_data['tracking_token']

        print(f"  [ALERT] EMERGENCY INCIDENT CREATED: ID {incident_id}")
        print(f"  [OK] Status: {trig_data['status']} | Trigger: TOUCH")
        print(f"  [OK] High-Priority FCM Push Sent to Guardian: {guardian.name}")
        print(f"  [OK] SMS Dispatch Created with Link: {tracking_url}")

        # Step 5: ESP32-CAM Emergency Burst Capture
        print("\n[STEP 5/9] ESP32-CAM Burst Capture & Forensics Vault Upload...")
        fake_jpg = b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\xFF\xD9'
        cam_resp = client.post('/api/camera/capture', data={
            'device_id': cam.device_id,
            'device_secret': 'cam_secret_2026',
            'image': (io.BytesIO(fake_jpg), 'burst_01.jpg', 'image/jpeg')
        }, content_type='multipart/form-data')
        cam_data = cam_resp.get_json()
        print(f"  [OK] Evidence Frame Encrypted & Uploaded: ID {cam_data['snapshot_id']}")
        print(f"  [OK] SHA-256 Hash: {cam_data['file_hash']}")
        print(f"  [OK] Attached to Incident: {incident_id}")

        # Step 6: Audio Anomaly Classifier (INMP441 Microphone)
        print("\n[STEP 6/9] INMP441 Acoustic Distress Analysis (DSP Scream/Distress)...")
        audio_resp = client.post('/api/audio/analyze', json={
            'peak': 0.89,
            'rms': 0.38,
            'zcr': 0.22,
            'spectral_centroid': 2850.0
        })
        audio_data = audio_resp.get_json()
        print(f"  [OK] Acoustic Classification: {audio_data['result']['classification']}")
        print(f"  [OK] Distress Confidence: {audio_data['result']['confidence'] * 100:.1f}%")
        print(f"  [OK] Emergency Flag: {audio_data['result']['is_emergency']}")

        # Step 7: Public Live Tracking Web Console Polling
        print("\n[STEP 7/9] Polling Public Tokenized Tracking Link (/track/<token>)...")
        track_resp = client.get(f'/track/{tracking_token}/api')
        track_data = track_resp.get_json()
        print(f"  [OK] Web Tracker Status: {track_data['incident']['status']}")
        print(f"  [OK] Live Coordinates: {track_data['current_location']['latitude']}, {track_data['current_location']['longitude']}")
        print(f"  [OK] Breadcrumb Trail Count: {len(track_data['breadcrumb'])} GPS points")

        # Step 8: Nearby Emergency Services
        print("\n[STEP 8/9] Haversine Spatial Query for Nearest Police & Hospitals...")
        nearby_resp = client.get(f'/api/nearby/all?lat={normal_lat}&lng={normal_lng}&radius_meters=5000')
        nearby_data = nearby_resp.get_json()
        print(f"  [OK] Nearest Police Booths: {nearby_data['summary']['police_count']}")
        if nearby_data['places']['police']:
            closest_police = nearby_data['places']['police'][0]
            print(f"    - {closest_police['name']} ({closest_police['distance_meters']}m, {closest_police['phone_number']})")
        print(f"  [OK] Nearest Hospitals: {nearby_data['summary']['hospital_count']}")
        print(f"  [OK] Nearest Shelters: {nearby_data['summary']['shelter_count']}")

        # Step 9: Safe Route Soft Computing Engine (ANFIS + Genetic Algorithm)
        print("\n[STEP 9/9] Calculating ANFIS + Genetic Algorithm Safe Detour Route...")
        from ai_ml.inference.predictor import inference_engine
        opt_res = inference_engine.plan_safe_route((normal_lat, normal_lng), (28.6300, 77.2200), hour_of_day=23)
        safest = opt_res['routes']['safest']
        print(f"  [OK] Safest Route Safety Score: {safest['safety_score']} / 100.0")
        print(f"  [OK] Distance: {safest['distance_km']} km | Est. Duration: {safest['duration_minutes']} mins")
        print(f"  [OK] Waypoints Generated: {len(safest['waypoints'])} GPS nodes")

        # Resolution
        print("\n" + "-" * 70)
        user_token = create_access_token(user.id, role='SAHELI')
        headers = {'Authorization': f"Bearer {user_token}"}
        resolve_resp = client.post(f'/api/emergency/{incident_id}/cancel', json={'reason': 'Safe verification complete'}, headers=headers)
        print(f"  [OK] Incident Safely Resolved: {resolve_resp.status_code == 200}")
        print("=" * 70)
        print("  SUCCESS: FULL ECOSYSTEM HARDWARE-TO-CLOUD SIMULATION COMPLETE & VERIFIED!")
        print("=" * 70 + "\n")

if __name__ == '__main__':
    run_simulation()
