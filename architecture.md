# 🏛️ SafeRoute Saheli Architecture

> **Four-layer ecosystem for connected safety, from wearable to responder**

---

## 🎯 **1. System Layers**

```
┌─────────────────────────────────────────────────────┐
│              Admin Dashboard (React)                 │
│     Real-time incident monitoring & escalation      │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket
┌────────────────────▼────────────────────────────────┐
│    Backend API (Node.js/Express + PostgreSQL)      │
│  Authentication, routing, AI, notifications, logs  │
└──┬──────────────┬──────────────┬────────────────────┘
   │              │              │
   │ REST/Socket  │ REST/Socket  │ WebSocket
   │              │              │
┌──▼─────┐   ┌───▼──────┐  ┌────▼────────┐
│ Flutter │   │ Object   │  │ PostgreSQL  │
│  App    │   │ Storage  │  │  Database   │
│ (iOS/   │   │  (S3)    │  │             │
│Android) │   │          │  └─────────────┘
└────▲────┘   └──────────┘
     │
     │ BLE
     │
┌────▼──────────┐
│ ESP32 Wearable│
│  (Trigger,    │
│   Camera,     │
│   Microphone) │
└───────────────┘
```

---

## 📊 **2. Data Flow Architecture**

### **Normal Mode (Monitoring)**
```
Wearable (low power)
    ↓ [BLE periodic ping - every 30s]
Flutter App (background location)
    ↓ [Location update - every 1 min in trip mode]
Backend API (queues location in PostgreSQL)
    ↓ [Periodic risk scoring - every 5 min]
React Dashboard (live map with breadcrumb trail)
    ↓ [WebSocket push to guardians - real-time]
Trusted Contacts (see live location on their app)
```

### **Emergency Mode (SOS Activated)**
```
Wearable or App (SOS pressed)
    ↓ [Instant trigger]
Flutter App (captures GPS, creates incident)
    ↓ [Priority HTTP POST to backend]
Backend API (stores incident, starts evidence pipeline)
    ├─ Push Notification (to guardians - <1s)
    ├─ SMS Notification (fallback - <5s)
    ├─ Email Notification (confirmation - <30s)
    └─ Evidence capture request (camera, audio ready)
    ↓
React Dashboard (live incident appears, auto-center map)
    ↓
Responders see incident with location, user context, evidence

---

## 📸 **3. Evidence Capture & Storage Pipeline**

```
SOS Triggered
    ↓
Wearable: Camera + Microphone "wake up"
    ↓ [5-30 second burst]
App: Buffers media in temporary directory
    ↓
[Network available?]
    ├─ YES: Immediate upload to backend
    └─ NO: Local queue (sync when network returns)
    ↓
Backend: Receive multipart form-data (file + metadata)
    ├─ Validate file type & size
    ├─ Encrypt file with AES-256
    ├─ Upload to S3-compatible storage
    ├─ Generate file hash (SHA-256)
    └─ Return signed URL (1hr TTL)
    ↓
PostgreSQL: Store metadata only
    ├─ incident_id (foreign key)
    ├─ file_name, file_path (S3 key)
    ├─ file_hash (integrity check)
    ├─ captured_at, upload_status
    └─ access_level (who can view)
    ↓
React Dashboard: Show evidence in incident detail
    ├─ Access logged (audit trail)
    ├─ Download via signed URL (auto-expires)
    └─ Export option (PDF report generation)
