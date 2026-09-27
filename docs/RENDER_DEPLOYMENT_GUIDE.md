# SafeRoute Saheli — Render Deployment & PostgreSQL Setup Guide
## सेफरूट सहेली — Render Cloud Deployment & PostgreSQL Complete Manual

This comprehensive guide explains how to deploy the complete **SafeRoute Saheli** ecosystem (Python Flask Backend, PostgreSQL Database, and React Admin Operations Console) on **Render Cloud (render.com)**.

---

## 1. Ecosystem Architecture on Render

```
                             [ User Mobile App / Wearable ESP32 ]
                                              │
                                              ▼ HTTPS / WSS
[ Render Static Site ]  ──────────▶  [ Render Web Service ]  ──────────▶  [ Render Managed PostgreSQL ]
(React Admin Portal)                 (Flask Backend + WS)                (saferoute-saheli-db)
https://...-admin.onrender.com        https://...-backend.onrender.com     Version: PostgreSQL 16
```

---

## 2. Automated 1-Click Deployment via Blueprint (`render.yaml`)

We have created [`render.yaml`](file:///c:/Safe-Route-saheli/render.yaml) at the repository root. This automates the provisioning of:
1. **PostgreSQL 16 Database** (`saferoute-saheli-db`)
2. **Flask REST & WebSocket Service** (`saferoute-saheli-backend`)
3. **React Admin Portal** (`saferoute-saheli-admin`)

### Step-by-Step Instructions:

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "feat: configure PostgreSQL and Render Blueprint deployment"
   git push origin main
   ```

2. **Login to Render**:
   - Open [https://render.com](https://render.com) and sign in (using your GitHub account).

3. **Deploy via Blueprint**:
   - In the Render Dashboard, click the **New +** button in the top navigation.
   - Select **Blueprint**.
   - Select your GitHub repository (`Safe-Route-saheli`).
   - Render will automatically inspect [`render.yaml`](file:///c:/Safe-Route-saheli/render.yaml).

4. **Review & Apply**:
   - Render will show the 3 resources to be created:
     - `saferoute-saheli-db` (PostgreSQL Database)
     - `saferoute-saheli-backend` (Web Service)
     - `saferoute-saheli-admin` (Static Site)
   - Click **Apply**.
   - Render will automatically create the database, run `python backend/scripts/init_db.py` to create all 30+ tables, seed the superadmin account, and launch the backend and admin panel!

---

## 3. Manual Step-by-Step Deployment (Alternative)

If you prefer to create each service manually through the Render dashboard UI:

### Step 1: Create PostgreSQL Database
1. In Render Dashboard, click **New +** -> **PostgreSQL**.
2. **Name**: `saferoute-saheli-db`
3. **Database Name**: `saferoute_saheli`
4. **User**: `saheli_user`
5. **Region**: `Singapore` (or nearest region)
6. **Plan**: `Free`
7. Click **Create Database**.
8. Copy the **Internal Database URL** (e.g. `postgres://saheli_user:...@dpg-.../saferoute_saheli`).

### Step 2: Create Flask Backend Web Service
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Name**: `saferoute-saheli-backend`
   - **Region**: Same as database (e.g., `Singapore`)
   - **Branch**: `main`
   - **Runtime**: `Python`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && python backend/scripts/init_db.py`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`
   - **Plan**: `Free`
4. Add **Environment Variables**:
   | Variable | Value | Notes |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.9` | Recommended Python version |
   | `FLASK_ENV` | `production` | Enables production mode |
   | `DATABASE_URL` | *Select your Render DB connection string* | Auto-converted to `postgresql://` |
   | `SECRET_KEY` | *(Generate a random 32-char key)* | Session protection |
   | `JWT_SECRET` | *(Generate a random 32-char key)* | Mobile/admin JWT token signing |
   | `TEST_MODE` | `false` | Production mode |
5. Click **Create Web Service**.

### Step 3: Create React Admin Panel (Static Site)
1. Click **New +** -> **Static Site**.
2. Connect your GitHub repository.
3. Configure:
   - **Name**: `saferoute-saheli-admin`
   - **Branch**: `main`
   - **Build Command**: `cd admin_panel && npm install && npm run build`
   - **Publish Directory**: `./admin_panel/dist`
4. Add **Rewrite Rule** (for React Router SPA navigation):
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`
5. Click **Create Static Site**.

---

## 4. Default Seeded Accounts & Credentials

When `python backend/scripts/init_db.py` runs during deployment, it initializes the database schema and seeds:

* **Admin Operations Portal**:
  * **URL**: `https://saferoute-saheli-admin.onrender.com/login`
  * **Username**: `admin`
  * **Password**: `AdminSaheli@2026`

* **Demo Saheli User**:
  * **Email**: `priya.sharma@saheli.org`
  * **Password**: `PriyaSaheli@2026`
  * **Emergency Contact**: `Rajesh Sharma (Father) - +919811122233`

* **Verified Safe Places**:
  * Delhi Police Headquarters (24x7)
  * AIIMS Trauma Center (24x7)
  * Apollo Pharmacy (24x7)
  * Delhi Commission for Women Shelter (181)

* **Geo-Fence Safe Havens**:
  * IIT Delhi Campus (Curfew: 22:30 - 06:00, 120s GPS battery saver)
  * Cyber City IT Park (Curfew: 21:00 - 07:00, 120s GPS battery saver)

---

## 5. Mobile App & IoT Hardware Configuration

### Connecting the Flutter App:
Open `flutter_app/lib/config/app_config.dart` or `.env` and set:
```dart
static const String baseUrl = 'https://saferoute-saheli-backend.onrender.com';
static const String socketUrl = 'https://saferoute-saheli-backend.onrender.com';
```

### Building the Android APK:
Now that the Android platform files and permissions have been generated, build your APK anytime with:
```bash
cd flutter_app
flutter build apk --release
```
The output APK will be generated at: `flutter_app/build/app/outputs/flutter-apk/app-release.apk`.

### Connecting ESP32 Wearable Device:
In `firmware/esp32/src/config.h`:
```cpp
#define SERVER_HOST "saferoute-saheli-backend.onrender.com"
#define SERVER_PORT 443
#define USE_SSL     true
```

---

## 6. Important Render & PostgreSQL Gotchas Handled

1. **SQLAlchemy `postgres://` to `postgresql://` conversion**:
   Render provides connection strings prefixed with `postgres://`, which breaks in SQLAlchemy 1.4+. SafeRoute Saheli's [`backend/config.py`](file:///c:/Safe-Route-saheli/backend/config.py) automatically sanitizes this prefix on boot.
2. **WebSocket & Gunicorn with Eventlet**:
   The start command uses `--worker-class eventlet -w 1` to support concurrent WebSocket rooms for live guardian streaming and emergency dispatch.
3. **Render Free Tier Sleep Handling**:
   Free web services sleep after 15 minutes of inactivity. When a request arrives, Render automatically spins it up in ~30 seconds. To keep it awake 24x7, you can set a free cron ping (e.g. via UptimeRobot or Cron-Job.org) to `https://saferoute-saheli-backend.onrender.com/api/health` every 10 minutes.
