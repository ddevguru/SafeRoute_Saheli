#ifndef SAHELI_EMERGENCY_MANAGER_H
#define SAHELI_EMERGENCY_MANAGER_H

#include <Arduino.h>
#include "../config.h"
#include "../sensors/actuators.h"
#include "../sensors/gps.h"
#include "../sensors/battery.h"

enum EmergencyState {
    STATE_IDLE,
    STATE_TRIGGERED,
    STATE_ACTIVE_ALARM,
    STATE_COOLDOWN
};

class EmergencyManager {
public:
    static void init(Actuators* actuators, GPSSensor* gps, BatteryMonitor* battery);
    static void triggerEmergency(const String& triggerSource, float confidence = 1.0f);
    static void update();
    static bool isEmergencyActive();
    static EmergencyState getState();
    static void cancelEmergency();

private:
    static EmergencyState currentState;
    static unsigned long alarmStartTime;
    static unsigned long lastTriggerTime;
    static String activeTriggerSource;

    static Actuators* _actuators;
    static GPSSensor* _gps;
    static BatteryMonitor* _battery;
};

#endif // SAHELI_EMERGENCY_MANAGER_H
