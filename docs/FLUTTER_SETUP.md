# SafeRoute Saheli — Flutter Mobile Application Setup & Architecture Guide

## 1. Overview
The SafeRoute Saheli mobile application is a production-grade personal safety client built using **Flutter (Dart 3+)** and **BLoC (Business Logic Component)** architecture. It serves two distinct user roles:
1. **Saheli (Primary User)**: Initiates emergency workflows, monitors wearable IoT sensor telemetry, explores AI-optimized safe routes, and configures privacy parameters.
2. **Guardian**: Monitors authorized wards, checks live status, streams authorized ESP32-CAM video feeds, and views real-time GPS locations during emergencies.

---

## 2. Clean Architecture Structure

```
flutter_app/
├── lib/
│   ├── blocs/                 # BLoC state management (AuthBloc, EmergencyBloc)
│   ├── config/                # Environment and timing constants (AppConfig)
│   ├── constants/             # Design tokens and color palettes (AppColors)
│   ├── core/                  # Core abstractions and error handlers
│   ├── models/                # Strongly-typed data models (User, Guardian, SafePlace, RouteOption, EmergencyIncident)
│   ├── notifications/         # Firebase Cloud Messaging & local notifications handler
│   ├── repositories/          # Data access layer (Auth, Emergency, Guardian, Routing)
│   ├── routes/                # Declarative named routing registry (AppRoutes)
│   ├── screens/               # 14 Full UI screens covering all product requirements
│   │   ├── splash_screen.dart
│   │   ├── onboarding_screen.dart
│   │   ├── login_screen.dart
│   │   ├── register_screen.dart
│   │   ├── forgot_password_screen.dart
│   │   ├── home_dashboard_screen.dart
│   │   ├── active_emergency_screen.dart
│   │   ├── guardians_management_screen.dart
│   │   ├── guardian_dashboard_screen.dart
│   │   ├── live_camera_screen.dart
│   │   ├── safe_route_screen.dart
│   │   ├── nearby_help_screen.dart
│   │   ├── emergency_history_screen.dart
│   │   └── privacy_settings_screen.dart
│   ├── services/              # HTTP, WebSocket & REST communication (ApiService)
│   ├── storage/               # Encrypted device storage (SecureStorageService)
│   ├── theme/                 # Typography, button themes, and dark/light palettes (AppTheme)
│   ├── utils/                 # Formatting and calculation utilities
│   ├── widgets/               # Reusable UI widgets (EmergencyButton, StatusOverviewCard, QuickActionTile, NearbyPlaceCard)
│   └── main.dart              # MultiRepositoryProvider & MultiBlocProvider app bootloader
└── test/
    ├── widget_test.dart       # Splash and onboarding boot integration tests
    └── components_test.dart   # Core UI widget unit and interaction tests
```

---

## 3. Brand Identity & Design System

The application strictly adheres to the SafeRoute Saheli design specification:
- **Primary Color**: `#002350` (Deep Midnight Blue)
- **Secondary Color**: `#D2AE39` (Warm Protective Gold)
- **Background**: `#F5F7FA` (Soft Off-White Slate)
- **Card Surface**: `#FFFFFF` (Pure Crisp White)
- **Emergency Crimson**: `#DC2626`
- **Warning Amber**: `#F59E0B`
- **Success Emerald**: `#10B981`
- **Feminine & Protective**: Rounded corners (16-18px), soft elevated box shadows, high contrast typography, accessible touch targets, and zero childish tropes.

---

## 4. Screen Inventory & Features

| Screen | Route | Description |
|---|---|---|
| **Splash** | `/` | Animated logo, scale/fade transitions, tagline, automated auth-check routing. |
| **Onboarding** | `/onboarding` | 4-step walkthrough: Wearable device, Instant emergency alerts, Guardian connectivity, AI safe routes. |
| **Login** | `/login` | Dual-tab authentication for Saheli and Guardian with token storage. |
| **Register** | `/register` | Saheli signup with complete personal, contact, and optional medical fields. |
| **Forgot Password**| `/forgot-password`| Multi-step OTP recovery with countdown timer and password reset. |
| **Home Dashboard** | `/home` | Greeting, device telemetry status card, 2.5s press-and-hold Emergency Button, 6 quick actions. |
| **Active Emergency**| `/active-emergency`| High-priority alert state, live dispatch logs, nearest help cards, revocable tracking link, cancel confirmation dialog. |
| **Guardians Hub** | `/guardians` | Add guardian form, relationship assignment, live permission management (Camera/Location). |
| **Guardian Portal**| `/guardian-dashboard`| Monitored wards status cards, battery level, live location streaming, authenticated video feed launcher. |
| **Live Camera** | `/live-camera` | Authenticated ESP32-CAM stream preview, snapshot trigger, latency indicator, audit logging disclaimer. |
| **Safe Route** | `/safe-route` | AI route comparison: Shortest, Fastest, and Neuro-Fuzzy Safety-Optimized route with risk factors. |
| **Nearby Help** | `/nearby-help` | Filterable nearest Police Stations, Hospitals, and Safe Places with distance, navigation, and direct call actions. |
| **History & Evidence**| `/emergency-history`| Comprehensive incident logs with bottom sheet evidence dossier (Audio, Snapshots, Video, GPS, Call logs). |
| **Privacy Settings**| `/privacy-settings`| Granular user control over camera permissions, audio recording, location sharing, clap/voice triggers, and cancel phrase. |

---

## 5. Development & Testing Commands

### Prerequisites
- Flutter SDK `3.10.0` or higher
- Dart SDK `3.0.0` or higher

### Install Dependencies
```bash
cd flutter_app
flutter pub get
```

### Static Analysis
```bash
flutter analyze
```
*Expected Output: `No issues found!`*

### Run Automated Tests
```bash
flutter test
```
*Expected Output: `All tests passed!` (Checks splash transition, onboarding flow, and core UI widget components).*

### Run Application
- **Windows Desktop**:
  ```bash
  flutter run -d windows
  ```
- **Chrome Web Browser**:
  ```bash
  flutter run -d chrome
  ```
- **Android Emulator**:
  ```bash
  flutter run -d emulator-id
  ```
  *(Note: For Android Emulator, `AppConfig.setAndroidEmulatorHost()` points to `10.0.2.2:5000`)*

---

## 6. Backend Integration Contracts
All network requests route through `ApiService` which automatically includes:
- Bearer JWT token in the `Authorization` header from `flutter_secure_storage`.
- Standard JSON content headers.
- Consistent error and timeout handling without crashing UI widgets.
