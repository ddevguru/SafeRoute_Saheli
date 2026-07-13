# 📋 SafeRoute Saheli Project Scope

> **Complete specification for building a safe, ethical women’s safety ecosystem**

SafeRoute Saheli is an **AIoT-powered emergency response platform** comprising three interconnected layers: a discreet wearable safety device, a comprehensive mobile app, and an intelligent admin dashboard. The system enables rapid emergency alerts, evidence preservation, predictive threat detection, and secure incident management—all designed with privacy and consent at its core.

**Technology Stack:**
- 📱 Mobile: **Flutter** (Android & iOS)
- 🖥️ Web: **React** + TypeScript
- ⚙️ Backend: **Node.js/Express**
- 🗄️ Database: **PostgreSQL**

**Core Principle:** This platform is built as an emergency **safety and evidence-support system**, not surveillance software. All media capture is user-initiated or emergency-triggered, with strict access controls, encryption, retention policies, and comprehensive audit trails.

---

## 🎯 Project Goals

| Goal | Purpose |
|------|---------|
| 🆘 **Emergency Response** | Enable one-tap SOS activation with automatic contact escalation |
| 📍 **Live Location Sharing** | Real-time tracking with trusted guardians and emergency responders |
| 📹 **Evidence Preservation** | Secure timestamped capture of images, audio, and video during incidents |
| 🤖 **Threat Intelligence** | Multi-sensor AI/ML for detecting stalking, harassment, and dangerous patterns |
| 📊 **Admin Command Center** | Dashboard for emergency monitoring, escalation workflows, and response coordination |
| 💎 **Discreet Wearable Design** | Jewelry-like form factor (pendant, charm, brooch) for inconspicuous protection |
| 🛡️ **Digital Abuse Support** | Document, classify, and export evidence for platform harassment and online threats |

## ⚠️ Problem Statement

Women face **layered, evolving safety threats**:
- **Physical threats:** Stalking, harassment, unsafe travel, assault
- **Digital threats:** Impersonation, harassment, blackmail, non-consensual content sharing
- **Access barriers:** Situations where phones are unavailable, controlled, or unsafe to use
- **Evidence gaps:** Lack of secure, time-stamped documentation for authorities
- **Response delays:** Slow or unreliable emergency contact workflows

**Current tools are insufficient:** A single SOS button cannot combine threat detection, evidence preservation, escalation, and real-time monitoring. SafeRoute Saheli bridges this gap with an integrated **wearable + app + backend + dashboard** ecosystem.

---

## 🔍 Scope Definition

### ✅ In Scope
- 📟 **Wearable IoT Device** — ESP32-based discreet safety trigger
- 📱 **Flutter Mobile App** — Primary user interface and control center
- 🖥️ **React Admin Dashboard** — Real-time incident monitoring and escalation
- ⚙️ **Node.js/Express Backend** — API, authentication, and business logic
- 🗄️ **PostgreSQL Database** — Normalized schema for users, incidents, and logs
- 📍 **Location Sharing & SOS Workflows** — Real-time tracking and emergency escalation
- 📸 **Evidence Capture** — Timestamped photos, audio, and short video clips
- 🤖 **AI/ML Risk Scoring** — Threat detection and pattern analysis
- 👥 **Escalation Framework** — Trusted contacts, guardians, and responders
- 📊 **Incident Analytics** — History, timelines, and evidence review
- 🛡️ **Digital Abuse Module** — Documentation, tagging, and exportable reports

### ❌ Out of Scope for MVP

- 🚫 Continuous covert recording in normal mode
- 🚫 Surveillance of other people without their consent
- 🚫 Long-duration real-time video streaming
- 🚫 Automatic access to private social media or encrypted messages
- 🚫 Guaranteed legal enforcement (requires human review and approval)

---

## 🏛️ System Components

### 📟 **5.1 Wearable Device**
The cornerstone of the SafeRoute ecosystem. Disguised as pendant jewelry (locket, brooch, charm, or bracelet module), it serves as the primary emergency trigger and evidence capture device.

**Key capabilities:**
- Emergency SOS activation (button or voice command)
- Low-power BLE communication with phone
- Camera, microphone, and IMU sensors
- Secure pairing with Flutter app
- Haptic feedback for confirmation

### 📱 **5.2 Mobile Application (Flutter)**
The central hub for user interaction and control.

**Key capabilities:**
- User registration and onboarding
- Wearable device pairing and management
- Trip mode with continuous location sharing
- Manual and voice-triggered SOS
- Emergency contact management
- Evidence capture and upload
- Risk alerts and safety recommendations
- Device health monitoring

### 🖥️ **5.3 Admin Dashboard (React)**
Real-time command center for guardians, safety staff, and emergency responders.

**Key capabilities:**
- Live incident monitoring and map view
- User and device management
- Evidence review with file download
- Route-risk heatmaps and analytics
- Escalation workflow controls
- Role-based access and audit logs

### ⚙️ **5.4 Backend Services (Node.js/Express)**
Intelligent core handling all business logic and integrations.

**Key capabilities:**
- JWT-based authentication and authorization
- Device pairing and secure key exchange
- Alert routing and notification dispatch
- AI/ML threat scoring and analysis
- Evidence metadata management
- Real-time updates via Socket.IO
- Audit trail logging

### 🗄️ **5.5 Database (PostgreSQL)**
Normalized schema storing all critical data with strict access controls.

**Structure:**
- Users, profiles, and authentication
- Devices and pairings
- Incidents, alerts, and evidence metadata
- AI scores and threat assessments
- Abuse reports and classifications
- Audit and admin logs

**Note:** Media files (images, audio, video) are stored in S3-compatible object storage with encrypted paths and signed URLs.

---

## 🛠️ Hardware Specifications

### 📦 **6.1 Component Options**

