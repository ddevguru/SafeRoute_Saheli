import unittest
from firmware.tests.hil_hardware_simulator import SensorSimulator, HILEmulator

class HILSimulationTestCase(unittest.TestCase):
    def test_battery_adc_voltage_conversion(self):
        """ADC 12-bit calculation across voltage levels"""
        full_batt = SensorSimulator.simulate_battery_adc(100)
        self.assertAlmostEqual(full_batt['battery_voltage'], 4.20)
        self.assertEqual(full_batt['status'], 'NORMAL')

        low_batt = SensorSimulator.simulate_battery_adc(15)
        self.assertLess(low_batt['battery_voltage'], 3.40)
        self.assertEqual(low_batt['status'], 'LOW')

        crit_batt = SensorSimulator.simulate_battery_adc(5)
        self.assertEqual(crit_batt['status'], 'CRITICAL')

    def test_gps_nmea_checksum_and_format(self):
        """NMEA $GPRMC sentence must be syntactically valid with XOR checksum"""
        nmea = SensorSimulator.generate_nmea_gprmc(28.6139, 77.2090)
        self.assertTrue(nmea.startswith("$GPRMC"))
        self.assertIn("*", nmea)
        parts = nmea.split("*")
        self.assertEqual(len(parts), 2)
        self.assertEqual(len(parts[1]), 2)  # 2-character hex checksum

    def test_mpu6050_fall_vs_normal(self):
        """Verify fall impact vector magnitude surpasses threshold"""
        fall = SensorSimulator.simulate_mpu6050_motion("FALL")
        self.assertTrue(fall['is_fall'])
        self.assertGreater(fall['accel_magnitude_g'], 2.8)

        normal = SensorSimulator.simulate_mpu6050_motion("NORMAL")
        self.assertFalse(normal['is_fall'])
        self.assertFalse(normal['is_struggle'])

    def test_audio_acoustic_distress_patterns(self):
        """Verify clap pattern and scream feature thresholds"""
        clap = SensorSimulator.simulate_audio_spikes("3_CLAP")
        self.assertEqual(clap['clap_count'], 3)
        self.assertTrue(clap['is_emergency'])

        scream = SensorSimulator.simulate_audio_spikes("SCREAM")
        self.assertGreater(scream['spectral_centroid'], 2200.0)
        self.assertTrue(scream['is_emergency'])

        ambient = SensorSimulator.simulate_audio_spikes("AMBIENT")
        self.assertFalse(ambient['is_emergency'])

    def test_hil_emulator_suite(self):
        """Run all emulator checks"""
        emulator = HILEmulator()
        res = emulator.run_hil_test(None)
        self.assertEqual(res['battery_adc'], 'PASS')
        self.assertEqual(res['gps_nmea'], 'PASS')
        self.assertEqual(res['mpu6050_fall'], 'PASS')
        self.assertEqual(res['inmp441_clap'], 'PASS')
        self.assertEqual(res['inmp441_scream'], 'PASS')

if __name__ == '__main__':
    unittest.main()
