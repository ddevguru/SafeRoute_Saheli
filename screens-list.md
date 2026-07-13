# 📱 SafeRoute Saheli Mobile & Web Screens

> **Complete screen flow for Flutter mobile app and React admin dashboard**

---

## 🔓 **1. Onboarding & Authentication (Public Screens)**

### User App (Flutter)

| Screen | Purpose | Actions |
|--------|---------|---------|
| 🚀 **Splash Screen** | App startup, branding | Auto-load (2s) → Home if logged in, else Login |
| 📖 **Welcome Carousel** | Feature showcase (3-5 cards) | ← → swipe, Skip button, Start button |
| 📋 **Privacy Notice** | Legal consent | Accept → Continue, Decline → Exit |
| 🔐 **Login Screen** | Email/phone + password entry | Sign up link, Forgot password link, Login button |
| ✍️ **Registration** | New user signup with email/phone | Password strength meter, Terms checkbox, Register button |
| 📱 **OTP Verification** | 6-digit code verification | Resend SMS link, Paste from clipboard, Verify button |
| 🔑 **Forgot Password** | Email recovery flow | Email input, Send OTP button, Verify & Reset link |
| ✏️ **Create New Password** | Set new secure password | Password requirements, Set password button |

---

## 👤 **2. User Onboarding & Setup**

| Screen | Purpose | Actions |
|--------|---------|---------|
| 👤 **Profile Setup** | Name, age, address, photo | Edit fields, Save profile |
| 📞 **Emergency Contacts** | Add trusted people to contact | +Add contact, Search contacts, Edit priority |
| 🛡️ **Trusted Guardians** | Approve specific guardians | Invite guardian, Accept/Deny requests |
| 📍 **Location Permissions** | Request location access | Always, Only while using app, Don't allow |
| 📟 **Wearable Pairing** | Scan QR code or manual entry | Scan QR, Pair device, Test connection |
| ⚙️ **Safety Preferences** | Risk alerts, notification settings | Enable/disable alerts, Adjust sensitivity |

---

## 🏠 **3. Home & Dashboard Screens**

| Screen | Purpose | Key Elements |
|--------|---------|--------------|
| **Main Dashboard** | Overview of safety status | Safety score gauge (0-100), Quick SOS button, Device status, Last incident summary, Safety tips |
| **Safety Score Gauge** | Visual risk indicator | Color-coded (green=safe, red=danger), Score breakdown (route, time, device) |
| **Device Status Widget** | Wearable health | Battery %, Connection status, Last ping time, Device name |
| **Quick SOS Button** | Large red button for panic | Tap-and-hold (2s) to activate, Visual countdown, Cancel option |
| **Silent SOS** | Discreet activation (no alarm) | Tap once, Vibration only, No sound, Escalates silently |
| **Trip Mode Toggle** | Start continuous tracking | On/Off toggle, Destination input, ETA display |
| **Notification Inbox** | View recent alerts | List of notifications, Mark as read, Delete old |

---

## 🗺️ **4. Navigation & Location Screens**

| Screen | Purpose | Interactions |
|--------|---------|--------------|
| **Live Map View** | Real-time location tracking | Pan/zoom map, Breadcrumb trail, Marker for user location |
| **Safe Route Suggestion** | AI-recommended safer path | Route A (fast) vs Route B (safer), Tap to navigate, Share route |
| **Route History** | Past trips with analytics | Calendar view, Tap trip → detail, Risk overlay |
| **Unsafe Zone Heatmap** | Incident density visualization | Color gradient (red=more incidents), Zoom to location |
| **Trip Details** | Full breakdown of one trip | Duration, distance, stops, risk score, evidence captured |

---

## 📸 **5. Evidence & Incident Screens**

| Screen | Purpose | Functionality |
|--------|---------|--------------|
| **Incident Timeline** | Chronological incident list | Tap → detail, Filter by type, Export as PDF |
| **Audio Evidence Viewer** | Play audio recordings | Play button, Progress bar, Download, Share |
| **Image Evidence Gallery** | View screenshots/photos | Pinch zoom, Swipe gallery, Full-screen view |
| **Video Evidence Player** | Watch emergency videos | Play controls, Progress scrubber, Caption toggle |
| **Evidence Upload** | Send files manually | Camera capture, Photo library, Audio record, Drag-drop |
| **Evidence Detail** | Metadata + full context | Timestamp, location, file size, downloader audit log |

---

## 🛡️ **6. Digital Abuse Module**

| Screen | Purpose | Features |
|--------|---------|----------|
| **Report Abuse** | Create new abuse case | Screenshot import, Message link, Platform selection |
| **Abuse Category** | Auto-tag abuse type | Harassment, Threat, Impersonation, Blackmail, Obscene |
| **Screenshot Import** | Load image for classification | Gallery import, Camera capture, Paste from clipboard |
| **Abuse Timeline** | Case chronology | Incident list, Add note, Add evidence |
| **Export Report** | Generate shareable PDF | Platform template, Police format, Share link |

---

## ⚙️ **7. Settings & Control Center**