| Component | Options | Purpose |
|-----------|---------|---------|
| **Microcontroller** | ESP32-S3, ESP32-S3 Sense, ESP32-CAM | Core processing, Wi-Fi/BLE |
| **Sensors** | OV2640 camera, MEMS microphone, MPU6050 IMU | Evidence capture & motion detection |
| **Connectivity** | BLE 5.0, Wi-Fi, GPS module | Device pairing and location |
| **Actuator** | Vibration motor (ERM/LRA) | Haptic feedback |
| **Power** | Li-Po cell (1-3Ah), charging circuit | 4-8 hour runtime |
| **Trigger** | Mechanical button, capacitive touch, NFC | User activation |
| **Enclosure** | 3D-printed, custom PCB in jewelry form | Pendant, locket, charm, brooch |

### 💡 **6.2 Recommended Prototype Configuration**

**Best for MVP:** **ESP32-S3 Sense + custom jewelry enclosure**
- ✅ All sensors in one compact board
- ✅ Wi-Fi + BLE for reliable pairing
- ✅ Camera and microphone built-in
- ✅ Battery charging support
- ✅ Affordable and quick prototyping

**For Production:** **Custom ESP32-S3 PCB + jewelry housing**
- Smaller footprint optimized for pendant/locket shape
- Detached camera and microphone modules
- Enhanced battery management
- Better thermal characteristics

### ⚡ **6.3 Known Hardware Challenges & Solutions**

| Challenge | Root Cause | Solution |
|-----------|-----------|----------|
| **Battery Drain** | Camera, GPS, Wi-Fi active all the time | Deep sleep, event-triggered capture, burst mode |
| **Overheating** | Compact jewelry enclosure traps heat | Low-duty-cycle networking, passive cooling |
| **False Triggers** | Accidental button presses or misheard voice commands | Confirmation timer, confidence threshold, haptic feedback |
| **Connectivity Loss** | Poor BLE/WiFi in certain areas | Local buffering, SMS fallback, last-known location |
| **Camera Visibility** | Lens opening breaks disguise | Jewelry-like front design, limited FOV placement |
| **Battery Placement** | Li-Po cell doesn't fit pendant | Split design: trigger module + battery charm |

---

## 🔧 Device Architecture Options

### **Option A: Single Pendant Module** (All-in-One)
```
┌──────────────────────┐
│  📷 Camera (front)   │
├──────────────────────┤
│  PCB Stack (middle)  │
├──────────────────────┤
│  🔋 Battery (rear)   │
└──────────────────────┘
```
**Pros:** Simple, compact, impressive demo  
**Cons:** Heat issues, tight space, limited expandability  
**Best for:** Proof-of-concept and presentations

---

### **Option B: Split Wearable Design** (Modular)
```
Pendant Module          Necklace Charm
┌──────────────┐       ┌──────────┐
│ 📷 Trigger   │  ←→   │   🔋     │
│ 🎤 Sensors   │ BLE   │ Battery  │
│ PCB          │       │ Module   │
└──────────────┘       └──────────┘
```
**Pros:** Better battery placement, improved thermal management, modular upgrades  
**Cons:** More complex assembly  
**Best for:** Mid-stage production and user comfort

---

### **Option C: Wearable + Phone Assist** ⭐ (Recommended for MVP)
```
Wearable          ←→  Flutter App  ←→  Backend
┌─────────────┐      ┌─────────┐      ┌──────┐
│ 🔘 Trigger  │ BLE  │ 📍 GPS  │ Net  │ AI   │
│ 📹 Sensors  │      │ 📸 Cam  │      │ ML   │
│ Low Power   │      │ Logic   │      │      │
└─────────────┘      └─────────┘      └──────┘
```
**Pros:** Minimal battery load, phone-scale processing, best reliability  
**Cons:** Requires phone proximity  
**Best for:** MVP (strongest balance of cost, size, reliability)

---

## ✨ Functional Features

### 📟 **8.1 Wearable Capabilities**

**Activation & Alerts**
- 🔴 **Emergency SOS** — Loud, visible alert with automatic contact escalation
- 🔇 **Silent SOS** — Discreet activation without audible alarm
- 🎤 **Voice Commands** — Wake-word and emergency phrase detection
- 📳 **Haptic Feedback** — Vibration motor confirmation

**Evidence Capture**
- 📸 **Image Capture** — High-quality emergency photos
- 🎙️ **Audio Recording** — Ambient sound and voice capture
- 🎥 **Video Clips** — Short 10-30 second emergency recordings
- 📍 **Location Tagging** — GPS coordinates with each capture

**Monitoring & Communication**
- 📡 **Secure Pairing** — Encrypted BLE link with Flutter app
- 🔋 **Battery Reporting** — Real-time power status
- 🌐 **Connectivity Status** — Signal strength and network status
- 🧠 **Motion Detection** — IMU-based fall or struggle alerts

---

### 📱 **8.2 Mobile App (Flutter) Features**

**User Management**
- ✍️ Sign-up with email/phone verification
- 🔐 Secure login and session management
- 👤 Profile setup (name, age, preferences)
- 🔐 Password reset and recovery

**Device & Contacts**
- 🔗 Wearable pairing and re-pairing
- 👥 Emergency contact management (name, phone, email)
- 🛡️ Trusted guardian setup and permissions
- 📊 Device health and battery monitoring

**Safety Features**
- 🚗 **Trip Mode** — Continuous location tracking during travel
- 🗺️ **Live Map** — Real-time location with breadcrumb trail
- 💚 **Safe Route** — AI-powered safe travel suggestions
- 🆘 **Manual SOS** — Tap to trigger emergency without wearable
- 🔇 **Silent SOS** — Discreet alert without wearables alarm

**Evidence & Reporting**
- 📹 Evidence upload (photos, audio, video)
- 📋 Incident timeline with metadata
- 🛡️ Digital abuse reporting with auto-classification
- 📊 Safety score and risk alerts
- 🔐 Encrypted evidence storage

