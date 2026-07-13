# 🛡️ SafeRoute Saheli

> **An AIoT-powered Women’s Safety & Emergency Response Ecosystem**

SafeRoute Saheli is a comprehensive women’s safety platform that combines **AI**, **IoT**, **real-time communication**, and **mobile technology** to provide rapid emergency assistance, intelligent risk detection, and secure evidence management.

The ecosystem consists of:
- 📟 A discreet IoT wearable safety device
- 📱 A Flutter mobile application
- 🖥️ A React web admin dashboard
- ⚙️ A Node.js/Express backend with PostgreSQL

---

## ✨ Features

### 🚨 Emergency Response
- One-tap SOS activation
- Silent emergency alerts
- Live location sharing
- Multi-level emergency escalation
- Push notifications (FCM)
- SMS & Email notifications

### 🤖 AI-Powered Safety
- Route risk scoring
- Suspicious pattern detection
- AI-based risk engine
- Safety score generation

### 📸 Evidence Management
- Secure image, audio & video capture
- Cloud object storage
- Timestamped incident evidence
- Digital abuse reporting

### 👩‍💼 Admin Dashboard
- Live incident monitoring
- SOS management
- Escalation workflow
- Evidence review
- Analytics dashboard

---

# 🏗️ Architecture

```text
              IoT Wearable
                    │
                    ▼
          Flutter Mobile App
                    │
                    ▼
      Node.js / Express Backend
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 PostgreSQL    Object Storage   Socket.IO
                    │
                    ▼
         React Admin Dashboard
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Mobile | Flutter |
| Web | React |
| Backend | Node.js + Express |
| Database | PostgreSQL |
| Real-Time | Socket.IO / WebSocket |
| Maps | Leaflet / Mapbox |
| Storage | S3-Compatible Storage |
| Notifications | Firebase Cloud Messaging, SMS, Email |

---

## 📦 Core Modules

- 📟 Wearable Device Module
- 📱 Mobile App Module
- 🖥️ Admin Dashboard
- 🔗 Backend REST APIs
- 🤖 AI/ML Risk Engine
- 📂 Evidence Management
- 🚨 Notification & Escalation
- 📊 Incident Analytics
- 📍 Live Tracking
- 🛡️ Digital Abuse Reporting

---

## 🎯 Project Goals

- Improve women's personal safety
- Enable rapid emergency response
- Capture secure incident evidence
- Detect suspicious patterns using AI
- Assist administrators in emergencies
- Support digital abuse documentation

---

## 📁 Repository Structure

```text
SafeRoute-Saheli/
│
├── project-scope.md
├── architecture.md
├── database-schema.md
├── screens-list.md
├── README.md
```

---

## 🔒 Privacy & Ethics

SafeRoute Saheli is designed as an **emergency safety and evidence-support platform**.

It is intended to:

- Assist users during emergencies
- Improve emergency response
- Securely preserve evidence
- Support responsible incident documentation

**It is NOT designed for covert surveillance, unauthorized monitoring, or misuse of personal data.**

---

## 🚀 Future Enhancements

- Smartwatch support
- Offline SOS
- Voice distress detection
- Emergency contact prioritization
- Crime heatmaps
- Government emergency integration
- Safe Zone recommendations
- Multilingual support

---

## 📚 Documentation

This repository includes:

- 📘 `project-scope.md`
- 🏗️ `architecture.md`
- 🗄️ `database-schema.md`
- 📱 `screens-list.md`

---

## ❤️ Vision

> **"Technology should not only connect people—it should protect them."**

SafeRoute Saheli combines **AI**, **IoT**, and **real-time communication** to build a safer future through intelligent emergency response and responsible technology.

---

## 📄 License

This project is intended for educational, research, and humanitarian purposes. Any real-world deployment should comply with applicable privacy, security, and legal requirements.