```

**Security Notes:**
- ✅ Media never stored in PostgreSQL (only S3)
- ✅ Encryption key rotated quarterly
- ✅ Every download logged with timestamp, user, IP
- ✅ Signed URLs expire after 1 hour (can't be reused)
- ✅ Retention policy: auto-delete after 90 days (unless extended by admin)

---

## 🏗️ **4. Component Architecture**

### **4.1 Wearable IoT Layer (ESP32)**
**Sensors & Actuators:**
- 📟 **ESP32-S3 microcontroller** (Wi-Fi + BLE)
- 🔘 **Mechanical button** (trigger activation)
- 📷 **OV2640 camera** (image capture)
- 🎤 **MEMS microphone** (audio recording)
- 🧠 **MPU6050 IMU** (fall/struggle detection)
- 📳 **Vibration motor** (haptic feedback)
- 🔋 **Li-Po battery** (1-3Ah, 6-8hr runtime)

**Firmware Responsibilities:**
```
┌─────────────────────────────┐
│   ESP32 Firmware            │
├─────────────────────────────┤
│ ✅ BLE pairing with app     │
│ ✅ Button debouncing        │
│ ✅ Voice command detection  │
│ ✅ Camera/mic recording     │
│ ✅ Motion anomaly detection │
│ ✅ Deep sleep management    │
│ ✅ Buffering (offline mode) │
└─────────────────────────────┘
```

---

### **4.2 Mobile App Layer (Flutter)**

```
┌──────────────────────────────────────────┐
│         User Interface (Flutter)          │
├──────────────────────────────────────────┤
│ • Splash & Onboarding                    │
│ • Home Dashboard                         │
│ • Trip Mode (tracking)                   │
│ • SOS & Emergency Screens                │
│ • Evidence Upload                        │
│ • Digital Abuse Reporting                │
│ • Settings & Profile                     │
├──────────────────────────────────────────┤
│       State Management (GetX/Riverpod)   │
├──────────────────────────────────────────┤
│    Business Logic & Services             │
│ ├─ Auth Service (JWT tokens)             │
│ ├─ Device Service (BLE manager)          │
│ ├─ Location Service (GPS, permissions)   │
│ ├─ Alert Service (SOS routing)           │
│ ├─ Camera/Audio Service (recording)      │
│ ├─ Notification Handler (FCM)            │
│ └─ Local DB (SQLite for offline queue)   │
├──────────────────────────────────────────┤
│         Network & Security               │
│ ├─ REST API client (HTTP, SSL pinning)   │
│ ├─ BLE communication (encrypted)         │
│ ├─ Token refresh logic                   │
│ └─ Encryption (sensitive data at rest)   │
└──────────────────────────────────────────┘
```

---

### **4.3 Backend API Layer (Node.js/Express)**

```
┌──────────────────────────────────────────┐
│      Express HTTP Server                 │
├──────────────────────────────────────────┤
│  Middleware Layer:                       │
│  ├─ JWT auth verification                │
│  ├─ CORS & rate limiting                 │
│  ├─ Request logging (Morgan)             │
│  ├─ Error handling                       │
│  └─ Helmet (security headers)            │
├──────────────────────────────────────────┤
│        REST API Routes                   │
│  /auth ────→ Authentication Service      │
│  /users ───→ User Profile Service        │
│  /devices ─→ Device Pairing Service      │
│  /trips ───→ Trip Tracking Service       │
│  /alerts ──→ SOS Alert Service           │
│  /incidents→ Incident Management Service │
│  /evidence→ Evidence Storage Service     │
│  /reports ─→ Digital Abuse Service       │
│  /admin ───→ Admin Management Service    │
│  /analytics→ Analytics & BI Service      │
├──────────────────────────────────────────┤
│       Business Logic Services            │
│  ├─ Risk Scoring Engine (AI/ML)         │
│  ├─ Stalking Detection (multi-signal)    │
│  ├─ Digital Abuse Classifier (ML)        │
│  ├─ Route Prediction (geospatial)        │
│  └─ Incident Escalation Engine           │
├──────────────────────────────────────────┤
│      Data Layer (ORM)                    │
│  ├─ PostgreSQL connection pool           │
│  ├─ Sequelize/TypeORM models             │
│  ├─ Query optimization & caching         │
│  └─ Migration management                 │
├──────────────────────────────────────────┤
│    External Integrations                 │
│  ├─ Firebase Cloud Messaging (push)      │
│  ├─ Twilio (SMS)                         │
│  ├─ SendGrid (email)                     │
│  ├─ AWS S3 (media storage)               │
│  ├─ Google Maps (routing)                │
│  └─ Redis (caching, sessions)            │
└──────────────────────────────────────────┘
```

---

### **4.4 Admin Dashboard (React)**

```
┌──────────────────────────────────────────┐
│      React 18 Component Tree             │
├──────────────────────────────────────────┤
│  ├─ Auth Layout (login)                  │
│  ├─ Main Dashboard Layout                │
│  │  ├─ Header (user, notifications)      │
│  │  ├─ Sidebar (navigation)              │
│  │  └─ Content (dynamic by route)        │
│  │     ├─ Incident Command Center        │
│  │     ├─ Live Map View                  │
│  │     ├─ User Management               │
│  │     ├─ Device Inventory              │
│  │     ├─ Evidence Viewer               │
│  │     ├─ Analytics Dashboard           │
│  │     ├─ Role Management               │
│  │     └─ Audit Logs                    │
├──────────────────────────────────────────┤
│      State Management (Redux Toolkit)    │
│  ├─ Auth state (user, token, permissions)
│  ├─ Incident state (list, detail, filters)
│  ├─ User state (directory)               │
│  ├─ Map state (zoom, center, markers)    │
│  ├─ Notification state (real-time)       │
│  └─ UI state (modals, sidebars)         │
├──────────────────────────────────────────┤
│        API Integration (Axios)           │
│  └─ REST client with auth header         │
│  └─ WebSocket listener (Socket.IO)       │
├──────────────────────────────────────────┤
│     Libraries & Utils                    │
│  ├─ Material-UI v5 (components)          │
│  ├─ Recharts (analytics charts)          │
│  ├─ Leaflet (map visualization)          │
│  ├─ date-fns (time formatting)           │
│  ├─ formik + yup (form validation)       │
│  └─ TypeScript (type safety)             │
└──────────────────────────────────────────┘
```

---

## 🚀 **5. Deployment Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                     Cloud Infrastructure                     │
├─────────────────────────────────────────────────────────────┤
│  AWS / DigitalOcean / Google Cloud / On-Premise             │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │  Docker Compose  │  │  Kubernetes      │  │ Terraform │  │
│  │  (development)   │  │  (production)    │  │ (IaC)     │  │
│  └──────────────────┘  └──────────────────┘  └───────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Container Image Registry (DockerHub)        │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ • node:18-alpine (backend)                          │    │
│  │ • node:18-alpine (admin dashboard)                  │    │
│  │ • postgis/postgis (database)                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │  App Server    │  │  App Server    │  │ Load Balancer│   │
│  │ (Express:3000) │  │ (Express:3000) │  │  (nginx)     │   │
│  └────────────────┘  └────────────────┘  └──────────────┘   │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │   PostgreSQL (RDS / Managed Instance)               │    │
│  │   • Replication (master-slave)                      │    │
│  │   • Automated backups (daily)                       │    │
│  │   • Point-in-time recovery (30 days)                │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │    AWS S3 / MinIO (Object Storage)                │       │
│  │    • Media files (images, audio, video)           │       │
│  │    • Lifecycle policy (90-day auto-delete)        │       │
│  │    • Encryption at rest (AES-256)                 │       │
│  │    • Versioning (immutable evidence)              │       │
│  └──────────────────────────────────────────────────┘       │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │     CDN (CloudFront / Bunny)                      │       │
│  │     • Static assets caching                       │       │
│  │     • DDoS protection                             │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘

Mobile Apps (Flutter):
• Google Play Store (Android)
• Apple App Store (iOS)
• Update via app store (OTA updates)
```