**User Experience**
- ⏰ Check-in reminders during trip mode
- 🚨 Real-time push notifications
- 📞 Quick-dial emergency contacts
- ⚙️ Granular privacy and notification settings

---

### 🖥️ **8.3 Admin Dashboard (React) Features**

**Incident Management**
- 🗺️ **Live Map View** — Real-time incident map with pinned locations
- 🔴 **Incident Queue** — Prioritized by severity (critical → low)
- 📋 **Incident Details** — Full context, contacts, and evidence
- 📸 **Evidence Viewer** — Secure image/audio/video player
- 🔗 **Chain of Custody** — Audit trail for evidence access

**User & Device Management**
- 👥 **User List** — All users with registration date and status
- 📟 **Device Monitoring** — Wearable firmware, battery, last-seen
- 🔧 **Device Management** — Repair, revoke, re-issue commands
- 🛡️ **Trusted Guardian Approval** — Verify guardians and permissions

**Analytics & Insights**
- 🔥 **Route-Risk Heatmap** — Incident density and danger zones
- 📊 **Incident Analytics** — Trends, severity distribution, response times
- 🎯 **SOS Effectiveness** — Response rate and escalation success
- 🕐 **Time-of-Day Analysis** — When incidents are most likely

**Admin Tools**
- 🎯 **Escalation Controls** — Assign, reassign, or close incidents
- 📞 **Contact Dispatch** — Send alerts to guardians or responders
- 📄 **Report Export** — PDF/CSV export for authorities
- 🔐 **Role Management** — Assign admin, operator, viewer roles
- 📋 **Audit Logs** — Complete activity history with timestamps

---

## 🤖 AI/ML Intelligence Layer

### 🚨 **9.1 Stalking Risk Scoring** (NOT Absolute Detection)

**Important:** System reports **"suspicious follow patterns"** not **"stalker detected"**

**Multi-Sensor Signals:**
- 📍 GPS route mirroring (distance, bearing, speed similarity)
- 📡 Repeated Bluetooth proximity patterns
- ⏰ Time-of-day correlation with user commute history
- 🚶 Movement anomalies (unusual stops, sudden acceleration)
- 🗺️ Deviation from user's normal travel areas

**Risk Levels:**
- 🟢 **Low:** <30% confidence — informational, no alert
- 🟡 **Medium:** 30-60% confidence — user notification, optional evidence capture
- 🔴 **High:** 60-85% confidence — guardian alert, recommended SOS
- 🔴 **Critical:** >85% confidence — auto-escalation to responders

---

### 🗺️ **9.2 Safe Route Prediction**

**Input Signals:**
- 📊 Historical incident density by location and time
- ⏰ Day-of-week and time-of-day risk patterns
- 🚫 Known danger zones and user blacklist
- 👥 Community reports and Saheli user feedback
- 📱 User preferences (fast vs. safe route)

**Output:** Route recommendation with risk scorecard, not a guarantee

---

### 🎤 **9.3 Voice Command Recognition**

**Design Principles:**
- Privacy-first: Local on-device keyword spotting
- Limited command set: SOS, "record," "share location," "call mom"
- Confidence threshold: Only activate if >85% confident
- No continuous transcription in normal mode

**Activation Phrases:**
- "Hey Saheli" (wake-word)
- "Emergency" or "Help" (panic trigger)
- "Record evidence" (start capture)

---

### 🧠 **9.4 Motion Anomaly Detection (IMU/Accelerometer)**

**Patterns Detected:**
- 📉 Sudden impact or fall (rapid Z-axis spike)
- 🏃 Running motion (high-frequency acceleration)
- 💪 Struggle movement (erratic multi-axis oscillation)
- 🤸 Unusual jerk patterns (inconsistent with normal gait)

**Fusion:** Combined with location (stationary), voice (fear), and time (late night) for context

---

### 📊 **9.5 Threat Level Classification**

| Level | Confidence | Signals | Response |
|-------|-----------|---------|----------|
| **Low** | <30% | Single weak signal | App notification only |
| **Medium** | 30-60% | Multiple weak signals | User alert + optional capture |
| **High** | 60-85% | Strong signal cluster | Guardian notification + location share |
| **Critical** | >85% | Multiple strong signals | Auto-escalate to responders |

---

### 🛡️ **9.6 Digital Abuse Auto-Classification**

**Supported Categories:**
- 😠 **Harassment** — Repeated unwanted messages
- 👤 **Impersonation** — Fake profiles claiming to be you
- 🔗 **Stalking** — Excessive monitoring/tracking online
- 💰 **Blackmail/Extortion** — Threats for money/favors
- ⚠️ **Threat** — Direct violence or harm statements
- 🔞 **Obscene** — Non-consensual sexual content

**Mechanism:** ML classifier on user-uploaded screenshots + manual review

---

### 🧮 **9.7 Fuzzy Risk Engine** (Multi-Signal Fusion)

**Formula:**
```
Safety Score = (0.3 × route_risk) + (0.2 × motion_anomaly) 
             + (0.25 × location_deviation) + (0.15 × time_context)
             + (0.1 × voice_confidence)
```

**Output:** Single 0-100 safety score updated in real-time on app and dashboard

---

## 🛡️ **10. Digital Abuse Module**

### **10.1 Workflow**

```
User Import Screenshot → ML Classifier → Manual Review → Export Report
```

**Step-by-step:**
1. 📸 User shares screenshot or message link via app
2. 🔍 ML model auto-tags abuse category with confidence score
3. ✏️ User reviews, corrects, and adds context
4. 📋 System builds case bundle with metadata
5. 📤 User exports shareable report for platforms, police, or authorities

### **10.2 Metadata Captured**

| Field | Purpose |
|-------|---------|
| **Platform** | Social media, messaging app, email, etc. |
| **Username** | Account that sent/posted abusive content |
| **Timestamp** | When abuse occurred |
| **Link/URL** | Direct reference to the content |
| **Category** | Harassment, threat, impersonation, etc. |
| **Severity** | User-rated 1-5 |
| **Context** | User notes for authorities |

