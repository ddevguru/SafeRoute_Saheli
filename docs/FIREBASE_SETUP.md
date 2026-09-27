# SafeRoute Saheli — Firebase Cloud Messaging (FCM) & Push Notifications Guide

## 1. Overview
SafeRoute Saheli uses **Firebase Cloud Messaging (FCM)** via the **Firebase Admin SDK (Python)** on the Flask backend and the **Flutter client** to deliver instant, high-priority notifications to guardians and users.

> **CRITICAL SECURITY RULE:** Firebase Admin credentials and private keys are **NEVER** bundled or exposed in the Flutter mobile application. The Flutter app only obtains its device registration token and syncs it with the backend via authenticated HTTPS calls.

---

## 2. Notification Types & Priority Levels

| Notification Type | Trigger Event | Priority | Channel / Sound | Recipients |
|---|---|---|---|---|
| **`EMERGENCY_ALERT`** | Hardware Touch SOS, Voice "HELP", Clap, App Hold Button, Fall | **MAX / High** | `emergency_channel`<br>*(emergency_siren)* | All linked guardians + Emergency contacts |
| **`BATTERY_WARNING`** | IoT Wearable battery drops below 20% (Warning) or 10% (Critical) | High | `default`<br>*(default)* | Saheli (20%), Saheli + Primary Guardians (<=10%) |
| **`ROUTE_DEVIATION`**| GPS deviates beyond threshold from selected route corridor | High | `default`<br>*(warning_beep)* | Saheli |
| **`DEVICE_OFFLINE`** | ESP32 wearable device misses heartbeat check-in interval | Normal | `default`<br>*(subtle)* | Saheli |
| **`TEST_ALERT`** | QA verification from app or Admin Portal | High | `default` | Calling account |

---

## 3. High-Priority Emergency Payload Contract

When an emergency incident is triggered, `NotificationService.sendEmergencyPush()` transmits the following standardized payload:

```json
{
  "notification": {
    "title": "🚨 Emergency Alert",
    "body": "Riya Sharma has triggered an emergency (TOUCH). Tap to view live location."
  },
  "data": {
    "incident_id": "inc-8f2a1b9c",
    "user_id": "usr-3e7d9a11",
    "user_name": "Riya Sharma",
    "trigger_type": "TOUCH",
    "latitude": "28.6139",
    "longitude": "77.2090",
    "tracking_token": "u_9Z1Kx...sec48",
    "tracking_url": "https://saheli.safe/track/u_9Z1Kx...sec48",
    "timestamp": "2026-09-27T12:00:00Z",
    "type": "EMERGENCY_ALERT",
    "click_action": "FLUTTER_NOTIFICATION_CLICK"
  },
  "android": {
    "priority": "high",
    "notification": {
      "channel_id": "emergency_channel",
      "sound": "emergency_siren",
      "priority": "max",
      "default_vibrate_timings": true
    }
  },
  "apns": {
    "payload": {
      "aps": {
        "sound": "default",
        "content_available": true,
        "interruption_level": "time-sensitive"
      }
    }
  }
}
```

---

## 4. Backend Configuration & Setup

### A. Environment Variables (`backend/.env`)
```ini
# Firebase Project ID
FIREBASE_PROJECT_ID=saferoute-saheli-prod

# Option 1: File-based Service Account (Recommended for Kubernetes/Docker)
FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase-service-account.json

# Option 2: Inline Environment Variables (Recommended for Cloud PaaS)
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xyz@saferoute-saheli-prod.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"

# Development & Test Mode (Simulates FCM without external calls)
TEST_MODE=false
```

### B. Graceful Mock / Fallback Architecture
If running locally without real Firebase credentials (`TEST_MODE=true`), `FirebaseAdminClient` automatically enters simulated mode:
- Push notifications are logged to `NotificationLog` table.
- Simulated delivery references (`mock-fcm-...`) are stored in `EmergencyNotification`.
- Real-time updates are immediately broadcast over WebSockets to open Flutter and React Admin screens.
- The server will **never crash** due to missing cloud credentials.

---

## 5. Device Token REST API

### 1. Register or Update FCM Token
- **Endpoint:** `POST /api/notifications/tokens`
- **Headers:** `Authorization: Bearer <JWT>`
- **Request Body:**
  ```json
  {
    "fcm_token": "eX1Z8A...fcm_registration_token...",
    "platform": "ANDROID"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "FCM token registered successfully",
    "token_id": "tok-4a11-b9cd",
    "role": "GUARDIAN"
  }
  ```

### 2. List Active Tokens
- **Endpoint:** `GET /api/notifications/tokens`
- **Headers:** `Authorization: Bearer <JWT>`
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "count": 1,
    "tokens": [
      {
        "id": "tok-4a11-b9cd",
        "fcm_token": "eX1Z8A...",
        "platform": "ANDROID",
        "created_at": "2026-09-27T10:15:00"
      }
    ]
  }
  ```

### 3. Revoke Token on Signout
- **Endpoint:** `DELETE /api/notifications/tokens`
- **Headers:** `Authorization: Bearer <JWT>`
- **Request Body (Optional):**
  ```json
  {
    "fcm_token": "eX1Z8A..."
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "1 token(s) revoked successfully"
  }
  ```

### 4. Dispatch Test Notification
- **Endpoint:** `POST /api/notifications/test`
- **Headers:** `Authorization: Bearer <JWT>`
- **Request Body:**
  ```json
  {
    "title": "🧪 Test Emergency Siren",
    "body": "Checking device sound & vibration channel"
  }
  ```

---

## 6. Flutter Mobile Integration

The Flutter client manages notifications through `FcmNotificationService`:

```dart
// 1. Initialize notification channel (in main.dart or after login)
await FcmNotificationService.initialize();

// 2. Sync token with backend upon FCM token refresh
await FcmNotificationService.syncDeviceToken(freshFcmToken);

// 3. Listen to incoming push notifications in UI components
FcmNotificationService.payloadStream.listen((data) {
  if (data['type'] == 'EMERGENCY_ALERT') {
    // Navigate immediately to ActiveEmergencyScreen or Guardian viewer
  }
});
```

---

## 7. Testing & Verification

Run the automated notification test suite:
```bash
python -m unittest tests/test_firebase_notifications.py
```

*Expected output: `Ran 9 tests ... OK`*
