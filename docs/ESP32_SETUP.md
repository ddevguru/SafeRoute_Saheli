# SafeRoute Saheli — ESP32 Wearable Firmware Setup & Flashing Guide

This document details the toolchain setup, configuration, calibration, and compilation steps for the **SafeRoute Saheli All-in-One Wearable Safety Device** (`firmware/esp32/`).

---

## 1. Prerequisites & Toolchain

The wearable firmware is developed with **PlatformIO** (VS Code Extension or CLI) on the **Arduino-ESP32** framework.

### Recommended Environment:
- **VS Code** with the **PlatformIO IDE** extension installed.
- Or **PlatformIO Core CLI** (`pip install platformio`).
- USB-to-UART Bridge Driver:
  - Silicon Labs CP210x or WCH CH340G driver depending on your ESP32 board.

---

## 2. Directory Structure

```
firmware/esp32/
├── platformio.ini         # Board environment, partitions & dependencies
└── src/
    ├── config.h           # Central hardware pins, server URLs & thresholds
    ├── main.cpp           # Dual-Core FreeRTOS setup & task orchestration
    ├── sensors/
    │   ├── touch_sensor.h / .cpp  # TTP223 capacitive touch handler
    │   ├── mpu6050.h / .cpp       # 6-Axis motion, fall & struggle detector
    │   ├── gps.h / .cpp           # NEO-6M UART2 NMEA parser
    │   ├── microphone.h / .cpp    # INMP441 I2S continuous clap detector
    │   ├── battery.h / .cpp       # ADC battery voltage divider & rolling average
    │   └── actuators.h / .cpp     # Piezo buzzer & MOSFET vibration motor
    ├── communication/
    │   └── wifi_manager.h / .cpp  # Non-blocking Wi-Fi auto-reconnect
    ├── storage/
    │   └── local_storage.h / .cpp # SPIFFS offline emergency backup queue
    └── api/
        └── backend_client.h / .cpp# HTTP REST client to SafeRoute Flask API
```

---

## 3. Configuration (`src/config.h`)

Before flashing, configure your local Wi-Fi credentials and backend server address in [`firmware/esp32/src/config.h`](file:///c:/Safe-Route-saheli/firmware/esp32/src/config.h):

```c
#define WIFI_SSID             "YourWiFiSSID"
#define WIFI_PASSWORD         "YourWiFiPassword"
#define BACKEND_BASE_URL      "http://192.168.1.100:5000/api"
#define DEVICE_ID             "SAHELI-WEARABLE-001"
#define DEVICE_SECRET         "wearable_esp32_hmac_shared_secret_2026"
```

---

## 4. Compilation & Flashing Instructions

### Via PlatformIO CLI:
```bash
cd firmware/esp32

# 1. Build firmware binary
pio run

# 2. Flash to connected ESP32 board
pio run --target upload

# 3. Open high-speed serial monitor (115200 baud)
pio device monitor -b 115200
```

---

## 5. FreeRTOS Dual-Core Task Architecture

The wearable firmware distributes processing across both physical Xtensa LX6 cores:
- **Core 0 (`AudioTask`):**
  - Priority: 2 (High).
  - Dedicated to continuous, zero-jitter 16kHz 24-bit I2S sampling from the INMP441 digital microphone.
  - Runs acoustic peak detection and triple-clap pattern matching state machine.
- **Core 1 (`SupervisorTask`):**
  - Priority: 1.
  - Polls TTP223 touch sensor (1.5s press-and-hold trigger).
  - Computes 3D acceleration and angular velocity vector magnitudes on MPU6050 for fall (>2.8g) and struggle (>200 dps) detection.
  - Parses NEO-6M NMEA sentences on UART2.
  - Maintains Wi-Fi connection and manages periodic heartbeats and SPIFFS offline queue flushes.
