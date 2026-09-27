#ifndef SAHELI_MICROPHONE_H
#define SAHELI_MICROPHONE_H

#include <Arduino.h>
#include <driver/i2s.h>

class MicrophoneSensor {
public:
    MicrophoneSensor(uint8_t sckPin, uint8_t wsPin, uint8_t sdPin);
    bool begin();
    bool updateClapDetection(); // Returns true when valid 3-clap pattern is matched
    int32_t readPeakAmplitude();
    void recordAudioSnippet(uint8_t* buffer, size_t bufferSize);

private:
    uint8_t _sckPin;
    uint8_t _wsPin;
    uint8_t _sdPin;
    bool _initialized;

    // Clap Pattern State Machine
    uint8_t _clapCount;
    uint32_t _lastClapTime;
    uint32_t _firstClapTime;
    uint32_t _lastTriggerTime;

    static const i2s_port_t I2S_PORT = I2S_NUM_0;
    static const int SAMPLE_RATE = 16000;
};

#endif // SAHELI_MICROPHONE_H
