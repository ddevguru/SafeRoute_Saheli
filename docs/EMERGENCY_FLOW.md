# SafeRoute Saheli — Unified Emergency State Machine & Multi-Channel Pipeline

## 1. Overview
SafeRoute Saheli executes an ultra-reliable, deterministic emergency pipeline. Regardless of whether an alarm is initiated by hardware capacitive touch, acoustic keyword detection, acoustic clap pattern, physical motion anomaly, or in-app press-and-hold button, all triggers enter a unified arbitration state machine.

---

## 2. Emergency Trigger Classification

| Event Trigger Code | Physical / Digital Source | Detection Mechanism | Confidence Threshold |
|---|---|---|---|
| **`TOUCH`** | TTP223 Sensor on GPIO 13 | 1.5s continuous hold, active HIGH | `1.00` |
| **`BUTTON`** | Flutter Mobile Client UI | 2.5s press-and-hold with haptic dial | `1.00` |
| **`VOICE`** | INMP441 I2S Microphone | Keyword Spotting ("HELP", "SAVE ME", "BACHAO") | `>= 0.85` |
| **`CLAP`** | INMP441 I2S Microphone | 3 rapid peak spikes within 700ms window | `>= 0.90` |
| **`MOTION_FALL`** | MPU6050 Accelerometer | Vector magnitude $> 2.8g$ followed by stillness | `>= 0.85` |
| **`MOTION_STRUGGLE`**| MPU6050 Gyroscope | High angular velocity tumble ($> 200^\circ/s$) | `>= 0.80` |
| **`MULTI_SIGNAL`** | Sensor Fusion | Simultaneous motion anomaly + vocal trigger | `1.00` |

---

## 3. Finite State Machine (FSM) Diagram

```
 +-------------------------------------------------------------------+
 |                             NORMAL                                |
 +-------------------------------------------------------------------+
                                   |
                     (Any Trigger Source Detected)
                                   v
 +-------------------------------------------------------------------+
 |                    TRIGGER_DETECTED & VERIFY                      |
 |         (Debounce acoustic spikes & check confidence)             |
 +-------------------------------------------------------------------+
                                   |
                       [Confidence >= Threshold]
                                   v
 +-------------------------------------------------------------------+
 |                        EMERGENCY_ACTIVE                           |
 |  1. Hardware Actuators: Piezo Buzzer ON + Vibration Motor ON      |
 |  2. Optical Unit: ESP32-CAM White Flashlight + 5-Frame Burst      |
 |  3. Acoustic Unit: Audio clip recording triggered                |
 |  4. Navigation: Acquire NEO-6M High-Precision GPS Lock            |
 +-------------------------------------------------------------------+
                                   |
                                   v
 +-------------------------------------------------------------------+
 |                   BACKEND INCIDENT DISPATCH                       |
 |  1. Create DB Incident Record in `emergency_incidents`            |
 |  2. Generate Revocable Secure Tracking Session (`/track/<token>`) |
 |  3. Dispatch High-Priority FCM Siren Push to Guardians            |
 |  4. Dispatch Emergency SMS with Google Maps & Live Tracking URL   |
 |  5. Place Automated Twilio/Exotel Emergency Voice Call            |
 |  6. Broadcast Real-Time WebSocket to `saheli_<id>` and Admin      |
 +-------------------------------------------------------------------+
                                   |
                                   v
 +-------------------------------------------------------------------+
 |                    ACTIVE GUARDIAN MONITORING                     |
 |  - Guardian views real-time GPS path (5s refresh interval)        |
 |  - Authenticated Live ESP32-CAM Stream Preview                    |
 |  - Nearest Help Cards: Police (350m), Hospital (800m), Safe Place |
 +-------------------------------------------------------------------+
             |                                           |
    [Hold Cancel Button]                        [Police/Admin Resolve]
             v                                           v
 +-----------------------+                   +-----------------------+
 |       CANCELLED       |                   |       RESOLVED        |
 | (Logged False Alarm)  |                   | (Safely Closed Dossier|
 +-----------------------+                   +-----------------------+
```

---

## 4. Multi-Channel Dispatch Fallback Matrix

An emergency contact may not have the SafeRoute Saheli app installed or mobile data active. The system guarantees delivery through three tiered fallback channels:

```
[Emergency Triggered]
         │
         ├──► 1. Guardian with App: FCM High-Priority Push + WebSocket Live Stream
         │
         ├──► 2. Guardian without App: Emergency SMS with Google Maps & Tracking Link
         │
         └──► 3. Voice Fallback: Automated Phone Call with Text-to-Speech Message
```

### SMS Format:
```
🚨 SAFEROUTE SAHELI EMERGENCY ALERT!

Emergency triggered by: Riya Sharma
Trigger: TOUCH
Battery: 85%
Location: https://maps.google.com/?q=28.6139,77.2090
Live Tracking: https://saheli.safe/track/sec_token_9x

Please check immediately.
```

---

## 5. De-escalation & Cancellation Guard

To prevent an attacker from easily suppressing an active emergency alert:
- **Press-and-Hold Required:** The in-app cancellation button requires a continuous press-and-hold action with a confirmation dialog.
- **Audit Reason Required:** Every cancellation requires a reason (`"User confirmed safe"` or `"False alarm"`).
- **Incident Preservation:** Cancelled incidents are never deleted; their telemetry, audio snippets, and captured camera frames remain archived in the evidence dossier for accountability.
