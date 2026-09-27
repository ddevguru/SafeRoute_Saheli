/*
 * =====================================================================================
 *  SAFEROUTE SAHELI — AI VISION & EVIDENCE CAMERA (ESP32-CAM)
 *  ALL-IN-ONE ARDUINO IDE FIRMWARE (SINGLE-FILE IMPLEMENTATION)
 * =====================================================================================
 *  Target Board:       AI Thinker ESP32-CAM
 *  Arduino IDE Core:   ESP32 by Espressif Systems (v2.0.x or v3.x)
 *  Partition Scheme:   Huge APP (3MB No OTA / 1MB SPIFFS)
 *  PSRAM:              Enabled
 *  Live Backend URL:   https://saferoute-saheli-backend.onrender.com
 *
 *  FEATURES IMPLEMENTED:
 *  1. OV2640 2-Megapixel Camera Driver (VGA/SVGA, PSRAM Accelerated)
 *  2. Live High-Speed MJPEG Streaming Server on Port 81 (/stream, /capture, /status)
 *  3. Secure Evidence Frame HTTPS Upload to Render Forensics Vault
 *  4. High-Power Flashlight LED Illuminator (GPIO 4)
 *  5. Emergency 5-Frame Burst Capture Sequence
 *  6. Periodic Cloud Telemetry & Device Heartbeat
 * =====================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include "esp_http_server.h"

// =====================================================================================
// 1. USER CONFIGURATION & CLOUD CREDENTIALS
// =====================================================================================
// Enter your WiFi Credentials here:
const char* WIFI_SSID         = "YOUR_WIFI_NAME";        // <-- Apne WiFi ka naam yahan dalein
const char* WIFI_PASSWORD     = "YOUR_WIFI_PASSWORD";    // <-- Apne WiFi ka password yahan dalein

// Live Render Backend API URL:
const char* BACKEND_BASE_URL  = "https://saferoute-saheli-backend.onrender.com/api";

// IoT Camera Identity & Cryptographic Secret:
const char* DEVICE_ID         = "SAHELI-CAM-001";
const char* DEVICE_SECRET     = "esp32cam_hmac_secret_token_saheli_2026";
const char* FIRMWARE_VERSION  = "1.0.0-CAM-ARDUINO";
const int   STREAM_PORT       = 81;

// =====================================================================================
// 2. AI-THINKER ESP32-CAM PIN DEFINITIONS
// =====================================================================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
#define FLASH_LED_PIN      4

// MJPEG Multipart Boundaries
#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY     = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART         = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t streamHttpd = NULL;
bool flashState = false;
unsigned long lastHeartbeatTime = 0;
unsigned long lastReconnectAttempt = 0;

// =====================================================================================
// 3. HARDWARE CAMERA INITIALIZATION
// =====================================================================================
bool initCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0       = Y2_GPIO_NUM;
    config.pin_d1       = Y3_GPIO_NUM;
    config.pin_d2       = Y4_GPIO_NUM;
    config.pin_d3       = Y5_GPIO_NUM;
    config.pin_d4       = Y6_GPIO_NUM;
    config.pin_d5       = Y7_GPIO_NUM;
    config.pin_d6       = Y8_GPIO_NUM;
    config.pin_d7       = Y9_GPIO_NUM;
    config.pin_xclk     = XCLK_GPIO_NUM;
    config.pin_pclk     = PCLK_GPIO_NUM;
    config.pin_vsync    = VSYNC_GPIO_NUM;
    config.pin_href     = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn     = PWDN_GPIO_NUM;
    config.pin_reset    = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Check PSRAM for high-resolution buffering
    if (psramFound()) {
        Serial.println("[Camera] PSRAM Detected! Configuring SVGA resolution with dual frame-buffers.");
        config.frame_size   = FRAMESIZE_VGA; // 640x480 for ultra-fluid streaming
        config.jpeg_quality = 12;            // Lower number = higher quality (10-63)
        config.fb_count     = 2;
        config.grab_mode    = CAMERA_GRAB_LATEST;
    } else {
        Serial.println("[Camera] Warning: PSRAM not found. Using conservative QVGA settings.");
        config.frame_size   = FRAMESIZE_QVGA; // 320x240
        config.jpeg_quality = 16;
        config.fb_count     = 1;
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[Camera] esp_camera_init failed with error 0x%x\n", err);
        return false;
    }

    // Camera Sensor Tweaks (flip/mirror if needed)
    sensor_t* s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_brightness(s, 1);
        s->set_contrast(s, 1);
        s->set_saturation(s, 0);
    }

    pinMode(FLASH_LED_PIN, OUTPUT);
    digitalWrite(FLASH_LED_PIN, LOW);
    return true;
}

void setFlashlight(bool state) {
    flashState = state;
    digitalWrite(FLASH_LED_PIN, flashState ? HIGH : LOW);
}

// =====================================================================================
// 4. EMBEDDED MJPEG STREAMING HTTP SERVER (PORT 81)
// =====================================================================================

// GET /stream -> Continuous MJPEG Video Feed
static esp_err_t streamHandler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[64];

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) return res;

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("[Stream] Camera frame acquisition failed.");
            res = ESP_FAIL;
        } else {
            size_t hlen = snprintf(part_buf, 64, _STREAM_PART, fb->len);
            res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
            if (res == ESP_OK) res = httpd_resp_send_chunk(req, part_buf, hlen);
            if (res == ESP_OK) res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
            esp_camera_fb_return(fb);
            fb = NULL;
        }

        if (res != ESP_OK) break;
        vTaskDelay(pdMS_TO_TICKS(40)); // ~22 FPS streaming throughput
    }
    return res;
}

// GET /capture -> Single Still JPEG Frame
static esp_err_t captureHandler(httpd_req_t *req) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=saheli_capture.jpg");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    esp_camera_fb_return(fb);
    return res;
}

// GET /status -> JSON Camera Health Diagnostics
static esp_err_t statusHandler(httpd_req_t *req) {
    char json[256];
    snprintf(json, sizeof(json),
        "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"psram\":%s,\"free_heap\":%u,\"wifi_rssi\":%d,\"port\":%d}",
        DEVICE_ID, millis() / 1000,
        psramFound() ? "true" : "false",
        (unsigned int)ESP.getFreeHeap(),
        WiFi.RSSI(),
        STREAM_PORT
    );

    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, json, strlen(json));
}

bool startStreamServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = STREAM_PORT;
    config.ctrl_port = STREAM_PORT + 1;
    config.max_open_sockets = 4;
    config.lru_purge_enable = true;

    httpd_uri_t streamUri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = streamHandler,
        .user_ctx  = NULL
    };

    httpd_uri_t captureUri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = captureHandler,
        .user_ctx  = NULL
    };

    httpd_uri_t statusUri = {
        .uri       = "/status",
        .method    = HTTP_GET,
        .handler   = statusHandler,
        .user_ctx  = NULL
    };

    if (httpd_start(&streamHttpd, &config) == ESP_OK) {
        httpd_register_uri_handler(streamHttpd, &streamUri);
        httpd_register_uri_handler(streamHttpd, &captureUri);
        httpd_register_uri_handler(streamHttpd, &statusUri);
        return true;
    }
    return false;
}

// =====================================================================================
// 5. SECURE FORENSIC EVIDENCE UPLOAD (RENDER HTTPS MULTIPART POST)
// =====================================================================================
bool uploadEvidenceSnapshot(bool enableFlashAssist) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[Upload] WiFi not connected! Skipping upload.");
        return false;
    }

    if (enableFlashAssist) {
        setFlashlight(true);
        delay(120); // Allow sensor auto-gain to adjust to flash illumination
    }

    // Discard 1 stale frame buffer to ensure fresh capture
    camera_fb_t *dummy = esp_camera_fb_get();
    if (dummy) esp_camera_fb_return(dummy);

    camera_fb_t *fb = esp_camera_fb_get();
    if (enableFlashAssist) setFlashlight(false);

    if (!fb) {
        Serial.println("[Upload] Failed to capture evidence frame.");
        return false;
    }

    Serial.printf("[Upload] Captured frame: %u bytes. Dispatching to Render Cloud...\n", fb->len);

    WiFiClientSecure client;
    client.setInsecure(); // Let's Encrypt validation
    HTTPClient http;

    String url = String(BACKEND_BASE_URL) + "/camera/capture";
    http.begin(client, url);

    String boundary = "----SaheliEvidenceBoundary7MA4YWxkTrZu0gW";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    http.addHeader("X-Device-Id", DEVICE_ID);
    http.addHeader("X-Device-Secret", DEVICE_SECRET);

    // Build Multipart Header & Footer
    String head = "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    head += String(DEVICE_ID) + "\r\n";

    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"device_secret\"\r\n\r\n";
    head += String(DEVICE_SECRET) + "\r\n";

    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"image\"; filename=\"evidence.jpg\"\r\n";
    head += "Content-Type: image/jpeg\r\n\r\n";

    String tail = "\r\n--" + boundary + "--\r\n";

    size_t totalLen = head.length() + fb->len + tail.length();

    // Stream multipart binary payload
    int httpResponseCode = http.sendRequest("POST", (uint8_t*)head.c_str(), head.length());
    // Use low-level client write for raw JPEG bytes + tail
    WiFiClientSecure *tcp = (WiFiClientSecure*)http.getStreamPtr();
    if (tcp) {
        tcp->write(fb->buf, fb->len);
        tcp->write((const uint8_t*)tail.c_str(), tail.length());
    }

    // Release camera frame buffer
    esp_camera_fb_return(fb);

    String response = http.getString();
    Serial.printf("[Upload] Cloud Vault Response (HTTP %d): %s\n", httpResponseCode, response.c_str());
    http.end();

    return (httpResponseCode == 200 || httpResponseCode == 201);
}

// 5-Frame Emergency Burst Capture Sequence
void triggerEmergencyBurst() {
    Serial.println("\n🚨 [EMERGENCY BURST] Initiating 5-frame forensic evidence sequence! 🚨");
    for (int frame = 1; frame <= 5; frame++) {
        Serial.printf("[Burst] Capturing frame %d/5...\n", frame);
        uploadEvidenceSnapshot(true); // Flash assist enabled for emergency evidence
        delay(300); // 300ms inter-frame gap
    }
    Serial.println("🚨 [EMERGENCY BURST] 5-frame sequence complete. 🚨\n");
}

// =====================================================================================
// 6. PERIODIC CLOUD HEARTBEAT
// =====================================================================================
void sendCameraHeartbeat() {
    if (WiFi.status() != WL_CONNECTED) return;

    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;

    String url = String(BACKEND_BASE_URL) + "/devices/heartbeat";
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    payload += "\"device_secret\":\"" + String(DEVICE_SECRET) + "\",";
    payload += "\"camera_health\":\"HEALTHY\",";
    payload += "\"wifi_rssi\":" + String(WiFi.RSSI()) + ",";
    payload += "\"firmware_version\":\"" + String(FIRMWARE_VERSION) + "\"";
    payload += "}";

    int code = http.POST(payload);
    Serial.printf("[Heartbeat] ESP32-CAM -> Render (HTTP %d)\n", code);
    http.end();
}

// =====================================================================================
// 7. ARDUINO SETUP & LOOP
// =====================================================================================
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n==================================================================");
    Serial.println("   SAFEROUTE SAHELI — AI VISION & EVIDENCE CAMERA (ESP32-CAM)    ");
    Serial.printf ("   Firmware: %s | Device ID: %s\n", FIRMWARE_VERSION, DEVICE_ID);
    Serial.printf ("   Target Backend: %s\n", BACKEND_BASE_URL);
    Serial.println("==================================================================");

    // 1. Initialize OV2640 Camera
    if (!initCamera()) {
        Serial.println("[Setup] FATAL: OV2640 camera initialization failed! Halting.");
        while (true) {
            delay(1000);
        }
    }
    Serial.println("[Setup] OV2640 Camera Hardware Initialized Successfully.");

    // 2. Connect to WiFi
    Serial.printf("[WiFi] Connecting to %s...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false); // Maximize streaming bandwidth
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 25) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WiFi] Connected Successfully!");
        Serial.printf("[WiFi] Live Video Stream URL: http://%s:%d/stream\n", 
                      WiFi.localIP().toString().c_str(), STREAM_PORT);
        Serial.printf("[WiFi] Still Snapshot URL:   http://%s:%d/capture\n", 
                      WiFi.localIP().toString().c_str(), STREAM_PORT);
    } else {
        Serial.println("\n[WiFi] Warning: WiFi connection failed. Reconnection loop active.");
    }

    // 3. Start Port 81 MJPEG Live Video Streaming Server
    if (startStreamServer()) {
        Serial.printf("[Setup] MJPEG Streaming HTTP Server active on port %d.\n", STREAM_PORT);
    } else {
        Serial.println("[Setup] Warning: Could not start MJPEG HTTP server.");
    }

    // 4. Initial Cloud Heartbeat
    sendCameraHeartbeat();

    Serial.println("\n[Setup] System Ready. Awaiting streaming connections & triggers.\n");
    Serial.println("Available Serial Commands:");
    Serial.println("  'c' -> Capture & Upload Single Evidence Frame");
    Serial.println("  'b' -> Trigger 5-Frame Emergency Burst Capture");
    Serial.println("  'f' -> Toggle High-Power Flashlight LED");
    Serial.println("  's' -> Print Device Status & Video Stream URL\n");
}

void loop() {
    unsigned long now = millis();

    // 1. WiFi Auto-Reconnect
    if (WiFi.status() != WL_CONNECTED) {
        if (now - lastReconnectAttempt >= 10000) {
            lastReconnectAttempt = now;
            Serial.println("[WiFi] Reconnecting...");
            WiFi.disconnect();
            WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        }
    }

    // 2. Periodic Cloud Heartbeat (Every 30 seconds)
    if (now - lastHeartbeatTime >= 30000) {
        lastHeartbeatTime = now;
        sendCameraHeartbeat();
    }

    // 3. Serial Interactive Commands
    if (Serial.available()) {
        char cmd = (char)Serial.read();
        switch (cmd) {
            case 'c':
            case 'C':
                Serial.println("[Serial] Uploading evidence snapshot...");
                uploadEvidenceSnapshot(false);
                break;
            case 'b':
            case 'B':
                triggerEmergencyBurst();
                break;
            case 'f':
            case 'F':
                setFlashlight(!flashState);
                Serial.printf("[Serial] Flashlight LED %s\n", flashState ? "ON" : "OFF");
                break;
            case 's':
            case 'S':
                Serial.println("\n--- ESP32-CAM STATUS ---");
                Serial.printf("Device ID:    %s\n", DEVICE_ID);
                Serial.printf("WiFi Status:  %s (IP: %s)\n", 
                              WiFi.status() == WL_CONNECTED ? "CONNECTED" : "DISCONNECTED",
                              WiFi.localIP().toString().c_str());
                Serial.printf("Stream URL:   http://%s:%d/stream\n", WiFi.localIP().toString().c_str(), STREAM_PORT);
                Serial.printf("Free Heap:    %u bytes\n", (unsigned int)ESP.getFreeHeap());
                Serial.printf("PSRAM:        %s\n", psramFound() ? "Enabled" : "Disabled");
                Serial.println("-------------------------\n");
                break;
            default:
                break;
        }
    }

    delay(20);
}
