class AppConfig {
  static const String appName = 'SafeRoute Saheli';
  static const String tagline = 'Stay Connected. Stay Aware. Stay Safe.';
  static const String appVersion = '1.0.0';

  // Base API URL (Auto-selects 10.0.2.2 for Android Emulator, localhost for Desktop/Web)
  static String baseUrl = 'http://127.0.0.1:5000/api';
  static String wsUrl = 'http://127.0.0.1:5000';

  // Fallback for Android Emulator:
  static void setAndroidEmulatorHost() {
    baseUrl = 'http://10.0.2.2:5000/api';
    wsUrl = 'http://10.0.2.2:5000';
  }

  // IoT Hardware & Emergency Timing Constants
  static const int emergencyLocationIntervalSeconds = 5;
  static const int normalLocationIntervalSeconds = 25;
  static const int emergencyHoldDurationMilliseconds = 2500; // 2.5 seconds press-and-hold
  static const int cameraStreamRefreshSeconds = 5;
}
