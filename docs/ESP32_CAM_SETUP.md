# SafeRoute Saheli — ESP32-CAM Dedicated Firmware Setup Guide

This guide details the flashing, configuration, streaming, and testing procedures for the **Dedicated ESP32-CAM Optical Unit** (`firmware/esp32_cam/`).

---

## 1. Hardware Architecture

The optical module is built exclusively for the **AI-Thinker ESP32-CAM** board featuring:
- **Sensor:** OmniVision OV2640 2-Megapixel CMOS camera.
- **PSRAM:** 4MB external pseudo-static RAM enabling double-buffering and high-resolution JPEG compression.
- **Flashlight LED:** High-intensity white LED on GPIO 4 for night illumination during emergency bursts.
- **Firmware Separation:** This codebase runs completely independent of the wearable band.

---

## 2. Flashing Procedure via FTDI Programmer

Because standard AI-Thinker ESP32-CAM boards lack an onboard USB-to-UART converter:

### FTDI Wiring for Flashing:
| FTDI Programmer | ESP32-CAM Pin | Notes |
| :--- | :--- | :--- |
| **VCC (5V)** | **5V Pin** | Must supply solid 500mA+ |
| **GND** | **GND Pin** | Common Ground |
| **TX** | **U0R (GPIO 3)** | Program receive |
| **RX** | **U0T (GPIO 1)** | Program transmit |
| **GND** | **GPIO 0** | **Connect GPIO 0 to GND to enter Bootloader mode during flashing!** |

### Flashing Steps:
1. Connect **GPIO 0 to GND**.
2. Press the **RST** button on the back of the ESP32-CAM.
3. Run the upload command:
   ```bash
   cd firmware/esp32_cam
   pio run --target upload
   ```
4. Once upload completes, **disconnect GPIO 0 from GND**.
5. Press the **RST** button again to boot into normal streaming mode.

---

## 3. Streaming and Live Feed URLs

Upon connecting to Wi-Fi, the ESP32-CAM starts the authenticated MJPEG server on port 81:
- **Live Stream URL:** `http://<camera_ip>:81/stream?key=SaheliStreamKey2026`
- **Instant Snapshot:** `http://<camera_ip>:81/capture`
- **Device Health Status:** `http://<camera_ip>:81/status`

---

## 4. Emergency Burst Capture & Evidence Upload

During an emergency incident:
1. The camera immediately pulses the high-intensity flashlight LED on GPIO 4.
2. It captures a sequence of **5 high-resolution frames** at 300ms intervals.
3. Each frame is uploaded directly to the backend endpoint:
   `POST /api/camera/emergency-capture`
   with multipart form data containing `device_id`, `device_secret`, and binary JPEG payload.