### **10.3 Known Limitations & Fixes**

| Limitation | Reason | Fix |
|-----------|--------|-----|
| **Can't read encrypted DMs** | End-to-end encryption blocks access | User manually shares content via screenshot |
| **False classification** | Slang, context, sarcasm confuse ML | Manual review step with easy correction |
| **Sensitive data in evidence** | Screenshots may contain PII | Encryption at rest + role-based access |
| **No automatic platform reporting** | APIs don't exist for all platforms | Provide exportable reports and templates |

---

## 🔍 **11. Stalking Detection Deep Dive**

### **11.1 Design Philosophy**

> ❌ **DON'T:** “Stalker detected” ← Claims certainty  
> ✅ **DO:** “Suspicious follow-pattern detected” ← Graded confidence

System is designed for **awareness**, not accusation. Multiple weak signals → medium confidence → guardian alert (not auto-SOS).

### **11.2 Signal Combination Table**

| Signal | Detection Method | Weight | Notes |
|--------|------------------|--------|-------|
| **GPS Mirror** | Route similarity (>80%) for 2+ trips | 30% | Most reliable |
| **BLE Proximity** | Repeated <10m distance matches | 20% | Smartphone-level accuracy |
| **Stop Matching** | Same stops at same times (>70% match) | 15% | Commute pattern interference |
| **Speed Sync** | Velocity correlation >0.8 | 15% | Could be shared transport |
| **Time Context** | Late night (23:00-05:00) risk multiplier | 10% | Statistically riskier hours |
| **User Report** | Manual “felt unsafe” flag | 10% | Subjective but valuable |

### **11.3 Known False Positive Scenarios & Fixes**

| Scenario | Cause | Fix |
|----------|-------|-----|
| **Shared commute** | Bus/train followed by many people | Time-window narrowing, speed variance check |
| **Popular route** | Same highway everyone uses | Geofence to “unusual” areas only |
| **Coincidence** | Two people happen to go same way | Require 3+ pattern repeats within 2 weeks |
| **Shared destination** | Workplace/gym in same building | Exclude known common destinations |

### **11.4 Escalation Workflow**

```
Weak Signal (20-40%)        Medium Signal (40-70%)        Strong Signal (70%+)
        ↓                           ↓                             ↓
  App notification          Guardian notification         Auto-escalate + 
  Optional evidence         Optional SOS prompt           Prompt emergency mode
```

---

## 📱 **12. App Screen Flows**

### **12.1 User App (Flutter)**

**🔐 Onboarding Journey**
- Splash screen with logo
- Feature intro carousel (3-5 screens)
- Permission request (location, camera, mic, storage)
- Registration (email/phone + password)
- OTP or email verification
- Profile setup (name, age, emergency address)
- Wearable pairing wizard

**🏠 Main Dashboard**
- Live safety score (0-100 gauge)
- Quick SOS button (large, red)
- Trip mode toggle
- Current device status (battery, connection)
- Last incident summary
- Safety tips carousel

**🚗 Trip Mode Flow**
- Trip start confirmation (destination, ETA)
- Live map with breadcrumb trail
- Real-time safety score updates
- Auto-stop on arrival or manual end
- Trip summary with risk heatmap overlay

**🆘 Emergency Workflow**
- SOS button → 10-second countdown confirmation
- Silent SOS (no alarm, discreet)
- Automatic location capture and contact escalation
- Live evidence capture (camera ready)
- Check-in reminders every 30 seconds
- Option to cancel within confirmation window

**📊 Evidence & Incident History**
- Incident timeline (reverse chronological)
- Evidence gallery (photos, audio, video)
- Timestamp and metadata for each file
- Easy share to contacts or police

**🛡️ Digital Abuse Module**
- Screenshot import
- Auto-tagging (harassment, threat, impersonation)
- Case bundle builder
- PDF export for authorities

**⚙️ Settings & Control**
- Profile (name, emergency address, contacts)
- Trusted guardians (add, remove, permissions)
- Emergency contacts (fast-dial list)
- Notification preferences
- Privacy and permissions audit
- Help and FAQ

---

### **🖥️ 12.2 Admin Dashboard (React)**

**🗺️ Incident Command Center**
- Live map with incident pins (color-coded by severity)
- Real-time incident queue (auto-sorted by severity)
- Incident detail panel (full context, contacts, evidence)
- Escalation action buttons

**📊 Dashboard Overview**
- Active incidents count (by severity)
- Response time metrics
- SOS vs. triggered incidents split
- Daily incident trend chart

**👥 User Management**
- All users list (search, filter by status)
- User detail view (contacts, device pairings, incident history)
- Trusted guardian approvals (new guardian requests)
- Role and permission management

**📟 Device Management**
- All wearables inventory
- Firmware version tracking
- Battery health monitoring
- Last-seen device status
- Repair and revoke workflows

**📹 Evidence Viewer**
- Secure media playback (photos, audio, video)
- Full audit trail of who accessed what, when
- Download with encrypted link
- Blur or redact sensitive areas

**📈 Analytics & Reporting**
- Route-risk heatmap (incident density by location)
- Time-of-day risk analysis
- SOS response effectiveness metrics
- Export reports (PDF, CSV)

---

## 🗄️ **13. Data Model & Schema**

### **13.1 Core Entities**

```
Users (1) ──→ (M) User_Profiles
        ├─→ (M) Device_Pairings ──→ Devices
        ├─→ (M) Contacts ──→ Emergency_Contacts
        ├─→ (M) Trips ──→ (M) Trip_Points
        ├─→ (M) Alerts ──→ Incidents ──→ (M) Evidence
        └─→ (M) Abuse_Reports

Incidents ──→ (M) AI_Scores
            ──→ (M) Notifications

Admin_Users ──→ (M) Admin_Logs
             ──→ (M) Audit_Logs
```

