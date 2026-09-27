#ifndef SAHELI_LOCAL_STORAGE_H
#define SAHELI_LOCAL_STORAGE_H

#include <Arduino.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>

struct QueuedEmergency {
    String triggerType;
    double latitude;
    double longitude;
    int batteryPercent;
    uint32_t timestamp;
};

class LocalStorage {
public:
    static bool begin();
    static bool queueEmergency(const QueuedEmergency& event);
    static bool hasQueuedEvents();
    static size_t getQueuedEvents(QueuedEmergency* outEvents, size_t maxCount);
    static void clearQueue();

private:
    static const char* QUEUE_FILE;
};

#endif // SAHELI_LOCAL_STORAGE_H
