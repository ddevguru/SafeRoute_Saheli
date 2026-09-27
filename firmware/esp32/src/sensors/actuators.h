#ifndef SAHELI_ACTUATORS_H
#define SAHELI_ACTUATORS_H

#include <Arduino.h>

class Actuators {
public:
    Actuators(uint8_t buzzerPin, uint8_t vibrationPin, uint8_t ledPin);
    void begin();
    void setAlarmState(bool active);
    void update(); // Must be called in loop when alarm is active
    void pulseVibration(uint16_t durationMs = 250);

private:
    uint8_t _buzzerPin;
    uint8_t _vibrationPin;
    uint8_t _ledPin;
    bool _isAlarmActive;
    uint32_t _lastToggleTime;
    bool _toggleState;
};

#endif // SAHELI_ACTUATORS_H
