#ifndef SAHELI_SNAPSHOT_MANAGER_H
#define SAHELI_SNAPSHOT_MANAGER_H

#include <Arduino.h>
#include "camera_config.h"
#include "camera_driver.h"

class SnapshotManager {
public:
    static bool uploadSingleSnapshot(bool isEmergency = false);
    static void triggerBurstCapture(int frameCount = BURST_FRAME_COUNT);

private:
    static bool sendMultipartImage(camera_fb_t* fb, const String& endpoint);
};

#endif // SAHELI_SNAPSHOT_MANAGER_H
