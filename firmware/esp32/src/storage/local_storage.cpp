#include "local_storage.h"

const char* LocalStorage::QUEUE_FILE = "/emergency_queue.json";

bool LocalStorage::begin() {
    if (!SPIFFS.begin(true)) {
        return false;
    }
    return true;
}

bool LocalStorage::queueEmergency(const QueuedEmergency& event) {
    DynamicJsonDocument doc(4096);

    // Read existing file if present
    if (SPIFFS.exists(QUEUE_FILE)) {
        File f = SPIFFS.open(QUEUE_FILE, "r");
        if (f) {
            deserializeJson(doc, f);
            f.close();
        }
    }

    JsonArray array = doc.as<JsonArray>();
    if (array.isNull()) {
        array = doc.to<JsonArray>();
    }

    JsonObject item = array.createNestedObject();
    item["trigger"] = event.triggerType;
    item["lat"] = event.latitude;
    item["lng"] = event.longitude;
    item["battery"] = event.batteryPercent;
    item["time"] = event.timestamp;

    File f = SPIFFS.open(QUEUE_FILE, "w");
    if (!f) return false;

    serializeJson(doc, f);
    f.close();
    return true;
}

bool LocalStorage::hasQueuedEvents() {
    if (!SPIFFS.exists(QUEUE_FILE)) return false;
    File f = SPIFFS.open(QUEUE_FILE, "r");
    if (!f) return false;
    size_t sz = f.size();
    f.close();
    return sz > 10;
}

size_t LocalStorage::getQueuedEvents(QueuedEmergency* outEvents, size_t maxCount) {
    if (!SPIFFS.exists(QUEUE_FILE)) return 0;

    File f = SPIFFS.open(QUEUE_FILE, "r");
    if (!f) return 0;

    DynamicJsonDocument doc(4096);
    DeserializationError err = deserializeJson(doc, f);
    f.close();

    if (err) return 0;

    JsonArray array = doc.as<JsonArray>();
    size_t count = 0;
    for (JsonObject item : array) {
        if (count >= maxCount) break;
        outEvents[count].triggerType = item["trigger"].as<String>();
        outEvents[count].latitude = item["lat"].as<double>();
        outEvents[count].longitude = item["lng"].as<double>();
        outEvents[count].batteryPercent = item["battery"].as<int>();
        outEvents[count].timestamp = item["time"].as<uint32_t>();
        count++;
    }

    return count;
}

void LocalStorage::clearQueue() {
    if (SPIFFS.exists(QUEUE_FILE)) {
        SPIFFS.remove(QUEUE_FILE);
    }
}
