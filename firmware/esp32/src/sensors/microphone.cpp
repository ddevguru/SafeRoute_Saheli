#include "microphone.h"
#include <math.h>

#define CLAP_PEAK_THRESHOLD    14000
#define CLAP_MIN_INTERVAL_MS   160
#define CLAP_MAX_INTERVAL_MS   650
#define CLAP_WINDOW_MS         1400
#define CLAP_COOLDOWN_MS       3500

MicrophoneSensor::MicrophoneSensor(uint8_t sckPin, uint8_t wsPin, uint8_t sdPin)
    : _sckPin(sckPin), _wsPin(wsPin), _sdPin(sdPin), _initialized(false),
      _clapCount(0), _lastClapTime(0), _firstClapTime(0), _lastTriggerTime(0) {}

bool MicrophoneSensor::begin() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = _sckPin,
        .ws_io_num = _wsPin,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = _sdPin
    };

    esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) return false;

    err = i2s_set_pin(I2S_PORT, &pin_config);
    if (err != ESP_OK) return false;

    _initialized = true;
    return true;
}

int32_t MicrophoneSensor::readPeakAmplitude() {
    if (!_initialized) return 0;

    int32_t sample_buffer[128];
    size_t bytes_read = 0;
    i2s_read(I2S_PORT, (char*)sample_buffer, sizeof(sample_buffer), &bytes_read, portMAX_DELAY);

    int32_t maxPeak = 0;
    int samples = bytes_read / sizeof(int32_t);
    for (int i = 0; i < samples; i++) {
        int32_t val = abs(sample_buffer[i] >> 14); // Scale 32-bit sample to 18-bit
        if (val > maxPeak) {
            maxPeak = val;
        }
    }
    return maxPeak;
}

bool MicrophoneSensor::updateClapDetection() {
    uint32_t now = millis();
    if (now - _lastTriggerTime < CLAP_COOLDOWN_MS) {
        return false;
    }

    int32_t peak = readPeakAmplitude();

    // Check if peak exceeds acoustic clap threshold
    if (peak > CLAP_PEAK_THRESHOLD) {
        if (_clapCount == 0) {
            // First clap
            _clapCount = 1;
            _firstClapTime = now;
            _lastClapTime = now;
        } else {
            uint32_t delta = now - _lastClapTime;
            if (delta >= CLAP_MIN_INTERVAL_MS && delta <= CLAP_MAX_INTERVAL_MS) {
                _clapCount++;
                _lastClapTime = now;

                if (_clapCount >= 3) {
                    // Valid 3-clap emergency pattern confirmed!
                    _clapCount = 0;
                    _lastTriggerTime = now;
                    return true;
                }
            }
        }
    }

    // Reset pattern if time window expired
    if (_clapCount > 0 && (now - _firstClapTime > CLAP_WINDOW_MS)) {
        _clapCount = 0;
    }

    return false;
}

void MicrophoneSensor::recordAudioSnippet(uint8_t* buffer, size_t bufferSize) {
    if (!_initialized) return;
    size_t bytes_read = 0;
    i2s_read(I2S_PORT, buffer, bufferSize, &bytes_read, portMAX_DELAY);
}
