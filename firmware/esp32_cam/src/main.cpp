#include <Arduino.h>
#include <WiFi.h>
#include "camera_config.h"
#include "camera_driver.h"
#include "stream_server.h"
#include "snapshot_manager.h"
#include "diagnostics.h"

unsigned long lastHeartbeatTime = 0;
unsigned long lastReconnectAttempt = 0;
bool flashState = false;

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=======================================================");
    Serial.println("  SAFEROUTE SAHELI — DEDICATED ESP32-CAM FIRMWARE      ");
    Serial.printf ("  Firmware Version: %s | Device ID: %s\n", FIRMWARE_VERSION, DEVICE_ID);
    Serial.println("=======================================================");

    // 1. Initialize OV2640 Camera Hardware
    if (!CameraDriver::initCamera(FRAMESIZE_VGA, 10)) {
        Serial.println("[Setup] FATAL: Camera initialization failed! Halting.");
        while (true) {
            delay(1000);
        }
    }

    // 2. Connect to WiFi
    Serial.printf("[WiFi] Connecting to %s...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false); // Maximize streaming throughput
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WiFi] Connected successfully!");
        Serial.printf("[WiFi] IP Address: http://%s:%d/stream\n", 
                      WiFi.localIP().toString().c_str(), STREAM_SERVER_PORT);
    } else {
        Serial.println("\n[WiFi] Warning: Initial WiFi connection timed out. Reconnection loop active.");
    }

    // 3. Start Authenticated MJPEG Live Stream Server on Port 81
    if (StreamServer::startServer()) {
        Serial.println("[Setup] MJPEG Stream Server active.");
    }

    // 4. Initial Diagnostics & Telemetry
    Diagnostics::printDiagnostics();
    Diagnostics::sendHeartbeat();

    Serial.println("[Setup] System Ready. Awaiting commands & streaming requests.\n");
    Serial.println("Debug Commands via Serial Console:");
    Serial.println("  'c' -> Single snapshot upload to backend");
    Serial.println("  'b' -> Trigger 5-frame emergency burst capture");
    Serial.println("  'd' -> Print full diagnostics report");
    Serial.println("  'f' -> Toggle high-power flashlight LED\n");
}

void loop() {
    unsigned long now = millis();

    // 1. WiFi Auto-Reconnect Management
    if (WiFi.status() != WL_CONNECTED) {
        if (now - lastReconnectAttempt >= 10000) {
            lastReconnectAttempt = now;
            Serial.println("[WiFi] Reconnecting...");
            WiFi.disconnect();
            WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        }
    }

    // 2. Periodic Cloud Heartbeat
    if (now - lastHeartbeatTime >= HEARTBEAT_INTERVAL_MS) {
        lastHeartbeatTime = now;
        Diagnostics::sendHeartbeat();
    }

    // 3. Serial Debug Commands (Manual trigger, hardware testing, QA)
    if (Serial.available()) {
        char cmd = (char)Serial.read();
        switch (cmd) {
            case 'c':
            case 'C':
                Serial.println("[Serial] Capturing single snapshot...");
                SnapshotManager::uploadSingleSnapshot(false);
                break;
            case 'b':
            case 'B':
                Serial.println("[Serial] Triggering emergency burst capture...");
                SnapshotManager::triggerBurstCapture(BURST_FRAME_COUNT);
                break;
            case 'd':
            case 'D':
                Diagnostics::printDiagnostics();
                break;
            case 'f':
            case 'F':
                flashState = !flashState;
                CameraDriver::setFlashLED(flashState);
                Serial.printf("[Serial] Flashlight LED %s\n", flashState ? "ON" : "OFF");
                break;
            default:
                break;
        }
    }

    delay(20);
}
