/*
 * =====================================================================================
 *  SAFEROUTE SAHELI — WEARABLE SAFETY DEVICE (MAIN ESP32)
 *  ALL-IN-ONE ARDUINO IDE FIRMWARE (SINGLE-FILE IMPLEMENTATION)
 * =====================================================================================
 *  Target Board:       ESP32 Dev Module / DOIT ESP32 DEVKIT V1
 *  Arduino IDE Core:   ESP32 by Espressif Systems (v2.0.x or v3.x)
 *  Live Backend URL:   https://saferoute-saheli-backend.onrender.com
 *
 *  HARDWARE COMPONENTS SUPPORTED:
 *  1. TTP223 Capacitive Touch Sensor         -> GPIO 13 (SOS Long-Press 1.5s)
 *  2. MPU-6050 6-Axis Accel / Gyro (I2C)     -> SDA: GPIO 21, SCL: GPIO 22 (Fall & Struggle)
 *  3. NEO-6M GPS Module (UART2)               -> RX2: GPIO 16, TX2: GPIO 17 (Live Tracking)
 *  4. INMP441 I2S Digital Microphone         -> SCK: GPIO 26, WS: GPIO 25, SD: GPIO 33 (3-Clap SOS)
 *  5. Battery Voltage Monitor (ADC1)         -> GPIO 34 (Voltage Divider 2:1)
 *  6. Active Piezo Buzzer                    -> GPIO 14 (Acoustic Siren)
 *  7. Haptic Vibration Motor (MOSFET)        -> GPIO 12 (Tactile Feedback)
 *  8. Onboard Status LED                     -> GPIO 2  (Visual Beacon)
 * =====================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <Wire.h>
#include <ESP_I2S.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

WebServer* localServer = nullptr;
I2SClass*  i2sMic      = nullptr;

// =====================================================================================
// 1. USER CONFIGURATION & CLOUD CREDENTIALS
// =====================================================================================
// Enter your WiFi Credentials here:
const char* WIFI_SSID         = "Nothing Phone (3a) Lite_1682";        // <-- Apne WiFi ka naam yahan dalein
const char* WIFI_PASSWORD     = "Nothing3a";    // <-- Apne WiFi ka password yahan dalein

// Live Render Backend API URL:
const char* BACKEND_BASE_URL  = "https://saferoute-saheli-backend.onrender.com/api";

// IoT Device Identity & Cryptographic Secret:
const char* DEVICE_ID         = "SAHELI-WEARABLE-001";
const char* DEVICE_SECRET     = "wearable_secret_2026";
const char* FIRMWARE_VERSION  = "1.0.0-ARDUINO";

// =====================================================================================
// 2. HARDWARE PIN DEFINITIONS
// =====================================================================================
#define PIN_TOUCH_SENSOR      13    // TTP223 Touch sensor (Active HIGH)
#define PIN_I2C_SDA           21    // MPU6050 SDA
#define PIN_I2C_SCL           22    // MPU6050 SCL
#define PIN_GPS_RX            16    // ESP32 RX2 connects to NEO-6M TX
#define PIN_GPS_TX            17    // ESP32 TX2 connects to NEO-6M RX
#define PIN_I2S_SCK           26    // INMP441 Serial Clock (BCLK)
#define PIN_I2S_WS            25    // INMP441 Word Select (LRCLK)
#define PIN_I2S_SD            33    // INMP441 Serial Data Out (DIN)
#define PIN_BATTERY_ADC       34    // Battery voltage divider (ADC1)
#define PIN_BUZZER            14    // Piezo Buzzer (Transistor driven)
#define PIN_VIBRATION         15    // Haptic Motor (Avoid GPIO 12 - MTDI pin causes flash 1.8V boot crash!)
#define PIN_STATUS_LED        2     // Onboard Status LED

// Detection Thresholds
#define TOUCH_HOLD_TRIGGER_MS 700   // 0.7s quick hold for SOS
#define MPU6050_ADDR          0x68
#define FALL_ACCEL_THRESHOLD  2.8f  // 2.8 G impact
#define STRUGGLE_GYRO_THRESH  200.0f// 200 deg/s angular velocity
#define CLAP_PEAK_THRESHOLD   22000 // Sharp clap amplitude (prevents floating pin false triggers)
#define CLAP_MIN_GAP_MS       180   // Min interval between claps
#define CLAP_MAX_GAP_MS       750   // Max interval between claps
#define CLAP_COUNT_REQUIRED   3     // 3 rapid claps for SOS

// Telemetry Timing Intervals
#define INTERVAL_NORMAL_GPS   25000 // 25 seconds normal GPS push
#define INTERVAL_EMERGENCY_GPS 5000 // 5 seconds high-frequency emergency stream
#define INTERVAL_HEARTBEAT    30000 // 30 seconds cloud health heartbeat

// =====================================================================================
// 3. GLOBAL OBJECTS & DATA STRUCTURES
// =====================================================================================
#define gpsSerial Serial2 // Use pre-allocated UART2 to prevent duplicate driver abort crash

bool hasMPU    = false; // Set to true only if MPU-6050 responds on I2C
bool hasI2SMic = false; // Set to true only if INMP441 driver installs cleanly

struct GPSData {
    double latitude       = 28.6139; // Default fallback: New Delhi
    double longitude      = 77.2090;
    float  speedKmph      = 0.0f;
    bool   hasValidFix    = false;
    int    satellites     = 0;
};

GPSData currentGPS;
bool emergencyActive      = false;
unsigned long emergencyStartTime = 0;
unsigned long lastHeartbeatTime  = 0;
unsigned long lastGpsPushTime    = 0;
unsigned long touchStartTime     = 0;
bool touchPressed         = false;

// Clap Detector State Machine
int clapCount             = 0;
unsigned long lastClapTime = 0;

// FreeRTOS Task Handles
TaskHandle_t audioTaskHandle      = NULL;
TaskHandle_t supervisorTaskHandle = NULL;

// =====================================================================================
// 4. ACTUATOR CONTROLS (BUZZER, VIBRATION, LED)
// =====================================================================================
void initActuators() {
    pinMode(PIN_BUZZER, OUTPUT);
    pinMode(PIN_VIBRATION, OUTPUT);
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    digitalWrite(PIN_VIBRATION, LOW);
    digitalWrite(PIN_STATUS_LED, LOW);
}

void pulseHaptic(int durationMs) {
    digitalWrite(PIN_VIBRATION, HIGH);
    delay(durationMs);
    digitalWrite(PIN_VIBRATION, LOW);
}

void playStartupTone() {
    digitalWrite(PIN_STATUS_LED, HIGH);
    digitalWrite(PIN_BUZZER, HIGH);
    delay(40);
    digitalWrite(PIN_BUZZER, LOW);
    digitalWrite(PIN_STATUS_LED, LOW);
    delay(50);
    pulseHaptic(60);
}

void updateAlarmActuators() {
    if (!emergencyActive) {
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_VIBRATION, LOW);
        return;
    }

    // Auto-silence acoustic alarm after 60 seconds (backend tracking continues)
    if (millis() - emergencyStartTime > 60000) {
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_VIBRATION, LOW);
        return;
    }

    // Pulsing acoustic + strobe alarm cycle
    unsigned long cycle = millis() % 600;
    if (cycle < 300) {
        digitalWrite(PIN_BUZZER, HIGH);
        digitalWrite(PIN_VIBRATION, HIGH);
        digitalWrite(PIN_STATUS_LED, HIGH);
    } else {
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_VIBRATION, LOW);
        digitalWrite(PIN_STATUS_LED, LOW);
    }
}

// =====================================================================================
// 5. BATTERY MONITOR (ADC)
// =====================================================================================
float readBatteryVoltage() {
    int raw = analogRead(PIN_BATTERY_ADC);
    // ADC 12-bit (0-4095), 3.3V reference, 2:1 voltage divider
    float voltage = (raw / 4095.0f) * 3.3f * 2.0f;
    if (voltage < 2.0f) voltage = 3.85f; // Simulation fallback when on USB power
    return voltage;
}

int calculateBatteryPercent(float voltage) {
    if (voltage >= 4.20f) return 100;
    if (voltage <= 3.20f) return 0;
    return (int)((voltage - 3.20f) / (4.20f - 3.20f) * 100.0f);
}

// =====================================================================================
// 6. MPU-6050 SENSOR DRIVER (RAW I2C IMPLEMENTATION — NO EXTERNAL LIB REQUIRED)
// =====================================================================================
bool initMPU6050() {
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    Wire.setTimeOut(50); // Prevent bus lockup if MPU6050 is not plugged in
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x6B); // PWR_MGMT_1 register
    Wire.write(0x00); // Wake up MPU-6050
    return (Wire.endTransmission() == 0);
}

void checkMotionEvents(bool &outFall, bool &outStruggle, float &outAccelMag, float &outGyroMag) {
    outFall = false;
    outStruggle = false;

    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x3B); // Starting register for Accel readings
    if (Wire.endTransmission(false) != 0) return;

    if (Wire.requestFrom(MPU6050_ADDR, 14, true) == 14) {
        int16_t ax = (Wire.read() << 8) | Wire.read();
        int16_t ay = (Wire.read() << 8) | Wire.read();
        int16_t az = (Wire.read() << 8) | Wire.read();
        Wire.read(); Wire.read(); // Skip temperature
        int16_t gx = (Wire.read() << 8) | Wire.read();
        int16_t gy = (Wire.read() << 8) | Wire.read();
        int16_t gz = (Wire.read() << 8) | Wire.read();

        // Convert to Gs (+/- 2g scale: 16384 LSB/g)
        float gX = ax / 16384.0f;
        float gY = ay / 16384.0f;
        float gZ = az / 16384.0f;
        outAccelMag = sqrt(gX * gX + gY * gY + gZ * gZ);

        // Convert to deg/s (+/- 250 deg/s scale: 131 LSB/(deg/s))
        float dX = gx / 131.0f;
        float dY = gy / 131.0f;
        float dZ = gz / 131.0f;
        outGyroMag = sqrt(dX * dX + dY * dY + dZ * dZ);

        // Fall detection: abrupt high-g impact
        if (outAccelMag > FALL_ACCEL_THRESHOLD) {
            outFall = true;
        }

        // Physical struggle: high rotational agitation
        if (outGyroMag > STRUGGLE_GYRO_THRESH) {
            outStruggle = true;
        }
    }
}

// =====================================================================================
// 7. NEO-6M GPS NMEA PARSER (STANDALONE NON-BLOCKING)
// =====================================================================================
void parseNMEALine(String line) {
    if (line.startsWith("$GPRMC") || line.startsWith("$GNRMC")) {
        // Example: $GPRMC,123519,A,2836.834,N,07712.540,E,022.4,084.4,230326,003.1,W*6A
        int comma1 = line.indexOf(',');
        int comma2 = line.indexOf(',', comma1 + 1);
        int comma3 = line.indexOf(',', comma2 + 1); // Status ('A' = Valid, 'V' = Warning)
        
        if (comma3 > 0 && line.charAt(comma2 + 1) == 'A') {
            int comma4 = line.indexOf(',', comma3 + 1); // Lat
            int comma5 = line.indexOf(',', comma4 + 1); // N/S
            int comma6 = line.indexOf(',', comma5 + 1); // Lon
            int comma7 = line.indexOf(',', comma6 + 1); // E/W
            int comma8 = line.indexOf(',', comma7 + 1); // Speed in knots

            String rawLat = line.substring(comma3 + 1, comma4);
            String latDir = line.substring(comma4 + 1, comma5);
            String rawLon = line.substring(comma5 + 1, comma6);
            String lonDir = line.substring(comma6 + 1, comma7);
            String rawSpeed = line.substring(comma7 + 1, comma8);

            if (rawLat.length() >= 4 && rawLon.length() >= 5) {
                // Convert DDMM.MMMM to Decimal Degrees
                double latDeg = rawLat.substring(0, 2).toDouble();
                double latMin = rawLat.substring(2).toDouble();
                double lat = latDeg + (latMin / 60.0);
                if (latDir == "S") lat = -lat;

                double lonDeg = rawLon.substring(0, 3).toDouble();
                double lonMin = rawLon.substring(3).toDouble();
                double lon = lonDeg + (lonMin / 60.0);
                if (lonDir == "W") lon = -lon;

                currentGPS.latitude = lat;
                currentGPS.longitude = lon;
                currentGPS.speedKmph = rawSpeed.toFloat() * 1.852f; // Knots to km/h
                currentGPS.hasValidFix = true;
            }
        }
    }
}

void pollGPS() {
    static String nmeaBuffer = "";
    while (gpsSerial.available() > 0) {
        char c = (char)gpsSerial.read();
        if (c == '\n') {
            nmeaBuffer.trim();
            if (nmeaBuffer.length() > 0) {
                parseNMEALine(nmeaBuffer);
            }
            nmeaBuffer = "";
        } else if (c != '\r') {
            if (nmeaBuffer.length() < 120) {
                nmeaBuffer += c;
            } else {
                nmeaBuffer = ""; // Overflow guard
            }
        }
    }
}

// =====================================================================================
// 8. INMP441 I2S DIGITAL MICROPHONE DRIVER & 3-CLAP SOS DETECTOR
// =====================================================================================
bool initI2SMicrophone() {
    if (i2sMic == nullptr) {
        i2sMic = new I2SClass();
    }
    i2sMic->setPins(PIN_I2S_SCK, PIN_I2S_WS, -1, PIN_I2S_SD);
    return i2sMic->begin(I2S_MODE_STD, 16000, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO, I2S_STD_SLOT_LEFT);
}

bool detectClapSpike() {
    if (i2sMic == nullptr) return false;
    int16_t sampleBuffer[128];
    size_t bytesRead = i2sMic->readBytes((char*)sampleBuffer, sizeof(sampleBuffer));
    if (bytesRead == 0) return false;
    
    int samples = bytesRead / sizeof(int16_t);
    int maxAmplitude = 0;
    long sum = 0;
    for (int i = 0; i < samples; i++) {
        int amp = abs(sampleBuffer[i]);
        sum += amp;
        if (amp > maxAmplitude) maxAmplitude = amp;
    }

    int avgAmplitude = sum / (samples > 0 ? samples : 1);

    // True acoustic clap has an impulse peak:
    // 1. Peak must be loud (> 22000)
    // 2. Crest factor: Peak must be at least 3.5x higher than average window (rejects floating pin static!)
    return (maxAmplitude > CLAP_PEAK_THRESHOLD && maxAmplitude > (avgAmplitude * 3.5));
}

bool updateClapPattern() {
    unsigned long now = millis();
    if (detectClapSpike()) {
        if (clapCount == 0) {
            clapCount = 1;
            lastClapTime = now;
            Serial.println("[Clap] Spike #1 detected.");
        } else {
            unsigned long gap = now - lastClapTime;
            if (gap >= CLAP_MIN_GAP_MS && gap <= CLAP_MAX_GAP_MS) {
                clapCount++;
                lastClapTime = now;
                Serial.printf("[Clap] Spike #%d detected! (gap: %lu ms)\n", clapCount, gap);
                if (clapCount >= CLAP_COUNT_REQUIRED) {
                    clapCount = 0;
                    return true; // 3-Clap SOS Trigger!
                }
            } else if (gap > CLAP_MAX_GAP_MS) {
                clapCount = 1;
                lastClapTime = now;
                Serial.println("[Clap] Resetting pattern. Spike #1 started.");
            }
        }
        delay(80); // Debounce acoustic decay
    }

    if (clapCount > 0 && (now - lastClapTime > CLAP_MAX_GAP_MS)) {
        clapCount = 0;
    }
    return false;
}

// =====================================================================================
// 9. SECURE CLOUD API CLIENT (RENDER HTTPS)
// =====================================================================================
void sendCloudHeartbeat() {
    if (WiFi.status() != WL_CONNECTED) return;

    WiFiClientSecure client;
    client.setInsecure(); // Allows connection to Render's Let's Encrypt SSL
    HTTPClient http;

    String url = String(BACKEND_BASE_URL) + "/devices/heartbeat";
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    float v = readBatteryVoltage();
    int pct = calculateBatteryPercent(v);

    String payload = "{";
    payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    payload += "\"device_secret\":\"" + String(DEVICE_SECRET) + "\",";
    payload += "\"battery_percent\":" + String(pct) + ",";
    payload += "\"battery_voltage\":" + String(v, 2) + ",";
    payload += "\"wifi_rssi\":" + String(WiFi.RSSI()) + ",";
    payload += "\"firmware_version\":\"" + String(FIRMWARE_VERSION) + "\"";
    payload += "}";

    int code = http.POST(payload);
    Serial.printf("[Cloud] Heartbeat -> %s (HTTP %d)\n", url.c_str(), code);
    http.end();
}

void triggerEmergencySOS(String triggerSource, float confidence) {
    emergencyActive = true;
    emergencyStartTime = millis();

    Serial.printf("\n🚨 [EMERGENCY TRIGGERED] Reason: %s | Confidence: %.2f 🚨\n", 
                  triggerSource.c_str(), confidence);

    // Immediate tactile & audio confirmation
    pulseHaptic(400);

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[Cloud] WiFi disconnected! Queueing alert locally.");
        return;
    }

    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;

    String url = String(BACKEND_BASE_URL) + "/devices/events";
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    float v = readBatteryVoltage();
    int pct = calculateBatteryPercent(v);

    String payload = "{";
    payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    payload += "\"device_secret\":\"" + String(DEVICE_SECRET) + "\",";
    payload += "\"event_type\":\"EMERGENCY_TRIGGER\",";
    payload += "\"payload\":{";
    payload += "\"trigger_type\":\"" + triggerSource + "\",";
    payload += "\"confidence\":" + String(confidence, 2) + ",";
    payload += "\"latitude\":" + String(currentGPS.latitude, 6) + ",";
    payload += "\"longitude\":" + String(currentGPS.longitude, 6) + ",";
    payload += "\"speed_kmph\":" + String(currentGPS.speedKmph, 1) + ",";
    payload += "\"battery_percent\":" + String(pct);
    payload += "}}";

    int code = http.POST(payload);
    Serial.printf("[Cloud] SOS Event Dispatch -> HTTP %d\n", code);
    http.end();
}

void sendGPSTelemetry() {
    if (WiFi.status() != WL_CONNECTED) return;

    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;

    String url = String(BACKEND_BASE_URL) + "/devices/events";
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    payload += "\"device_secret\":\"" + String(DEVICE_SECRET) + "\",";
    payload += "\"event_type\":\"GPS_TELEMETRY\",";
    payload += "\"payload\":{";
    payload += "\"latitude\":" + String(currentGPS.latitude, 6) + ",";
    payload += "\"longitude\":" + String(currentGPS.longitude, 6) + ",";
    payload += "\"speed_kmph\":" + String(currentGPS.speedKmph, 1) + ",";
    payload += "\"emergency_active\":" + String(emergencyActive ? "true" : "false");
    payload += "}}";

    http.POST(payload);
    http.end();
}

// =====================================================================================
// 10. FREERTOS DUAL-CORE MULTITASKING TASKS
// =====================================================================================

// Core 0: High-Frequency Audio DSP (Spawned only if physical I2S microphone is detected)
void audioCoreTask(void* parameter) {
    Serial.println("[Core 0] Audio Clap Listening Task Active.");
    while (true) {
        if (hasI2SMic && updateClapPattern()) {
            Serial.println("[Core 0] >>> 3-CLAP EMERGENCY PATTERN DETECTED! <<<");
            triggerEmergencySOS("CLAP", 0.95f);
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

// =====================================================================================
// 11. ARDUINO SETUP & LOOP (BULLETPROOF INITIALIZATION)
// =====================================================================================
void setup() {
    // Disable brownout detector to prevent false reset on USB power sag
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

    Serial.begin(115200);
    delay(200);
    Serial.println();
    Serial.println("==================================================================");
    Serial.println("   SAFEROUTE SAHELI — MAIN ESP32 WEARABLE SAFETY DEVICE           ");
    Serial.printf ("   Firmware: %s | Device ID: %s\n", FIRMWARE_VERSION, DEVICE_ID);
    Serial.printf ("   Target Backend: %s\n", BACKEND_BASE_URL);
    Serial.println("==================================================================");
    Serial.flush();

    // 1. Initialize Actuators (Buzzer, Vibration, Status LED)
    initActuators();
    playStartupTone();
    Serial.println("[Setup 1/6] Actuators initialized (Buzzer: GPIO 14, Vibration: GPIO 15, LED: GPIO 2)");
    Serial.flush();

    // 2. Initialize TTP223 Capacitive Touch
    pinMode(PIN_TOUCH_SENSOR, INPUT_PULLDOWN);
    Serial.println("[Setup 2/6] TTP223 Capacitive Touch Sensor initialized on GPIO 13 (INPUT_PULLDOWN)");
    Serial.flush();

    // 3. Initialize MPU-6050 Motion Sensor (Safe check with timeout)
    hasMPU = initMPU6050();
    if (hasMPU) {
        Serial.println("[Setup 3/6] MPU-6050 6-Axis Motion Sensor: OK");
    } else {
        Serial.println("[Setup 3/6] Note: MPU-6050 not detected on I2C. Motion alarms bypassed safely.");
    }
    Serial.flush();

    // 4. Initialize NEO-6M GPS on UART2
    gpsSerial.begin(9600, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);
    Serial.println("[Setup 4/6] NEO-6M GPS Receiver (UART2): Initialized on GPIO 16/17");
    Serial.flush();

    // 5. Initialize INMP441 I2S Microphone (Safe check)
    hasI2SMic = initI2SMicrophone();
    if (hasI2SMic) {
        Serial.println("[Setup 5/6] INMP441 I2S Digital Microphone: OK");
        // Spawn audio clap task on Core 0 only when mic is present
        xTaskCreatePinnedToCore(
            audioCoreTask,
            "AudioCoreTask",
            4096,
            NULL,
            1,
            &audioTaskHandle,
            0
        );
    } else {
        Serial.println("[Setup 5/6] Note: INMP441 I2S Microphone not detected. Clap detector bypassed safely.");
    }
    Serial.flush();

    // 6. Connect to WiFi & Start SoftAP Direct Hotspot
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP("Saheli_Smart_Band", "12345678");
    delay(100);
    IPAddress apIP = WiFi.softAPIP();
    Serial.println("\n--------------------------------------------------");
    Serial.println("[WiFi AP] Direct SoftAP Hotspot Active: 'Saheli_Smart_Band'");
    Serial.printf ("[WiFi AP] SoftAP Direct URL: http://%s (Password: 12345678)\n", apIP.toString().c_str());
    Serial.println("--------------------------------------------------");
    Serial.flush();

    if (String(WIFI_SSID) != "YOUR_WIFI_NAME") {
        Serial.printf("[WiFi STA] Connecting to Router / Hotspot: %s\n", WIFI_SSID);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 10) {
            delay(300);
            Serial.print(".");
            attempts++;
        }
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\n==================================================");
            Serial.println("✅ [WiFi STA] Connected! Network: " + String(WIFI_SSID));
            Serial.println("🌐 [WiFi STA] ESP32 IP Address: " + WiFi.localIP().toString());
            Serial.println("👉 ENTER THIS IP IN SAHELI MOBILE APP: " + WiFi.localIP().toString());
            Serial.println("==================================================\n");
            sendCloudHeartbeat();
        } else {
            Serial.println("\n[WiFi STA] Router not found. Operating via direct SoftAP at 192.168.4.1");
            Serial.println("👉 CONNECT PHONE TO 'Saheli_Smart_Band' & USE IP: 192.168.4.1 IN APP\n");
        }
    } else {
        Serial.println("[WiFi STA] Notice: Set WIFI_SSID & WIFI_PASSWORD to connect directly to home router/cloud.");
        Serial.println("[WiFi STA] Defaulting to Direct AP mode (Connect phone to 'Saheli_Smart_Band').");
    }
    Serial.flush();

    // Initialize WebServer pointer after Wi-Fi stack is active
    localServer = new WebServer(80);

    // Register local HTTP endpoints for Mobile App
    localServer->on("/", HTTP_GET, []() {
        float v = readBatteryVoltage();
        int pct = calculateBatteryPercent(v);
        String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>Saheli Smart Band</title>";
        html += "<style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#002350;color:#fff;text-align:center;padding:25px;}";
        html += ".card{background:rgba(255,255,255,0.08);padding:20px;border-radius:18px;margin:20px auto;max-width:380px;border:1px solid rgba(255,255,255,0.15);}";
        html += ".badge{background:#10B981;color:#fff;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:bold;}";
        html += ".btn{background:#D2AE39;color:#000;padding:12px 24px;border:none;border-radius:10px;font-weight:bold;text-decoration:none;display:inline-block;margin-top:15px;}";
        html += "</style></head><body>";
        html += "<h2>SafeRoute Saheli — Smart Band</h2>";
        html += "<div class='card'>";
        html += "<p><span class='badge'>HARDWARE ONLINE</span></p>";
        html += "<p><b>Device ID:</b> " + String(DEVICE_ID) + "</p>";
        html += "<p><b>Battery:</b> " + String(pct) + "% (" + String(v, 2) + "V)</p>";
        html += "<p><b>GPS Fix:</b> " + String(currentGPS.hasValidFix ? "FIXED" : "SEARCHING...") + "</p>";
        html += "<p><b>Emergency:</b> " + String(emergencyActive ? "<b style='color:#EF4444'>ACTIVE SOS</b>" : "NORMAL") + "</p>";
        html += "<a class='btn' href='/test-alarm'>Test Hardware Alarm</a>";
        html += "</div></body></html>";
        localServer->sendHeader("Access-Control-Allow-Origin", "*");
        localServer->send(200, "text/html", html);
    });

    localServer->on("/status", HTTP_GET, []() {
        float v = readBatteryVoltage();
        int pct = calculateBatteryPercent(v);
        String json = "{";
        json += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
        json += "\"status\":\"ONLINE\",";
        json += "\"device_type\":\"ESP32_WEARABLE\",";
        json += "\"nickname\":\"Saheli Smart Safety Band\",";
        json += "\"battery_percent\":" + String(pct) + ",";
        json += "\"battery_voltage\":" + String(v, 2) + ",";
        json += "\"wifi_rssi\":" + String(WiFi.RSSI()) + ",";
        json += "\"latitude\":" + String(currentGPS.latitude, 6) + ",";
        json += "\"longitude\":" + String(currentGPS.longitude, 6) + ",";
        json += "\"gps_fixed\":" + String(currentGPS.hasValidFix ? "true" : "false") + ",";
        json += "\"emergency_active\":" + String(emergencyActive ? "true" : "false") + ",";
        json += "\"firmware_version\":\"" + String(FIRMWARE_VERSION) + "\",";
        json += "\"uptime_s\":" + String(millis() / 1000);
        json += "}";
        localServer->sendHeader("Access-Control-Allow-Origin", "*");
        localServer->send(200, "application/json", json);
    });

    localServer->on("/ping", HTTP_GET, []() {
        localServer->sendHeader("Access-Control-Allow-Origin", "*");
        localServer->send(200, "application/json", "{\"pong\":true,\"device_id\":\"" + String(DEVICE_ID) + "\"}");
    });

    localServer->on("/test-alarm", HTTP_ANY, []() {
        digitalWrite(PIN_BUZZER, HIGH);
        digitalWrite(PIN_VIBRATION, HIGH);
        digitalWrite(PIN_STATUS_LED, HIGH);
        delay(1200);
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_VIBRATION, LOW);
        digitalWrite(PIN_STATUS_LED, LOW);
        localServer->sendHeader("Access-Control-Allow-Origin", "*");
        localServer->send(200, "application/json", "{\"success\":true,\"message\":\"Hardware siren and haptic motor activated on local Wi-Fi!\"}");
    });

    localServer->begin();
    Serial.println("[Setup] Local HTTP server active on port 80");
    Serial.println("[Setup] System Initialization Complete. Wearable Active.\n");
    Serial.flush();

    Serial.println("Available Serial Commands:");
    Serial.println("  't' -> Simulate Touch SOS");
    Serial.println("  'c' -> Simulate 3-Clap SOS");
    Serial.println("  'f' -> Simulate Fall SOS");
    Serial.println("  'r' -> Reset / Cancel SOS Alarm\n");
    Serial.flush();
}

void loop() {
    unsigned long now = millis();

    // 1. Maintain WiFi Router Connection (if configured)
    if (String(WIFI_SSID) != "YOUR_WIFI_NAME" && WiFi.status() != WL_CONNECTED) {
        static unsigned long lastReconnect = 0;
        if (now - lastReconnect > 20000) {
            lastReconnect = now;
            Serial.println("[WiFi STA] Reconnecting to router...");
            WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        }
    }

    // 2. Poll GPS Module (Non-blocking character stream)
    pollGPS();

    // 3. TTP223 Touch SOS Check (Quick Click & Hold SOS with Instant Feedback)
    bool touchState = (digitalRead(PIN_TOUCH_SENSOR) == HIGH);
    static unsigned long lastTapTime = 0;
    static int tapCount = 0;

    if (touchState) {
        digitalWrite(PIN_STATUS_LED, HIGH); // Instant visual feedback when touched!
        if (!touchPressed) {
            touchPressed = true;
            touchStartTime = now;
            Serial.println("\n[Touch] 👆 Touch Sensor Contact! (Hold 0.7s or Double-Tap for SOS)");
            pulseHaptic(40); // Quick tactile confirmation tick
        } else if (now - touchStartTime >= TOUCH_HOLD_TRIGGER_MS) {
            Serial.println("\n[Touch] 🚨 Long-press SOS Threshold Reached! 🚨");
            triggerEmergencySOS("TOUCH", 1.00f);
            touchPressed = false;
        }
    } else {
        digitalWrite(PIN_STATUS_LED, LOW);
        if (touchPressed) {
            unsigned long pressDuration = now - touchStartTime;
            touchPressed = false;
            if (pressDuration > 40 && pressDuration < TOUCH_HOLD_TRIGGER_MS) {
                tapCount++;
                if (tapCount == 1) {
                    lastTapTime = now;
                    Serial.println("[Touch] Single Click / Tap registered.");
                } else if (tapCount >= 2 && (now - lastTapTime < 600)) {
                    Serial.println("\n[Touch] 🚨 Double-Click SOS Triggered! 🚨");
                    triggerEmergencySOS("TOUCH_DOUBLE_TAP", 1.00f);
                    tapCount = 0;
                }
            }
        }
        if (tapCount > 0 && (now - lastTapTime >= 600)) {
            tapCount = 0;
        }
    }

    // 4. MPU-6050 Motion Anomaly Check (Only if sensor is physically connected)
    if (hasMPU) {
        bool isFall = false, isStruggle = false;
        float aMag = 0, gMag = 0;
        checkMotionEvents(isFall, isStruggle, aMag, gMag);
        if (isFall) {
            Serial.printf("[Motion] Fall Detected! (Accel: %.2f G)\n", aMag);
            triggerEmergencySOS("MOTION_FALL", 0.90f);
        } else if (isStruggle) {
            Serial.printf("[Motion] Struggle Detected! (Gyro: %.2f deg/s)\n", gMag);
            triggerEmergencySOS("MOTION_STRUGGLE", 0.85f);
        }
    }

    // 5. Update Actuator Alarms
    updateAlarmActuators();

    // 6. Periodic Heartbeat
    if (now - lastHeartbeatTime >= INTERVAL_HEARTBEAT) {
        lastHeartbeatTime = now;
        sendCloudHeartbeat();
    }

    // 7. Periodic GPS Push (Higher frequency if SOS is active)
    unsigned long gpsInterval = emergencyActive ? INTERVAL_EMERGENCY_GPS : INTERVAL_NORMAL_GPS;
    if (now - lastGpsPushTime >= gpsInterval) {
        lastGpsPushTime = now;
        sendGPSTelemetry();
    }

    // 8. Service local Wi-Fi HTTP requests from mobile app on same network
    if (localServer != nullptr) {
        localServer->handleClient();
    }

    // 9. Process Serial Testing Commands
    if (Serial.available()) {
        char cmd = (char)Serial.read();
        switch (cmd) {
            case 't':
            case 'T':
                triggerEmergencySOS("TOUCH_TEST", 1.0f);
                break;
            case 'c':
            case 'C':
                triggerEmergencySOS("CLAP_TEST", 0.95f);
                break;
            case 'f':
            case 'F':
                triggerEmergencySOS("FALL_TEST", 0.90f);
                break;
            case 'r':
            case 'R':
                emergencyActive = false;
                initActuators();
                Serial.println("[Serial] Emergency SOS alarm cancelled & silenced.");
                break;
            default:
                break;
        }
    }

    delay(10);
}