### **13.2 PostgreSQL Table Structure**

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **users** | User accounts | id, email, phone, password_hash, created_at |
| **user_profiles** | Extended profile info | user_id, age_group, emergency_address, preferences |
| **roles** | Role definitions | id, role_name (user, guardian, operator, admin) |
| **user_roles** | Role assignments | user_id, role_id, assigned_by, assigned_at |
| **devices** | Wearable inventory | id, device_uuid, device_type, firmware_version, battery_level |
| **device_pairings** | User-device relationships | user_id, device_id, pairing_status, paired_at |
| **contacts** | Contact directory | id, user_id, contact_name, contact_phone, contact_email |
| **emergency_contacts** | Escalation settings | user_id, contact_id, notify_sms, notify_push, notify_call |
| **trips** | Trip sessions | id, user_id, trip_name, start_location, end_location, trip_status, risk_score |
| **trip_points** | GPS coordinates | trip_id, latitude, longitude, speed, heading, captured_at |
| **alerts** | Emergency alerts | id, user_id, trip_id, alert_type, severity, trigger_source, status |
| **incidents** | Full incident records | alert_id, user_id, title, summary, incident_type, severity, location, status |
| **evidence** | Media metadata | incident_id, media_type, file_name, file_path (S3), file_hash, captured_at |
| **abuse_reports** | Digital abuse documentation | user_id, category, platform_name, report_text, source_link, severity |
| **ai_scores** | ML inference results | incident_id, score_type, score_value, confidence, model_version |
| **notifications** | Delivery tracking | user_id, alert_id, channel (push/sms/email), status, sent_at, delivered_at |
| **admin_logs** | Admin actions | admin_user_id, action_type, target_type, target_id, action_details |
| **audit_logs** | Complete audit trail | actor_id, actor_role, action, resource_type, resource_id, old_value_json, new_value_json |

---

## ⚙️ **14. Backend Architecture (Node.js/Express)**

### **14.1 Core Modules**

```
Express Server
├── 🔐 Auth Module → JWT/OAuth, password hashing
├── 👤 User Module → Profile, preferences, deletion
├── 📟 Device Module → Pairing, firmware, status
├── 🆘 Alert Module → SOS trigger, routing, escalation
├── 🚗 Trip Module → Location tracking, route analysis
├── 📸 Evidence Module → File upload, encryption, signed URLs
├── 🤖 AI/ML Module → Risk scoring, threat detection
├── 📧 Notification Module → FCM, SMS, Email, WebSocket
├── 👥 Admin Module → User mgmt, roles, escalation
├── 📊 Analytics Module → Heatmaps, trends, reporting
└── 📋 Audit Module → Access logs, compliance tracking
```

### **14.2 REST API Endpoints**

| Endpoint Group | Purpose | Key Endpoints |
|---|---|---|
| **`/auth`** | Authentication | POST /login, POST /register, POST /refresh, POST /logout |
| **`/users`** | User profiles | GET /me, PUT /profile, DELETE /account |
| **`/devices`** | Wearable mgmt | POST /pair, GET /list, PUT /:id/status, DELETE /unpair |
| **`/contacts`** | Emergency contacts | GET /list, POST /add, PUT /:id, DELETE /:id |
| **`/trips`** | Trip tracking | POST /start, PUT /:id/end, GET /history, POST /:id/location |
| **`/alerts`** | Emergency alerts | POST /create, GET /active, PUT /:id/resolve |
| **`/incidents`** | Incident mgmt | GET /list, GET /:id, PUT /:id/status, POST /:id/escalate |
| **`/evidence`** | Media upload | POST /upload, GET /:id/download, DELETE /:id |
| **`/reports`** | Digital abuse | POST /create, GET /list, POST /:id/export |
| **`/admin`** | Admin operations | GET /users, GET /incidents, PUT /user/:id/role |
| **`/analytics`** | Dashboards | GET /heatmap, GET /trends, GET /response-time |
| **`/notifications`** | Delivery | GET /history, PUT /:id/mark-read |

### **14.3 Real-Time Communication (WebSocket)**

**Socket.IO Channels:**
- `incident:new` — New incident alert (broadcast to admin)
- `incident:update` — Incident status change
- `location:ping` — Live location update (to guardians)
- `evidence:uploaded` — New evidence file notification
- `device:status` — Wearable battery, connection status

---

## 📢 **15. Notification & Escalation Stack**

| Channel | Use Case | Provider | Priority |
|---------|----------|----------|----------|
| **Push Notification** | Real-time app alerts | Firebase Cloud Messaging (FCM) | 🔴 Critical |
| **SMS** | Fallback for offline users | Twilio, AWS SNS | 🔴 Critical |
| **Email** | Reports, summaries | SendGrid, AWS SES | 🟡 Medium |
| **WhatsApp** | In-region messaging (if available) | WhatsApp Business API | 🟡 Medium |
| **In-App Notification** | Dashboard alerts | Socket.IO WebSocket | 🟡 Medium |
| **Phone Call** | Critical escalation | Twilio, AWS Connect | 🔴 Critical (optional) |

**Escalation Sequence:**
```
SOS Triggered → Push (3s) → SMS (5s) → Email (10s) → Call (if unresponsive)
```

---

## 🔒 **16. Security & Privacy Architecture**

### **16.1 Security Controls**

| Control | Implementation | Auditing |
|---------|---|---|
| **Transport** | HTTPS/TLS 1.3 for all APIs | Certificate pinning in mobile app |
| **Authentication** | JWT tokens (15min) + refresh tokens (7d) | Failed login attempts logged |
| **Authorization** | Role-based access control (RBAC) | Admin action logs + audit trail |
| **Data Encryption** | AES-256 at rest (media & sensitive data) | Encryption key rotation policy |
| **Media Storage** | S3-compatible with signed URLs (1hr TTL) | Audit log of all downloads |
| **Device Pairing** | BLE ECDH key exchange | Pairing timestamp + verification |
| **Consent Logging** | User explicit opt-in for camera/mic | Consent date, time, scope in audit |

