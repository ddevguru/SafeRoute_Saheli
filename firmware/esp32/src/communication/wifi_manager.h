#ifndef SAHELI_WIFI_MANAGER_H
#define SAHELI_WIFI_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include "../config.h"

class WiFiManager {
public:
    static void init();
    static void maintainConnection();
    static bool isConnected();
    static int getRSSI();
    static String getIPAddress();
    static String getMacAddress();

private:
    static unsigned long lastReconnectAttempt;
    static const unsigned long RECONNECT_INTERVAL_MS = 10000;
};

#endif // SAHELI_WIFI_MANAGER_H