---

## 🔒 **6. Security Architecture**

```
┌──────────────────────────────────────────────────────────┐
│              User Request Layer                          │
├──────────────────────────────────────────────────────────┤
│                HTTPS/TLS 1.3 (enforced)                 │
│              Certificate Pinning (mobile)               │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│           API Gateway / Load Balancer                    │
├──────────────────────────────────────────────────────────┤
│ • Rate limiting (100 req/min per IP)                    │
│ • Request validation (size limits)                      │
│ • IP whitelist (if needed)                             │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│         Express Middleware (Security Layer)             │
├──────────────────────────────────────────────────────────┤
│ • Helmet (security headers)                            │
│ • CORS (controlled origins)                            │
│ • JWT verification (on every request)                  │
│ • Request logging (audit trail)                        │
│ • SQL injection prevention (parameterized queries)     │
│ • XSS protection (input sanitization)                  │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│         Authorization Layer (RBAC)                       │
├──────────────────────────────────────────────────────────┤
│ Roles:                                                  │
│ • user (self only)                                     │
│ • guardian (view assigned users)                       │
│ • operator (all incidents, no delete)                  │
│ • admin (all operations, audit logs)                   │
│ • super_admin (system configuration)                   │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│       Data Encryption & Storage Security                 │
├──────────────────────────────────────────────────────────┤
│ At Rest:                                                │
│ • Passwords: bcrypt (12 rounds)                        │
│ • API Keys: encrypted in env + vault                   │
│ • Evidence: AES-256 in S3                              │
│ • Backup: encrypted daily                              │
│                                                         │
│ In Transit:                                             │
│ • TLS 1.3 (100% enforcement)                           │
│ • no HTTP (automatic HTTPS redirect)                   │
│ • Certificate: wildcard or multi-SAN                   │
└─────────────────────────────────────────────────────────┘
```

