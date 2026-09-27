#ifndef SAHELI_STREAM_SERVER_H
#define SAHELI_STREAM_SERVER_H

#include <Arduino.h>
#include "esp_http_server.h"
#include "camera_config.h"
#include "camera_driver.h"

class StreamServer {
public:
    static bool startServer();
    static void stopServer();
    static bool isRunning();

private:
    static httpd_handle_t _streamHttpd;
    static esp_err_t streamHandler(httpd_req_t *req);
    static esp_err_t captureHandler(httpd_req_t *req);
    static esp_err_t statusHandler(httpd_req_t *req);
};

#endif // SAHELI_STREAM_SERVER_H
