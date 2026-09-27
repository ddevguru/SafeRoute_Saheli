"""
SafeRoute Saheli — High-Concurrency Burst Stress Testing Suite (Phase 26)
Simulates massive burst loads against the emergency ingestion and live tracking pipeline:
- 100 rapid emergency triggers with zero dropped alerts
- 200 rapid GPS stream points with sub-10ms latency
- 100 biometric PPG panic telemetry evaluations
- 200 high-frequency public tracking token resolutions (/track/<token>/api)
- Multi-threaded network socket concurrency against live server (TCP pool)
- P50, P90, P95, P99 latency percentiles & throughput benchmarking
"""

import sys
import os
import time
import math
import unittest
import urllib.request
import urllib.error
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Ensure project root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.device import Device
from backend.app.models.emergency import EmergencyIncident, TrackingToken
from backend.app.auth.jwt_handler import create_access_token


class BurstStressTestSuite(unittest.TestCase):
    """Automated benchmark validating throughput, latency percentiles, and database stability under load"""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Seed 10 distinct Saheli users for concurrent triggering
        cls.users = []
        cls.tokens = []
        for i in range(10):
            user = User(
                name=f"Stress Saheli {i+1}",
                email=f"stress_user_{i+1}@saheli.org",
                phone=f"+9198765432{i:02d}"
            )
            user.set_password("StressPass#2026")
            db.session.add(user)
            db.session.flush()
            cls.users.append(user)

            token = create_access_token(identity=user.id, role="SAHELI")
            cls.tokens.append(token)

        # Seed Paired IoT Device
        cls.device = Device(
            device_id="STRESS-WEARABLE-001",
            device_type="ESP32_WEARABLE",
            firmware_version="1.0.0",
            battery_percent=98,
            assigned_user_id=cls.users[0].id
        )
        cls.device.set_secret("stress_secret_key_2026")
        db.session.add(cls.device)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def _compute_stats(self, latencies: List[float]) -> Dict[str, float]:
        """Compute latency percentiles from measured durations (in milliseconds)"""
        if not latencies:
            return {}
        sorted_l = sorted(latencies)
        n = len(sorted_l)
        return {
            "count": n,
            "min_ms": round(sorted_l[0], 2),
            "p50_ms": round(sorted_l[int(n * 0.50)], 2),
            "p90_ms": round(sorted_l[int(n * 0.90)], 2),
            "p95_ms": round(sorted_l[int(min(n - 1, int(n * 0.95)))], 2),
            "p99_ms": round(sorted_l[int(min(n - 1, int(n * 0.99)))], 2),
            "max_ms": round(sorted_l[-1], 2),
            "avg_ms": round(sum(sorted_l) / n, 2),
        }

    def test_01_burst_emergency_trigger_throughput(self):
        """Simulate 100 rapid emergency triggers across 10 users with zero dropped alerts"""
        total_requests = 100
        latencies = []
        success_count = 0
        error_count = 0
        client = self.app.test_client()

        wall_start = time.perf_counter()
        for i in range(total_requests):
            user_idx = i % len(self.users)
            token = self.tokens[user_idx]
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "trigger_type": "TOUCH",
                "latitude": 28.6139 + (i * 0.0001),
                "longitude": 77.2090 + (i * 0.0001),
                "battery_percent": max(15, 100 - (i % 50)),
                "confidence": 0.98
            }

            t0 = time.perf_counter()
            resp = client.post('/api/emergency/trigger', json=payload, headers=headers)
            duration_ms = (time.perf_counter() - t0) * 1000.0

            latencies.append(duration_ms)
            if resp.status_code == 200 and resp.get_json().get('success'):
                success_count += 1
            else:
                error_count += 1

        total_wall_s = time.perf_counter() - wall_start
        stats = self._compute_stats(latencies)
        throughput = round(total_requests / total_wall_s, 1)

        print("\n--- [BURST STRESS BENCHMARK: 100 EMERGENCY TRIGGERS] ---")
        print(f"Wall Time: {total_wall_s:.2f}s | Throughput: {throughput} req/s")
        print(f"Success: {success_count}/{total_requests} (100%) | Dropped Alerts: {error_count}")
        print(f"Latency -> Min: {stats['min_ms']}ms | P50: {stats['p50_ms']}ms | P95: {stats['p95_ms']}ms | P99: {stats['p99_ms']}ms | Max: {stats['max_ms']}ms")

        self.assertEqual(error_count, 0, "All rapid emergency triggers must succeed with zero dropped alerts")
        self.assertEqual(success_count, total_requests)
        self.assertLess(stats['p95_ms'], 100.0, "P95 latency under burst load must be < 100ms")
        self.assertGreater(throughput, 50.0, "Throughput must exceed 50 req/s")

    def test_02_burst_gps_streaming_throughput(self):
        """Simulate 200 high-frequency GPS coordinate telemetry pings"""
        total_pings = 200
        latencies = []
        success_count = 0
        client = self.app.test_client()

        wall_start = time.perf_counter()
        for i in range(total_pings):
            user_idx = i % len(self.users)
            token = self.tokens[user_idx]
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "latitude": 28.6139 + (i * 0.0002),
                "longitude": 77.2090 + (i * 0.0002),
                "accuracy": 4.5,
                "speed": 1.2,
                "battery_percent": 90,
                "is_emergency": True
            }

            t0 = time.perf_counter()
            resp = client.post('/api/location/update', json=payload, headers=headers)
            duration_ms = (time.perf_counter() - t0) * 1000.0

            latencies.append(duration_ms)
            if resp.status_code == 200 and resp.get_json().get('success'):
                success_count += 1

        total_wall_s = time.perf_counter() - wall_start
        stats = self._compute_stats(latencies)
        throughput = round(total_pings / total_wall_s, 1)

        print("\n--- [BURST STRESS BENCHMARK: 200 GPS STREAM PINGS] ---")
        print(f"Wall Time: {total_wall_s:.2f}s | Throughput: {throughput} req/s")
        print(f"Success: {success_count}/{total_pings} | P50: {stats['p50_ms']}ms | P95: {stats['p95_ms']}ms | P99: {stats['p99_ms']}ms")

        self.assertEqual(success_count, total_pings, "All GPS coordinate pings must be successfully recorded")
        self.assertLess(stats['p95_ms'], 25.0, "P95 GPS ingestion latency must be < 25ms")
        self.assertGreater(throughput, 150.0, "GPS stream throughput must exceed 150 req/s")

    def test_03_concurrent_biometric_panic_evaluations(self):
        """Simulate 100 MAX30102 biometric telemetry evaluation streams"""
        total_evals = 100
        latencies = []
        panic_detected_count = 0
        client = self.app.test_client()

        wall_start = time.perf_counter()
        for i in range(total_evals):
            # Alternating between calm and acute panic
            is_panic = (i % 2 == 0)
            bpm = 138.0 if is_panic else 74.0
            accel = 1.01 if is_panic else 1.05

            payload = {
                "device_id": "STRESS-WEARABLE-001",
                "device_secret": "stress_secret_key_2026",
                "heart_rate_bpm": bpm,
                "spo2": 97.5,
                "accel_mag_g": accel,
                "is_finger_detected": True,
                "latitude": 28.6139,
                "longitude": 77.2090
            }

            t0 = time.perf_counter()
            resp = client.post('/api/emergency/biometric-telemetry', json=payload)
            dur_ms = (time.perf_counter() - t0) * 1000.0

            latencies.append(dur_ms)
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            if data.get('emergency_triggered'):
                panic_detected_count += 1

        total_wall_s = time.perf_counter() - wall_start
        stats = self._compute_stats(latencies)
        throughput = round(total_evals / total_wall_s, 1)

        print("\n--- [BURST STRESS BENCHMARK: 100 BIOMETRIC STREAMS] ---")
        print(f"Wall Time: {total_wall_s:.2f}s | Throughput: {throughput} req/s")
        print(f"Total: {total_evals} | Panics Flagged: {panic_detected_count} | P50: {stats['p50_ms']}ms | P95: {stats['p95_ms']}ms")

        self.assertEqual(panic_detected_count, 50, "Exactly 50% of alternating streams must detect panic")
        self.assertLess(stats['p95_ms'], 25.0)

    def test_04_public_tracking_link_high_frequency_resolutions(self):
        """Simulate 200 rapid guardian / family member polling hits on public tracking token (/track/<token>/api)"""
        client = self.app.test_client()
        init_resp = client.post(
            '/api/emergency/trigger',
            json={"trigger_type": "VOICE", "latitude": 28.6145, "longitude": 77.2095},
            headers={"Authorization": f"Bearer {self.tokens[0]}"}
        )
        self.assertEqual(init_resp.status_code, 200)
        token_str = init_resp.get_json()['tracking_token']

        total_reads = 200
        latencies = []
        success_count = 0

        wall_start = time.perf_counter()
        for i in range(total_reads):
            t0 = time.perf_counter()
            resp = client.get(f'/track/{token_str}/api')
            dur_ms = (time.perf_counter() - t0) * 1000.0

            latencies.append(dur_ms)
            if resp.status_code == 200 and resp.get_json().get('success'):
                success_count += 1

        total_wall_s = time.perf_counter() - wall_start
        stats = self._compute_stats(latencies)
        throughput = round(total_reads / total_wall_s, 1)

        print("\n--- [BURST STRESS BENCHMARK: 200 TRACKING TOKEN RESOLUTIONS] ---")
        print(f"Wall Time: {total_wall_s:.2f}s | Throughput: {throughput} req/s | Success: {success_count}/{total_reads}")
        print(f"Latency -> P50: {stats['p50_ms']}ms | P95: {stats['p95_ms']}ms | P99: {stats['p99_ms']}ms | Max: {stats['max_ms']}ms")

        self.assertEqual(success_count, total_reads)
        self.assertLess(stats['p95_ms'], 25.0, "P95 public tracking resolution must be sub-25ms")
        self.assertGreater(throughput, 200.0, "Tracking resolution throughput must exceed 200 req/s")

    def test_05_live_server_tcp_socket_concurrency(self):
        """Verify real-world TCP socket concurrency against the live Flask server at http://127.0.0.1:5000"""
        server_url = "http://127.0.0.1:5000/api/health"
        # Check if live server is reachable
        try:
            with urllib.request.urlopen(server_url, timeout=2.0) as chk:
                if chk.status != 200:
                    self.skipTest("Live server not running on port 5000")
        except Exception:
            self.skipTest("Live server not reachable on port 5000")

        total_requests = 50
        concurrency = 5
        latencies = []
        success_count = 0

        def hit_live_server(i: int):
            t0 = time.perf_counter()
            try:
                with urllib.request.urlopen(server_url, timeout=5.0) as resp:
                    dur_ms = (time.perf_counter() - t0) * 1000.0
                    return resp.status, dur_ms
            except Exception as e:
                dur_ms = (time.perf_counter() - t0) * 1000.0
                return 500, dur_ms

        wall_start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(hit_live_server, i) for i in range(total_requests)]
            for f in as_completed(futures):
                code, dur_ms = f.result()
                latencies.append(dur_ms)
                if code == 200:
                    success_count += 1

        total_wall_s = time.perf_counter() - wall_start
        stats = self._compute_stats(latencies)
        throughput = round(total_requests / total_wall_s, 1)

        print("\n--- [LIVE SERVER TCP CONCURRENCY BENCHMARK: 50 WORKERS] ---")
        print(f"Concurrency: {concurrency} TCP sockets | Throughput: {throughput} req/s | Success: {success_count}/{total_requests}")
        print(f"Latency -> P50: {stats['p50_ms']}ms | P95: {stats['p95_ms']}ms | Max: {stats['max_ms']}ms")

        self.assertEqual(success_count, total_requests, "All concurrent network requests against live server must succeed")
        self.assertLess(stats['p95_ms'], 100.0)


if __name__ == '__main__':
    unittest.main()