**Authentication Flow:**
```
User Input (email + password)
         ↓
POST /auth/login
         ↓
Hash comparison: bcrypt.compare(input, stored_hash)
         ↓
Generate JWT: sign({ user_id, role, exp: 15min }, secret)
         ↓
Return: { access_token, refresh_token (7d) }
         ↓
Client stores in secure storage (not localStorage)
         ↓
Every request: Authorization: Bearer <token>
         ↓
Middleware verifies JWT signature & expiration
```

---

## 🤖 **7. AI/ML Architecture**

### **Processing Location Strategy**

| Model | Location | Latency | Use Case |
|---|---|---|---|
| **Wake-word detection** | On-device (wearable) | Real-time | "Hey Saheli" activation |
| **Motion anomaly** | On-device (wearable) | Real-time | Fall/struggle detection |
| **Risk scoring** | Backend (serverless) | <500ms | Every location update |
| **Digital abuse classifier** | Backend (ML service) | <2s | User-triggered import |
| **Route prediction** | Backend (cache + ML) | <1s | Trip start + periodic updates |

### **Model Serving**

```
Backend ML Pipeline
├─ Flask/FastAPI microservice (dedicated port 5000)
├─ Model loading at startup (cache in memory)
├─ Input validation (numpy arrays)
├─ Batch prediction (where applicable)
├─ Output formatting (confidence scores, explanations)
└─ Logging (predictions for retraining feedback)
```

---

## 📈 **8. Scalability Design**

| Component | Strategy | Limit |
|---|---|---|
| **Database** | Connection pooling (20-100 connections) | Vertical scaling, read replicas at 10K users |
| **Backend API** | Horizontal scaling (Docker, auto-scaling) | 100+ instances for 1M users |
| **Real-time** | Socket.IO with Redis adapter | 10K concurrent connections per server |
| **Media Storage** | S3 unlimited, CloudFront CDN | Automatic scaling, no limits |
| **Notifications** | Queuing (RabbitMQ, AWS SQS) | 10K+ notifications/sec |
| **Analytics** | Periodic aggregation, caching | Pre-computed dashboards updated every 5min |

---

## 💪 **9. Reliability & Failover**

```
┌─ API Server Down?
│  └─ Health check fails → Auto-restart + alert
│
├─ Database Down?
│  └─ Failover to read replica → Cache returns
│
├─ S3 Down?
│  └─ Retry logic + fallback to CDN cache
│
├─ Notification Service Down?
│  └─ Queue to message broker + retry (exponential backoff)
│
├─ Network Disconnect (mobile)?
│  └─ Local buffering → Sync when online
│
└─ Wearable Offline?
   └─ Last-known location shown → Tamper alert if >5min
```

---

## 🔐 **10. Privacy by Design**

| Principle | Implementation |
|---|---|
| **Data Minimization** | Only collect: name, phone, email, location (when in trip) |
| **Purpose Limitation** | Evidence used only for incident documentation |
| **Consent** | Explicit opt-in for camera/mic + audit logging |
| **Transparency** | "View access log" link in evidence detail screen |
| **Retention** | Auto-delete evidence after 90 days |
| **Portability** | User can export all personal data as JSON/CSV |
| **Right to Delete** | Soft delete, 30-day grace period before permanent |
| **Anonymization** | Analytics aggregate (never individual tracking) |

**Privacy Audit Checklist:**
- ✅ No correlation across users
- ✅ No location history retained beyond 90 days
- ✅ No consent override (camera always requires confirmation)
- ✅ No third-party data sharing (unless user explicitly shares)
- ✅ No behavioral targeting or profiling