| Screen | Purpose | Options |
|--------|---------|---------|
| **Account Settings** | Profile & auth mgmt | Change email, Change password, Phone number, Delete account |
| **Privacy Settings** | Data & permission control | Location sharing, Camera access, Microphone access, Data export |
| **Notification Settings** | Alert preferences | Push enabled, SMS enabled, Sound toggle, Quiet hours |
| **Device Settings** | Wearable management | Rename device, Unpair device, Firmware update, Signal test |
| **Language Settings** | Localization | English, Hindi, Marathi, Tamil, etc. |
| **Help & Support** | FAQs & contact | FAQ search, Email support, Call support, In-app tutorial |
| **About App** | Version & credits | Version number, Build ID, Privacy policy, Terms of service |

---

## 🚨 **8. Emergency Workflow Screens**

| Screen | Trigger | Purpose | Flow |
|--------|---------|---------|------|
| **SOS Confirmation** | User presses SOS | Countdown timer (10s) | ← Cancel, → Confirm escalation |
| **Emergency Mode Active** | Confirmed SOS | Show "Help coming" + tracking | Auto-start camera/audio, Show live location |
| **Alert Sent Success** | Escalation complete | Confirmation message | Guardians notified: ✓ Push ✓ SMS ✓ Email |
| **Help Accepted** | Guardian confirmed | "Responder is on way" | Show responder ETA, Live chat option |
| **Live Rescue Tracking** | During emergency | Map + direction to responder | Auto-center on helper location |
| **Cancel Emergency** | User changing mind | Confirmation dialog | Notify cancellation to all |

---

## 👨‍💼 **9. Admin Dashboard (React Web)**

### **Authentication**

| Screen | Purpose | Actions |
|--------|---------|---------|
| **Admin Login** | Role-based access | Email + password, 2FA (OTP), Remember me checkbox |

### **Main Dashboard & Navigation**

```
┌─────────────────────────────────────────┐
│  Header: SafeRoute Admin | User | Logout │
├─────────────────────────────────────────┤
│ Sidebar │         Main Content Area    │
│ ├─ Dashboard                           │
│ ├─ Live Incidents                      │
│ ├─ Users & Devices                     │
│ ├─ Evidence Viewer                     │
│ ├─ Analytics                           │
│ ├─ Settings                            │
│ └─ Audit Logs                          │
└─────────────────────────────────────────┘
```

### **Core Admin Screens**

| Screen | Purpose | Components |
|--------|---------|-----------|
| **Dashboard Overview** | Real-time command center | KPI cards (active incidents, SOS today), Live incident queue, Map widget, Alert trends chart |
| **Live Incidents** | Sortable incident list | Table: user, incident type, severity, status, timestamp | Sort by severity, Filter by status, Search by user email |
| **Incident Detail** | Full case context | User info, Location map, Evidence gallery, Timeline, Escalation buttons (Assign, Close, Resolve) |
| **User Management** | User directory & roles | List with search, Filter by role, Bulk role assignment, User detail drawer |
| **Device Management** | Wearable inventory | Device list: UUID, model, firmware, battery, status | Revoke device, Force update, Remote lock |
| **Role Management** | Access control admin | Create role, Assign permissions, View permission matrix, Audit role changes |
| **Evidence Viewer** | Secure media playback | Image carousel, Audio player, Video player, Download with audit log, Blur sensitive areas |
| **Audit Logs** | Complete action history | Searchable log: who, what, when, IP address | Filter by action type, Export to CSV |

### **Analytics & Reporting**

| Screen | Visualization | Metrics |
|--------|---|---|
| **Risk Heatmap** | Map with incident density | Incident count by location, Time-of-day overlay, Neighborhood risk ranking |
| **SOS Response Stats** | Charts & KPIs | Response time (avg, min, max), Success rate %, Escalation breakdown |
| **Trends Dashboard** | Line charts | Incidents per day (7d, 30d), SOS triggers trend, Device usage pattern |
| **Reports Generator** | Export options | Date range picker, Format (PDF, CSV, JSON), Email schedule |

---

## 📊 **10. Screen Flow Diagrams**

### **Normal Mode (Monitoring)**

```
Splash → Login → Dashboard
                    ↓
         Home Dashboard
         ├─ Safety Score
         ├─ Device Status
         ├─ Trip Mode Toggle
         └─ Notification Inbox
              ↓
    Profile → Settings → Help
    Trip Map → Route History
    Contacts → Abuse Reporting
```

### **Emergency Mode (SOS)**

```
Panic Moment
    ↓
[Wearable Button or App SOS] → SOS Confirmation Screen (10s countdown)
    ↓
[CONFIRMED] → Emergency Mode Screen (live tracking + evidence capture)
    ↓
[Alert Sent] → Success Screen (responders notified, ETA shown)
    ↓
[Help Arrived] → Rescue Tracking Screen (live location of responder)
    ↓
[Emergency Resolved] → Post-Incident Summary (incident saved, evidence uploaded)
```

---

**Screen Count Summary:**
- 📱 User App: ~35 screens
- 🖥️ Admin Dashboard: ~15 screens
- 🔑 Total: ~50 unique screens

**Last Updated:** 2026-07-13