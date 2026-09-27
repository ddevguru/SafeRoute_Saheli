#ifndef SAHELI_TOUCH_SENSOR_H
#define SAHELI_TOUCH_SENSOR_H

#include <Arduino.h>

class TouchSensor {
public:
    TouchSensor(uint8_t pin, uint32_t holdTimeMs = 1500);
    void begin();
    bool update(); // Returns true if touch was held continuously for required duration
    bool isCurrentlyTouched() const;
    void reset();

private:
    uint8_t _pin;
    uint32_t _holdTimeMs;
    uint32_t _touchStartTime;
    bool _isHeld;
    bool _hasTriggered;
};

#endif // SAHELI_TOUCH_SENSOR_H
