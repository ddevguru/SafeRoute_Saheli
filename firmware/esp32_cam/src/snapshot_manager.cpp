#include "snapshot_manager.h"
#include <WiFi.h>

static const char* MULTIPART_BOUNDARY = "----SaheliCamBoundary2026";

bool SnapshotManager::sendMultipartImage(camera_fb_t* fb, const String& endpoint) {
    if (!fb || WiFi.status() != WL_CONNECTED) {
        return false;
    }

    // Extract host and port from BACKEND_BASE_URL (e.g. http://192.168.1.100:5000/api)
    String url = String(BACKEND_BASE_URL);
    String host = "192.168.1.100";
    uint16_t port = 5000;
    String basePath = "/api";

    int protoIdx = url.indexOf("://");
    if (protoIdx != -1) {
        String remain = url.substring(protoIdx + 3);
        int slashIdx = remain.indexOf('/');
        String hostPort = (slashIdx != -1) ? remain.substring(0, slashIdx) : remain;
        basePath = (slashIdx != -1) ? remain.substring(slashIdx) : "";

        int colonIdx = hostPort.indexOf(':');
        if (colonIdx != -1) {
            host = hostPort.substring(0, colonIdx);
            port = hostPort.substring(colonIdx + 1).toInt();
        } else {
            host = hostPort;
            port = 80;
        }
    }

    String fullPath = basePath + endpoint;

    WiFiClient client;
    if (!client.connect(host.c_str(), port)) {
        Serial.printf("[SnapshotManager] Failed to connect to %s:%d\n", host.c_str(), port);
        return false;
    }

    // Construct Body Parts
    String head = "";
    head += String("--") + MULTIPART_BOUNDARY + "\r\n";
    head += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    head += String(DEVICE_ID) + "\r\n";

    head += String("--") + MULTIPART_BOUNDARY + "\r\n";
    head += "Content-Disposition: form-data; name=\"device_secret\"\r\n\r\n";
    head += String(DEVICE_SECRET) + "\r\n";

    head += String("--") + MULTIPART_BOUNDARY + "\r\n";
    head += "Content-Disposition: form-data; name=\"image\"; filename=\"evidence.jpg\"\r\n";
    head += "Content-Type: image/jpeg\r\n\r\n";

    String tail = String("\r\n--") + MULTIPART_BOUNDARY + "--\r\n";

    size_t totalLen = head.length() + fb->len + tail.length();

    // Send HTTP Headers
    client.printf("POST %s HTTP/1.1\r\n", fullPath.c_str());
    client.printf("Host: %s:%d\r\n", host.c_str(), port);
    client.printf("Content-Type: multipart/form-data; boundary=%s\r\n", MULTIPART_BOUNDARY);
    client.printf("Content-Length: %u\r\n", totalLen);
    client.print("Connection: close\r\n\r\n");

    // Send Payload
    client.print(head);
    client.write(fb->buf, fb->len);
    client.print(tail);

    // Read Response Header Code
    unsigned long timeout = millis();
    while (client.available() == 0) {
        if (millis() - timeout > 5000) {
            Serial.println("[SnapshotManager] HTTP upload response timeout!");
            client.stop();
            return false;
        }
        delay(10);
    }

    String statusLine = client.readStringUntil('\r');
    bool success = (statusLine.indexOf("200") != -1 || statusLine.indexOf("201") != -1);

    client.stop();
    Serial.printf("[SnapshotManager] Upload %s: %s\n", fullPath.c_str(), success ? "SUCCESS" : "FAILED");
    return success;
}

bool SnapshotManager::uploadSingleSnapshot(bool isEmergency) {
    if (isEmergency) {
        CameraDriver::setFlashLED(true);
        delay(50); // Let exposure adapt
    }

    camera_fb_t* fb = CameraDriver::captureFrame();
    if (isEmergency) {
        CameraDriver::setFlashLED(false);
    }

    if (!fb) {
        Serial.println("[SnapshotManager] Frame capture failed!");
        return false;
    }

    String endpoint = isEmergency ? "/camera/emergency-capture" : "/camera/capture";
    bool ok = sendMultipartImage(fb, endpoint);
    CameraDriver::releaseFrame(fb);
    return ok;
}

void SnapshotManager::triggerBurstCapture(int frameCount) {
    Serial.printf("\n[SnapshotManager] *** TRIGGERING EMERGENCY BURST: %d FRAMES ***\n", frameCount);
    for (int i = 0; i < frameCount; i++) {
        Serial.printf("[SnapshotManager] Capturing burst frame %d/%d...\n", i + 1, frameCount);
        uploadSingleSnapshot(true);
        delay(BURST_FRAME_DELAY_MS);
    }
    Serial.println("[SnapshotManager] Burst capture sequence complete.\n");
}
