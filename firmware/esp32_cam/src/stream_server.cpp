#include "stream_server.h"
#include <WiFi.h>

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t StreamServer::_streamHttpd = nullptr;

esp_err_t StreamServer::streamHandler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t * _jpg_buf = NULL;
    char part_buf[64];

    // Optional query string auth check
    char query[128];
    if (httpd_req_get_url_query_str(req, query, sizeof(query)) == ESP_OK) {
        char keyVal[64];
        if (httpd_query_key_value(query, "key", keyVal, sizeof(keyVal)) == ESP_OK) {
            if (strcmp(keyVal, STREAM_AUTH_KEY) != 0) {
                httpd_resp_send_404(req);
                return ESP_FAIL;
            }
        }
    }

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    while (true) {
        fb = CameraDriver::captureFrame();
        if (!fb) {
            Serial.println("[StreamServer] Camera capture failed during streaming.");
            res = ESP_FAIL;
        } else {
            _jpg_buf_len = fb->len;
            _jpg_buf = fb->buf;
        }

        if (res == ESP_OK) {
            size_t hlen = snprintf(part_buf, 64, _STREAM_PART, _jpg_buf_len);
            res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
            if (res == ESP_OK) {
                res = httpd_resp_send_chunk(req, part_buf, hlen);
            }
            if (res == ESP_OK) {
                res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
            }
        }

        if (fb) {
            CameraDriver::releaseFrame(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if (res != ESP_OK) {
            break;
        }

        if (res != ESP_OK) {
            break;
        }

        // Small yield to let WiFi stack transmit smoothly (~20 FPS)
        vTaskDelay(pdMS_TO_TICKS(40));
    }

    return res;
}

esp_err_t StreamServer::captureHandler(httpd_req_t *req) {
    camera_fb_t *fb = CameraDriver::captureFrame();
    if (!fb) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    CameraDriver::releaseFrame(fb);
    return res;
}

esp_err_t StreamServer::statusHandler(httpd_req_t *req) {
    char jsonBuf[256];
    snprintf(jsonBuf, sizeof(jsonBuf),
        "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"psram\":%s,\"free_psram\":%u,\"free_heap\":%u,\"rssi\":%d}",
        DEVICE_ID, millis() / 1000,
        psramFound() ? "true" : "false",
        psramFound() ? (unsigned int)ESP.getFreePsram() : 0,
        (unsigned int)ESP.getFreeHeap(),
        WiFi.RSSI()
    );

    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, jsonBuf, strlen(jsonBuf));
}

bool StreamServer::startServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = STREAM_SERVER_PORT;
    config.ctrl_port = STREAM_SERVER_PORT + 1;
    config.max_open_sockets = 4;
    config.lru_purge_enable = true;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = streamHandler,
        .user_ctx  = NULL
    };

    httpd_uri_t capture_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = captureHandler,
        .user_ctx  = NULL
    };

    httpd_uri_t status_uri = {
        .uri       = "/status",
        .method    = HTTP_GET,
        .handler   = statusHandler,
        .user_ctx  = NULL
    };

    Serial.printf("[StreamServer] Starting HTTP MJPEG Server on port %d...\n", STREAM_SERVER_PORT);
    if (httpd_start(&_streamHttpd, &config) == ESP_OK) {
        httpd_register_uri_handler(_streamHttpd, &stream_uri);
        httpd_register_uri_handler(_streamHttpd, &capture_uri);
        httpd_register_uri_handler(_streamHttpd, &status_uri);
        Serial.printf("[StreamServer] Stream URL: http://<camera_ip>:%d/stream\n", STREAM_SERVER_PORT);
        return true;
    }

    Serial.println("[StreamServer] Failed to start HTTP server!");
    return false;
}

void StreamServer::stopServer() {
    if (_streamHttpd) {
        httpd_stop(_streamHttpd);
        _streamHttpd = nullptr;
        Serial.println("[StreamServer] Stopped.");
    }
}

bool StreamServer::isRunning() {
    return (_streamHttpd != nullptr);
}
