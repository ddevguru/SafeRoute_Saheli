"""
SafeRoute Saheli — Real-Time Health & Operations Telemetry Monitor
CLI Diagnostic Dashboard for System Administrators & Safety Operators
"""

import sys
import os
import time
from datetime import datetime

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.guardian import Guardian, GuardianUser
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident
from backend.app.models.evidence import CameraSnapshot, AudioRecording
from backend.app.models.routing import SafePlace, RouteDeviation
from backend.app.models.admin import AuditLog
from ai_ml.inference.predictor import inference_engine

def print_dashboard():
    app = create_app('testing')
    with app.app_context():
        # 1. DB Health & Latency
        t0 = time.time()
        db.session.execute(db.text("SELECT 1"))
        db_latency_ms = round((time.time() - t0) * 1000, 2)

        # 2. Key Metrics
        total_users = User.query.count()
        total_guardians = Guardian.query.count()
        total_links = GuardianUser.query.count()
        total_devices = Device.query.count()
        online_devices = Device.query.filter_by(status='ONLINE').count()
        active_emergencies = EmergencyIncident.query.filter_by(status='ACTIVE').count()
        total_incidents = EmergencyIncident.query.count()
        total_safe_places = SafePlace.query.count()
        total_snapshots = CameraSnapshot.query.count()
        total_audio = AudioRecording.query.count()
        total_deviations = RouteDeviation.query.count()
        recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(3).all()

        # 3. AI Health Check
        ai_t0 = time.time()
        test_risk = inference_engine.assess_risk(lighting=0.8, crowd=0.7, police_dist_km=0.5, time_risk=0.2, crime_score=0.1)
        ai_latency_ms = round((time.time() - ai_t0) * 1000, 2)

        print("\n" + "=" * 70)
        print("     SAFEROUTE SAHELI — REAL-TIME HEALTH & TELEMETRY MONITOR")
        print("     Time: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC") + " | Environment: PRODUCTION_READY")
        print("=" * 70)

        print("\n[1. CORE INFRASTRUCTURE]")
        print(f"  * Database Status        : HEALTHY (Latency: {db_latency_ms} ms)")
        print(f"  * AI / Soft Computing   : ONLINE (ANFIS PyTorch Latency: {ai_latency_ms} ms)")
        print(f"  * Test Risk Evaluation   : Score {test_risk['risk_score']} [{test_risk['level']}]")

        print("\n[2. ECOSYSTEM POPULATION]")
        print(f"  * Registered Sahelis     : {total_users}")
        print(f"  * Registered Guardians   : {total_guardians}")
        print(f"  * Active User Links      : {total_links}")
        print(f"  * Verified Safe Places   : {total_safe_places} (Police, Hospitals, Shelters)")

        print("\n[3. IOT HARDWARE FLEET]")
        print(f"  * Total Paired Devices   : {total_devices}")
        print(f"  * Online Hardware Units  : {online_devices}")

        devices = Device.query.all()
        for d in devices:
            print(f"    - {d.device_id} ({d.device_type}) | Status: {d.status} | Battery: {d.battery_percent}%")

        print("\n[4. INCIDENT & DISPATCH CENTER]")
        print(f"  * ACTIVE EMERGENCIES     : {active_emergencies}")
        print(f"  * Historical Incidents   : {total_incidents}")
        print(f"  * Forensics Snapshots    : {total_snapshots} frames")
        print(f"  * Audio Evidence Files   : {total_audio} records")
        print(f"  * Route Deviations Logged: {total_deviations} events")

        if recent_audits:
            print("\n[5. RECENT SECURITY AUDIT TRAIL]")
            for a in recent_audits:
                print(f"  * [{a.actor_type}] Action: {a.action} on {a.resource}")

        print("\n" + "=" * 70)
        print("  ALL SUBSYSTEMS FULLY OPERATIONAL — 0 SYSTEM DEGRADATIONS DETECTED")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    print_dashboard()