### **16.2 Privacy Safeguards**

**❌ What We DON'T Do:**
- ❌ Continuous silent recording in normal mode
- ❌ Unauthorized access to social media or private messages
- ❌ Location tracking without explicit consent
- ❌ Selling or sharing user data with third parties
- ❌ Storing raw media beyond retention policy (90 days default)

**✅ What We DO:**
- ✅ Emergency-only recording with automatic shutdown
- ✅ User-driven evidence import for digital abuse
- ✅ Guardian role limits on location access
- ✅ Encrypted audit trail for all evidence views
- ✅ Right to delete and data portability (GDPR/CCPA)

### **16.3 Known Privacy Risks & Mitigations**

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Hidden camera in wearable** | 🔴 High | Emergency-only activation + app logs + consent audit |
| **Unauthorized admin access** | 🔴 High | RBAC roles + 2FA + audit trail review |
| **Location tracking abuse** | 🟡 Medium | Explicit guardian consent + time-limited access |
| **Evidence data breach** | 🔴 High | AES-256 encryption + key rotation + access logs |
| **Unauthorized device pairing** | 🟡 Medium | User approval required + notification + unpair option |

---

## ⚡ **17. Non-Functional Requirements**

| Requirement | Target | Metric |
|---|---|---|
| **Emergency Response Time** | <3 seconds | SOS trigger → contact notification |
| **SOS Delivery Rate** | >99.5% | Notifications reaching intended recipients |
| **Wearable Battery Life** | 6-8 hours | Continuous trip mode with sampling |
| **Dashboard Uptime** | 99.9% | Availability SLA (3 nines) |
| **Device Scalability** | 100K+ concurrent users | Load testing requirements |
| **Offline Capability** | 2-4 hour buffer | App queues alerts when no connectivity |
| **UI Responsiveness** | <500ms | Time to tap SOS → confirmation |
| **Evidence Upload** | Upload ≤30MB in <60s | On standard 4G connection |
| **Location Accuracy** | ±10 meters | GPS-assisted via phone |
| **Availability in Low Signal** | Emergency mode only | Degrades gracefully, preserves SOS |

---

## 🧑‍💻 **18. User Journey Maps**

### **18.1 Normal Daily Usage**

```
User Opens App → Check Safety Score → Enable Trip Mode
                                            ↓
                            Start: Confirm Destination
                                    ↓
                    Background: Live Location Sharing
                    + Safe Route Suggestions
                    + Risk Alerts (if any)
                                    ↓
                            Arrival: Auto or Manual End
                                    ↓
                        Trip Summary + Risk Analysis
```

### **18.2 Emergency Activation (SOS)**

```
Panic Moment
    ↓
SOS Trigger (button/voice) ← Wearable or App
    ↓
10-Second Confirmation (can cancel)
    ↓
[CONFIRMED] → Incident Created in Backend
    ↓
Simultaneous Actions:
├─ Location captured (GPS)
├─ Evidence capture ready (camera/audio)
├─ Trusted contacts notified (push/SMS/email)
├─ Guardian dashboard updated (live incident)
└─ Emergency responders alerted (if configured)
    ↓
App shows: "Help is coming" + Live tracking enabled
```

### **18.3 Digital Abuse Documentation**

