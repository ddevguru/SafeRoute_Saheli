#ifndef SAHELI_CAM_DIAGNOSTICS_H
#define SAHELI_CAM_DIAGNOSTICS_H

#include <Arduino.h>
#include "camera_config.h"

class Diagnostics {
public:
    static void sendHeartbeat();
    static void printDiagnostics();
    static bool isHealthy();
};

#endif // SAHELI_CAM_DIAGNOSTICS_H
