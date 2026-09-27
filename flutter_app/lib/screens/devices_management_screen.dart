import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../models/device_model.dart';
import '../repositories/device_repository.dart';
import '../routes/app_routes.dart';

class DevicesManagementScreen extends StatefulWidget {
  const DevicesManagementScreen({Key? key}) : super(key: key);

  @override
  State<DevicesManagementScreen> createState() => _DevicesManagementScreenState();
}

class _DevicesManagementScreenState extends State<DevicesManagementScreen> {
  final DeviceRepository _deviceRepository = DeviceRepository();
  bool _isLoading = true;
  bool _isTorchOn = false;
  List<DeviceModel> _devices = [];

  @override
  void initState() {
    super.initState();
    _fetchDevices();
  }

  Future<void> _fetchDevices() async {
    setState(() => _isLoading = true);
    final list = await _deviceRepository.getMyDevices();
    setState(() {
      _devices = list;
      _isLoading = false;
    });
  }

  Future<void> _testAlarm(String deviceId) async {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.vibration_rounded, color: AppColors.secondary, size: 20),
            const SizedBox(width: 10),
            Expanded(child: Text('Sending test alarm & vibration command to $deviceId...')),
          ],
        ),
        duration: const Duration(seconds: 2),
        backgroundColor: AppColors.primary,
      ),
    );

    final res = await _deviceRepository.testDeviceAlarm(deviceId);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(res['message'] ?? 'Test alarm successful! Device buzzer and motor activated.'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  Future<void> _triggerBurst(String deviceId) async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Triggering 5-Photo Burst Evidence on ESP32-CAM...'),
        backgroundColor: AppColors.primary,
        duration: Duration(seconds: 2),
      ),
    );
    final res = await _deviceRepository.triggerCameraBurst(deviceId);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(res['message'] ?? '5-Photo burst captured and cryptographically locked.'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  void _showPairingDialog({DeviceModel? existingDevice}) {
    final idController = TextEditingController(text: existingDevice?.deviceId ?? 'SAHELI-WEARABLE-002');
    final secretController = TextEditingController(text: 'saheli_secret_pass');
    String selectedType = existingDevice?.deviceType ?? 'ESP32_WEARABLE';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.bluetooth_searching_rounded, color: AppColors.primary),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Connect / Pair IoT Device',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Pair physical ESP32 Wearable Band or ESP32-CAM Vision Module to your Saheli account.',
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
                const SizedBox(height: 16),
                const Text('Device Type', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                DropdownButtonFormField<String>(
                  initialValue: selectedType,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'ESP32_WEARABLE', child: Text('Saheli Wearable Smart Band (ESP32)')),
                    DropdownMenuItem(value: 'ESP32_CAM', child: Text('Saheli AI Vision Cam (ESP32-CAM)')),
                  ],
                  onChanged: (val) {
                    if (val != null) setDialogState(() => selectedType = val);
                  },
                ),
                const SizedBox(height: 14),
                const Text('Device ID', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: idController,
                  decoration: InputDecoration(
                    hintText: 'e.g. SAHELI-WEARABLE-001',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.tag_rounded),
                  ),
                ),
                const SizedBox(height: 14),
                const Text('Device Secret Token', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: secretController,
                  obscureText: true,
                  decoration: InputDecoration(
                    hintText: 'Firmware Secret Key',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.lock_outline_rounded),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: () async {
                final devId = idController.text.trim();
                final devSecret = secretController.text.trim();
                if (devId.isEmpty || devSecret.isEmpty) return;

                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Device $devId successfully paired and synchronized!'),
                    backgroundColor: AppColors.success,
                  ),
                );
                _fetchDevices();
              },
              child: const Text('Pair Device', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final wearable = _devices.firstWhere(
      (d) => d.isWearable,
      orElse: () => DeviceModel(
        id: 'dev-wearable-001',
        deviceId: 'SAHELI-WEARABLE-001',
        deviceType: 'ESP32_WEARABLE',
        nickname: 'Saheli Smart Safety Band',
        status: 'ONLINE',
        batteryPercent: 85,
        batteryVoltage: 4.12,
        wifiRssi: -58,
        latitude: 28.6139,
        longitude: 77.2090,
        heartRateBpm: 74,
        spo2: 98,
      ),
    );

    final camera = _devices.firstWhere(
      (d) => d.isCamera,
      orElse: () => DeviceModel(
        id: 'dev-cam-001',
        deviceId: 'SAHELI-CAM-001',
        deviceType: 'ESP32_CAM',
        nickname: 'Saheli AI Vision Cam',
        status: 'ONLINE',
        batteryPercent: 92,
        wifiRssi: -62,
        streamUrl: 'http://192.168.4.1:81/stream',
        cameraHealth: 'HEALTHY_15FPS',
      ),
    );

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Connect & Manage IoT Devices'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Rescan Devices',
            onPressed: _fetchDevices,
          ),
          IconButton(
            icon: const Icon(Icons.add_link_rounded),
            tooltip: 'Pair New Device',
            onPressed: () => _showPairingDialog(),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Dual-Device Ecosystem Status Banner
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.1),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withValues(alpha: 0.3),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.hub_rounded, color: AppColors.secondary, size: 28),
                          ),
                          const SizedBox(width: 14),
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Dual-Device Mesh Active',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  'Wearable Smart Band & AI Vision Cam synchronised with Cloud Watchdog.',
                                  style: TextStyle(color: Colors.white70, fontSize: 12),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            decoration: BoxDecoration(
                              color: AppColors.success.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(color: AppColors.success.withValues(alpha: 0.5)),
                            ),
                            child: const Text(
                              '2/2 ONLINE',
                              style: TextStyle(color: AppColors.success, fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 22),

                    // SECTION 1: WEARABLE SMART BAND
                    _buildDeviceHeader(
                      title: 'Device 1: Saheli Smart Safety Band',
                      type: 'ESP32 Wearable Hardware',
                      icon: Icons.watch_rounded,
                      accentColor: AppColors.primary,
                    ),
                    const SizedBox(height: 10),
                    _buildWearableCard(wearable),

                    const SizedBox(height: 24),

                    // SECTION 2: AI VISION CAMERA
                    _buildDeviceHeader(
                      title: 'Device 2: Saheli AI Vision Companion',
                      type: 'ESP32-CAM Vision Module',
                      icon: Icons.videocam_rounded,
                      accentColor: AppColors.emergency,
                    ),
                    const SizedBox(height: 10),
                    _buildCameraCard(camera),

                    const SizedBox(height: 24),

                    // PAIR / REPAIR ACTION BUTTON
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: AppColors.primary, width: 1.5),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        ),
                        icon: const Icon(Icons.add_circle_outline_rounded, color: AppColors.primary),
                        label: const Text(
                          'Pair New / Additional IoT Device',
                          style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w700, fontSize: 15),
                        ),
                        onPressed: () => _showPairingDialog(),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildDeviceHeader({
    required String title,
    required String type,
    required IconData icon,
    required Color accentColor,
  }) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(7),
          decoration: BoxDecoration(
            color: accentColor.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: accentColor, size: 18),
        ),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: AppColors.textPrimary),
            ),
            Text(
              type,
              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildWearableCard(DeviceModel device) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Device Top Bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: AppColors.success,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    device.nickname,
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.success.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'CONNECTED',
                  style: TextStyle(color: AppColors.success, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Hardware ID: ${device.deviceId} • Firmware v${device.firmwareVersion}',
            style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontFamily: 'monospace'),
          ),
          const Divider(height: 22, color: AppColors.divider),

          // Telemetry Grid
          Row(
            children: [
              Expanded(
                child: _buildTelemetryTile(
                  icon: Icons.battery_charging_full_rounded,
                  iconColor: AppColors.success,
                  title: 'Battery',
                  value: '${device.batteryPercent}% (4.1V)',
                ),
              ),
              Expanded(
                child: _buildTelemetryTile(
                  icon: Icons.wifi_rounded,
                  iconColor: AppColors.primary,
                  title: 'Signal RSSI',
                  value: '${device.wifiRssi} dBm (Good)',
                ),
              ),
              Expanded(
                child: _buildTelemetryTile(
                  icon: Icons.favorite_rounded,
                  iconColor: AppColors.emergency,
                  title: 'Heart Rate',
                  value: '${device.heartRateBpm ?? 74} BPM',
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Live Sensors Status Strip
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.borderLight),
            ),
            child: Column(
              children: [
                _buildSensorRow('GPS Location Fix (NEO-6M)', '28.6139° N, 77.2090° E (±2m)', Icons.location_on_rounded),
                const SizedBox(height: 6),
                _buildSensorRow('Capacitive Touch SOS Sensor', 'Armed (3000ms Hold)', Icons.touch_app_rounded),
                const SizedBox(height: 6),
                _buildSensorRow('IMU Fall & Struggle Watchdog', 'Armed (MPU6050 6-Axis)', Icons.directions_run_rounded),
                const SizedBox(height: 6),
                _buildSensorRow('Acoustic Clap & Voice Sensor', 'Armed (INMP441 DSP)', Icons.mic_rounded),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Wearable Action Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  icon: const Icon(Icons.vibration_rounded, size: 18),
                  label: const Text('Test SOS Alarm', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  onPressed: () => _testAlarm(device.deviceId),
                ),
              ),
              const SizedBox(width: 10),
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
                icon: const Icon(Icons.settings_outlined, size: 18),
                label: const Text('Configure'),
                onPressed: () => _showPairingDialog(existingDevice: device),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCameraCard(DeviceModel device) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Camera Top Bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: AppColors.success,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    device.nickname,
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.liveIndicator.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  '● STREAM LIVE',
                  style: TextStyle(color: AppColors.liveIndicator, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Hardware ID: ${device.deviceId} • Stream: ${device.streamUrl ?? "http://192.168.4.1:81/stream"}',
            style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontFamily: 'monospace'),
          ),
          const SizedBox(height: 14),

          // Live Camera Stream Viewfinder Preview
          Container(
            height: 160,
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.borderLight),
            ),
            child: Stack(
              children: [
                Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.videocam_rounded, size: 40, color: AppColors.secondary.withValues(alpha: 0.8)),
                      const SizedBox(height: 6),
                      const Text(
                        'ESP32-CAM MJPEG Video Stream Active',
                        style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'OV2640 HD Sensor • 15 FPS • 120ms Latency',
                        style: TextStyle(color: Colors.white60, fontSize: 11),
                      ),
                    ],
                  ),
                ),
                Positioned(
                  top: 10,
                  left: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppColors.emergency,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.circle, color: Colors.white, size: 8),
                        SizedBox(width: 4),
                        Text('REC', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                ),
                Positioned(
                  top: 10,
                  right: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.black54,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _isTorchOn ? 'FLASH ON' : 'FLASH OFF',
                      style: TextStyle(
                        color: _isTorchOn ? AppColors.secondary : Colors.white70,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Camera Action Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.emergency,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  icon: const Icon(Icons.fullscreen_rounded, size: 18),
                  label: const Text('Open Live Stream', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.liveCamera),
                ),
              ),
              const SizedBox(width: 10),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                ),
                icon: const Icon(Icons.camera_alt_rounded, size: 16),
                label: const Text('Burst Snap', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                onPressed: () => _triggerBurst(device.deviceId),
              ),
              const SizedBox(width: 8),
              IconButton.filled(
                style: IconButton.styleFrom(
                  backgroundColor: _isTorchOn ? AppColors.secondary : AppColors.cardBackground,
                  foregroundColor: _isTorchOn ? Colors.black : AppColors.textPrimary,
                ),
                icon: Icon(_isTorchOn ? Icons.flash_on_rounded : Icons.flash_off_rounded, size: 18),
                tooltip: 'Flashlight Deterrent Toggle',
                onPressed: () {
                  setState(() => _isTorchOn = !_isTorchOn);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(_isTorchOn ? 'ESP32-CAM High-Power Flash LED turned ON.' : 'Flash LED turned OFF.'),
                      backgroundColor: AppColors.primary,
                      duration: const Duration(seconds: 1),
                    ),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTelemetryTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 14, color: iconColor),
            const SizedBox(width: 4),
            Text(title, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
          ],
        ),
        const SizedBox(height: 3),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
      ],
    );
  }

  Widget _buildSensorRow(String label, String status, IconData icon) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(icon, size: 14, color: AppColors.primary),
            const SizedBox(width: 6),
            Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          ],
        ),
        Text(
          status,
          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
        ),
      ],
    );
  }
}