```
User experiences abuse online
    ↓
Opens Digital Abuse Module
    ↓
Screenshots or shares message/link
    ↓
App auto-classifies (harassment, threat, impersonation)
    ↓
User reviews + adds context
    ↓
System builds case bundle (metadata, links, timestamps)
    ↓
User exports PDF report
    ↓
Share with: Platform support, police, trusted guardian

---

## 🛠️ **19. Technology Stack**

### **Frontend**

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| 📱 **Mobile App** | Flutter + Dart | Cross-platform (Android/iOS), excellent performance, BLE support |
| 🎨 **UI Framework** | Material 3 + GetX | Modern design, state management, minimal boilerplate |
| 📍 **Maps** | Google Maps + Flutter Maps | Real-time tracking, route display, offline cache |
| 🔊 **Audio** | just_audio + flutter_sound | Recording and playback, background execution |
| 📷 **Camera** | camera + image_gallery_saver | Evidence capture, image processing |

### **Web Admin Dashboard**

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| 🖥️ **Framework** | React 18 + TypeScript | Type safety, ecosystem maturity, component reuse |
| 🎨 **UI Components** | Material-UI (MUI) v5 | Professional dashboards, accessibility, theming |
| 📊 **Charts** | Recharts + Nivo | Real-time updates, interactive analytics |
| 🗺️ **Maps** | Leaflet + React-Leaflet | Lightweight, heatmap support, cluster markers |
| 🔄 **State** | Redux Toolkit | Predictable state, middleware for async operations |

### **Backend**

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| ⚙️ **Runtime** | Node.js 18+ | JavaScript ecosystem, non-blocking I/O, npm maturity |
| 🌐 **Framework** | Express.js | Lightweight, middleware ecosystem, minimal overhead |
| 🔐 **Auth** | JWT + bcrypt | Stateless authentication, password hashing |
| 🔗 **Real-time** | Socket.IO | WebSocket fallback, rooms for targeted messaging |
| 📊 **Logging** | Winston + Morgan | Structured logs, multiple transports, audit trail |

### **Database & Storage**

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| 🗄️ **Database** | PostgreSQL 14+ | ACID transactions, JSON support, PostGIS for geo-queries |
| 📚 **ORM** | Sequelize or TypeORM | Type safety, migrations, relationship management |
| ☁️ **Media Storage** | AWS S3 or MinIO | Encrypted storage, signed URLs, lifecycle policies |
| 🔍 **Search** | PostgreSQL Full-Text Search | Built-in, no external dependency, sufficient for MVP |
| 💾 **Cache** | Redis (optional) | Session management, rate limiting, notification queues |

### **DevOps & Deployment**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| 🐳 **Containers** | Docker | Consistent environments, easy scaling |
| 🔄 **Orchestration** | Docker Compose (dev) / Kubernetes (prod) | Service management |
| 🚀 **CI/CD** | GitHub Actions | Automated testing, deployment pipelines |
| 📋 **IaC** | Terraform (optional) | Infrastructure as code, repeatable deployments |
| 🔐 **Secrets** | GitHub Secrets / Vault | API keys, database credentials, encryption keys |

---

## ✅ **20. Testing Strategy**

### **20.1 Unit & Integration Tests**

| Test Level | Coverage | Tools |
|---|---|---|
| **Unit Tests** | API handlers, utilities, validators | Jest, Flutter test |
| **API Integration** | Backend endpoints, DB interactions | Supertest, Postman |
| **UI Component Tests** | React components, Flutter widgets | React Testing Library, flutter_test |
| **Database Tests** | Migrations, transactions, constraints | Sequelize/TypeORM test suites |

### **20.2 Feature-Level Testing**

| Feature | Test Scenarios | Priority |
|---|---|---|
| 🆘 **SOS Workflow** | Trigger → confirm → escalate → cancel | 🔴 Critical |
| 📍 **Location Tracking** | GPS capture, accuracy, permission handling | 🔴 Critical |
| 📸 **Evidence Capture** | Camera/audio/video in low light, storage | 🟡 High |
| 🔗 **Device Pairing** | Pairing, unpairing, re-pairing, BLE dropout | 🟡 High |
| 🤖 **AI Scoring** | Risk score calculation, false positives | 🟡 High |
| 📧 **Notifications** | Push, SMS, email delivery, retry logic | 🟡 High |
| 🔐 **Auth & RBAC** | Login, token expiry, role permissions | 🔴 Critical |

### **20.3 Performance & Load Testing**

- **Load Test:** 1K concurrent users, 100 SOS/min peak
- **Stress Test:** Push dashboard to failure, recovery
- **Endurance:** 24-hour continuous trip mode on wearable
- **Mobile:** Battery drain, memory leaks, ANR (Android Not Responding)

### **20.4 Security Testing**

- **Penetration Testing:** API security, SQL injection, XSS
- **Encryption Audit:** Key management, data at rest/in transit
- **Access Control:** RBAC enforcement, privilege escalation attempts
- **Secrets Scanning:** No hardcoded credentials, API keys in code

### **20.5 User Acceptance Testing (UAT)**

- Real users perform SOS flows
- Wearable battery and pairing in real conditions
- Guardian/responder dashboard workflows
- Digital abuse classification accuracy

---

## ⚠️ **21. Known System Limitations & Mitigations**

### **21.1 Stalking Detection Uncertainty**

**Problem:** No single sensor can prove stalking—only detect suspicious patterns  
**Risk Level:** 🟡 Medium  
**Mitigation:**
- Report "suspicious follow-pattern" not "stalker detected"
- Use multi-sensor fusion (GPS + BLE + time + motion)
- Graded confidence levels (low/medium/high/critical)
- Require 3+ pattern repeats before medium confidence
- User can manually report discomfort to increase confidence

---

### **21.2 Battery Drain on Wearable**

**Problem:** Camera, mic, Wi-Fi drain 100mAh per hour  
**Risk Level:** 🔴 High  
**Mitigation:**
- Use phone-assisted GPS (wearable handles trigger only)
- Deep sleep mode: wake only on button or BLE command
- Burst capture: 5-10 seconds max per emergency
- Hardware: Split design (trigger pendant + battery charm)
- Target: 6-8 hours trip mode, 48 hours standby

---

### **21.3 Hidden Camera Privacy Risk**

**Problem:** Camera in jewelry could enable covert recording  
**Risk Level:** 🔴 Critical  
**Mitigation:**
- Emergency-only activation (no normal mode recording)
- Consent audit: every camera use logged with timestamp
- Access audit: all evidence views logged + who accessed what
- Strict RBAC: only responders with explicit role
- App notification: "Camera activated" alert to user
- Automatic shutdown: max 30-second recording, then stop

---

### **21.4 False Emergency Alerts**

**Problem:** Accidental button presses or sudden braking creates false positives  
**Risk Level:** 🟡 Medium  
**Mitigation:**
- 10-second confirmation timeout (can cancel)
- Haptic + visual feedback before escalation
- Confidence thresholds for AI alerts
- User training on voice commands
- Escalation levels (silent → soft alert → loud alert)

---

### **21.5 Network Failure in Low Signal Areas**

**Problem:** SMS/push may fail if no network  
**Risk Level:** 🔴 High (in emergencies)  
**Mitigation:**
- Local event queue: buffer offline incidents
- Retry logic: exponential backoff (3s, 6s, 12s...)
- SMS fallback: if push fails, send SMS
- Offline mode: app continues recording and batching
- Last-known location: fallback to previous GPS point
- Wearable buffer: 4-hour offline incident storage

---

### **21.6 Wearable Device Loss or Tamper**

**Problem:** Pendant can be removed, lost, or stolen  
**Risk Level:** 🟡 Medium  
**Mitigation:**
- Disconnect alert: app notifies if BLE drops >5 min
- Tamper detection: IMU detects jerks/impact of removal
- Last-seen status: admin dashboard shows last location
- Remote disable: admin can revoke pairing
- Geo-alert: notify if device moves >1km from last location

---

### **21.7 Evidence Data Breach**

**Problem:** Images/audio/video contain sensitive evidence  
**Risk Level:** 🔴 Critical  
**Mitigation:**
- AES-256 encryption at rest (S3)
- Signed URLs (1-hour TTL, single use)
- Access audit: log every download (who, when)
- Role-based access: only responders with case assignment
- Retention policy: auto-delete after 90 days (unless extended)
- Encrypted database backups

---

### **21.8 Digital Abuse Classification Limitations**

**Problem:** ML model can't read encrypted private messages  
**Risk Level:** 🟡 Medium  
**Mitigation:**
- User-driven import: user manually shares screenshots
- No automatic API access to private platforms
- Manual review: user corrects ML classification
- False classification rate: acceptable at <10%
- Platform templates: exportable reports for manual submission

---

## 🎯 **22. Phased Delivery Roadmap**

### **Phase 1: MVP (Months 1-4)** ⭐ Focus & Ship

**🟢 Must-Have Features**
- ✅ User registration & authentication (email/phone OTP)
- ✅ Wearable device pairing (BLE handshake)
- ✅ Emergency SOS trigger (button & voice command)
- ✅ Silent SOS (discreet activation)
- ✅ Live location sharing (phone GPS, wearable BLE)
- ✅ Trusted contacts & emergency escalation
- ✅ Trip mode (continuous tracking)
- ✅ Evidence capture (photos + audio)
- ✅ Basic risk scoring (route safety)
- ✅ Admin dashboard (live incidents, map, evidence viewer)
- ✅ Incident logs & history
- ✅ Device battery & connectivity status
- ✅ Push & SMS notifications (FCM + Twilio)

**🟡 Nice-to-Have (If Time)**
- Guide-based onboarding with permissions
- Basic analytics (incident trends)
- Report export (PDF)

**🔴 Excluded**
- Digital abuse module (complex ML)
- Advanced AI threat detection (needs data)
- Offline mode (scope creep)
- Smartwatch support (new platform)

---

### **Phase 2: Intelligence Layer (Months 5-7)**

- 🤖 Advanced stalking-risk engine (multi-signal fusion)
- 📍 Safe route prediction (incident-based suggestions)
- 🛡️ Digital abuse classifier (harassment, threat, impersonation)
- 📹 Short video capture (emergency only, 10-30s)
- 👥 Role-based multi-admin workflow (operator vs. responder)
- 📊 Advanced analytics (heatmaps, time-of-day analysis)
- 🔊 Voice distress detection (cry detection on wearable)
- 💬 Guardian request approval workflow

---

### **Phase 3: Scale & Optimize (Months 8+)**

- 🧠 On-device ML inference (lighter models, wearable-native)
- ⌚ Smartwatch companion app (WearOS/watchOS)
- 📞 Auto-call integration (critical escalation)
- 📋 Automated report templates (exportable to police)
- 🗺️ Multi-city risk heatmaps (city-level insights)
- 🌐 Multi-language support (localization)
- 🔋 Custom low-power wearable hardware (production PCB)
- 👂 Ear-device audio prompts (discreet guidance)

---

## 🏗️ **23. Development Build Sequence**

**Parallel Work Streams (Weeks 1-4):**
1. 📱 Flutter app: core screens, auth module, state management setup
2. ⚙️ Backend: API scaffolding, database schema, middleware setup
3. 🖥️ React dashboard: layout, component library, mock data integration

**Sequential Phase (Weeks 5-8):**
4. 🔗 BLE Integration: wearable simulator, pairing flow, state sync
5. 📍 Location & SOS: GPS handling, contact escalation, real-time updates
6. 📸 Evidence Capture: camera/audio/video permissions, upload pipeline
7. 🚀 Dashboard Wiring: live incident feed, map integration, role-based UI

**Integration Phase (Weeks 9-12):**
8. 🤖 AI Scoring: risk engine, stalking detection, scoring API endpoints
9. 📧 Notifications: FCM setup, SMS gateway, delivery tracking
10. 🔐 Security Audit: encryption, RBAC enforcement, audit logging
11. 🧪 Testing: E2E flows, load testing, security penetration testing
12. 📚 Documentation: API docs, deployment guides, user manuals

---

## 🌟 **24. Final Brand Positioning**

> **"Technology built with care. Safety engineered with consent."**

### **What SafeRoute Saheli IS:**
- ✅ An **emergency safety platform** combining wearable, mobile, and admin tech
- ✅ An **evidence preservation system** for secure incident documentation
- ✅ An **intelligent risk detection tool** using multi-sensor AI/ML
- ✅ A **structured escalation framework** for fast emergency response
- ✅ A **privacy-first system** with transparent consent and audit trails

### **What SafeRoute Saheli IS NOT:**
- ❌ Surveillance software or covert tracking tool
- ❌ Replacement for law enforcement (requires human review)
- ❌ A guarantee of safety (probabilistic risk scoring only)
- ❌ Designed for abusive partners or stalkers to track victims

### **For End Users:**
> "A discreet wearable that always has your back—emergency help at the press of a button, with built-in evidence capture and smart threat detection."

### **For Guardians & Responders:**
> "Real-time command center for monitoring emergencies, reviewing evidence, and coordinating response with structured workflows and comprehensive audit trails."

### **For Organizations (Schools, Companies, NGOs):**
> "Deploy SafeRoute to protect your community with intelligent risk detection, scalable administration, and compliant evidence management."

---

## 🚀 Final Checklist Before Launch

- [ ] MVP features tested end-to-end in real conditions
- [ ] Security audit completed (encryption, RBAC, audit logs)
- [ ] Privacy policy and consent flows finalized
- [ ] Database schema normalized and indexed
- [ ] Notification delivery tested (push, SMS, email fallback)
- [ ] AI risk scores validated for false positive rate
- [ ] Admin dashboard tested with 1K concurrent users
- [ ] Wearable battery life meets 6+ hour target
- [ ] Evidence encryption and access control verified
- [ ] Team trained on responsible deployment
- [ ] Documentation complete and accessible
- [ ] Demo flow polished for stakeholder presentation

---

**Version:** 1.0  
**Last Updated:** 2026-07-13  
**Status:** Ready for Phase 1 Development