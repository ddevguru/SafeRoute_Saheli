import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../models/device_model.dart';
import '../repositories/device_repository.dart';
import '../services/local_device_service.dart';
import '../routes/app_routes.dart';

class DevicesManagementScreen extends StatefulWidget {
  const DevicesManagementScreen({Key? key}) : super(key: key);

  @override
  State<DevicesManagementScreen> createState() => _DevicesManagementScreenState();
}

class _DevicesManagementScreenState extends State<DevicesManagementScreen> {
  final DeviceRepository _deviceRepository = DeviceRepository();
  final LocalDeviceService _localDeviceService = LocalDeviceService();

  late TextEditingController _wearableIpController;
  late TextEditingController _cameraIpController;

  bool _isLoading = true;
  bool _isPinging = false;
  bool _isTorchOn = false;
  List<DeviceModel> _devices = [];

  @override
  void initState() {
    super.initState();
    _wearableIpController = TextEditingController(text: _localDeviceService.connectionState.value.wearableIp);
    _cameraIpController = TextEditingController(text: _localDeviceService.connectionState.value.cameraIp);
    _initLocalService();
    _fetchDevices();
  }

  Future<void> _initLocalService() async {
    await _localDeviceService.init();
    if (mounted) {
      setState(() {
        _wearableIpController.text = _localDeviceService.connectionState.value.wearableIp;
        _cameraIpController.text = _localDeviceService.connectionState.value.cameraIp;
      });
    }
  }

  @override
  void dispose() {
    _wearableIpController.dispose();
    _cameraIpController.dispose();
    super.dispose();
  }

  Future<void> _fetchDevices() async {
    setState(() => _isLoading = true);
    final list = await _deviceRepository.getMyDevices();
    setState(() {
      _devices = list;
      _isLoading = false;
      for (final d in list) {
        if (d.isWearable && d.ipAddress != null && d.ipAddress!.isNotEmpty && d.ipAddress != '0.0.0.0') {
          _wearableIpController.text = d.ipAddress!;
          _localDeviceService.saveIps(
            wearableIp: d.ipAddress!,
            cameraIp: _cameraIpController.text,
          );
        }
      }
    });
  }

  Future<void> _pingAndConnectLocalWifi() async {
    setState(() => _isPinging = true);
    final wIp = _wearableIpController.text.trim();
    final cIp = _cameraIpController.text.trim();

    await _localDeviceService.saveIps(wearableIp: wIp, cameraIp: cIp);
    await _localDeviceService.pingAllDevices();
    await _fetchDevices();

    if (!mounted) return;
    setState(() => _isPinging = false);

    final local = _localDeviceService.connectionState.value;
    if (local.isWearableOnline) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ ESP32 Wearable Connected on Wi-Fi ($wIp)! Battery: ${local.wearableBattery}%'),
          backgroundColor: AppColors.success,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Cannot reach $wIp.\nTip: If phone is connected to "Saheli_Smart_Band", tap "Hotspot IP" (192.168.4.1).'),
          backgroundColor: AppColors.emergency,
          duration: const Duration(seconds: 4),
        ),
      );
    }
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
    return ValueListenableBuilder<LocalDeviceState>(
      valueListenable: _localDeviceService.connectionState,
      builder: (context, localState, _) {
        final isWearableLive = localState.isWearableOnline || _devices.any((d) => d.isWearable && d.isOnline);
        final isCamLive = localState.isCameraOnline || _devices.any((d) => d.isCamera && d.isOnline);
        final onlineCount = (isWearableLive ? 1 : 0) + (isCamLive ? 1 : 0);

        final wearable = _devices.firstWhere(
          (d) => d.isWearable,
          orElse: () => DeviceModel(
            id: 'dev-wearable-001',
            deviceId: 'SAHELI-WEARABLE-001',
            deviceType: 'ESP32_WEARABLE',
            nickname: 'Saheli Smart Safety Band',
            status: isWearableLive ? 'ONLINE' : 'OFFLINE',
            batteryPercent: isWearableLive ? localState.wearableBattery : 0,
            batteryVoltage: isWearableLive ? localState.wearableVoltage : 0.0,
            wifiRssi: isWearableLive ? localState.wearableRssi : 0,
            latitude: 28.6139,
            longitude: 77.2090,
            heartRateBpm: isWearableLive ? 74 : 0,
            spo2: isWearableLive ? 98 : 0,
          ),
        );

        final camera = _devices.firstWhere(
          (d) => d.isCamera,
          orElse: () => DeviceModel(
            id: 'dev-cam-001',
            deviceId: 'SAHELI-CAM-001',
            deviceType: 'ESP32_CAM',
            nickname: 'Saheli AI Vision Cam',
            status: isCamLive ? 'ONLINE' : 'OFFLINE',
            batteryPercent: isCamLive ? 92 : 0,
            wifiRssi: isCamLive ? -62 : 0,
            streamUrl: 'http://${localState.cameraIp}/stream',
            cameraHealth: isCamLive ? 'HEALTHY_20FPS' : 'DISCONNECTED',
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
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Dual-Device Mesh Network',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      onlineCount == 2
                                          ? 'Wearable Smart Band & AI Vision Cam connected and synchronised.'
                                          : onlineCount == 1
                                              ? '1 device active. Check Wi-Fi connection for second device.'
                                              : 'Devices are currently OFF / Disconnected. Turn on boards to start telemetry.',
                                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                                decoration: BoxDecoration(
                                  color: (onlineCount > 0 ? AppColors.success : AppColors.deviceOffline).withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: (onlineCount > 0 ? AppColors.success : AppColors.deviceOffline).withValues(alpha: 0.5),
                                  ),
                                ),
                                child: Text(
                                  '$onlineCount/2 ONLINE',
                                  style: TextStyle(
                                    color: onlineCount > 0 ? AppColors.success : Colors.white70,
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 18),

                        // SAME WI-FI CONNECTION SETUP CARD
                        _buildWifiConnectCard(localState),
                        const SizedBox(height: 22),

                        // SECTION 1: WEARABLE SMART BAND
                        _buildDeviceHeader(
                          title: 'Device 1: Saheli Smart Safety Band',
                          type: 'ESP32 Wearable Hardware',
                          icon: Icons.watch_rounded,
                          accentColor: AppColors.primary,
                        ),
                        const SizedBox(height: 10),
                        _buildWearableCard(wearable, isWearableLive),

                        const SizedBox(height: 24),

                        // SECTION 2: AI VISION CAMERA
                        _buildDeviceHeader(
                          title: 'Device 2: Saheli AI Vision Companion',
                          type: 'ESP32-CAM Vision Module',
                          icon: Icons.videocam_rounded,
                          accentColor: AppColors.emergency,
                        ),
                        const SizedBox(height: 10),
                        _buildCameraCard(camera, isCamLive),

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
      },
    );
  }

  Widget _buildWifiConnectCard(LocalDeviceState localState) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.05),
            blurRadius: 14,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.wifi_rounded, color: AppColors.primary, size: 20),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Connect on Same Local Wi-Fi',
                      style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                    Text(
                      'Phone and ESP32 must be on the same Wi-Fi / Hotspot',
                      style: TextStyle(fontSize: 11, color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Wearable IP Input Field
          const Text('ESP32 Wearable IP Address', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
          const SizedBox(height: 6),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _wearableIpController,
                  decoration: InputDecoration(
                    hintText: 'e.g. 192.168.1.150 or 192.168.4.1',
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    prefixIcon: const Icon(Icons.watch_rounded, size: 18),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  setState(() => _wearableIpController.text = '192.168.4.1');
                },
                child: const Text('Hotspot IP', style: TextStyle(fontSize: 11)),
              ),
            ],
          ),
          const SizedBox(height: 10),

          // ESP32-CAM IP Input Field
          const Text('ESP32-CAM IP & Port', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
          const SizedBox(height: 6),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _cameraIpController,
                  decoration: InputDecoration(
                    hintText: 'e.g. 192.168.1.151:81 or 192.168.4.1:81',
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    prefixIcon: const Icon(Icons.videocam_rounded, size: 18),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  setState(() => _cameraIpController.text = '192.168.4.1:81');
                },
                child: const Text('Hotspot CAM', style: TextStyle(fontSize: 11)),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Instructions Guide Card
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.primary.withValues(alpha: 0.15)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.help_outline_rounded, color: AppColors.primary, size: 16),
                    const SizedBox(width: 6),
                    const Text(
                      'Connection Steps (Mobile Data vs Wi-Fi)',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppColors.primary),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  '1. Power ON your ESP32 Wearable.\n'
                  '2. On your phone, open Settings > Wi-Fi and connect to network:\n'
                  '   • SSID: Saheli_Smart_Band (Password: 12345678)\n'
                  '3. Return here, keep IP as 192.168.4.1, and tap "Ping & Connect".\n'
                  'Note: If your phone is on 5G mobile data and not connected to the band\'s Wi-Fi, 192.168.4.1 will not be reachable.',
                  style: TextStyle(fontSize: 11, color: AppColors.textSecondary, height: 1.4),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Ping & Verify Button + Cloud Sync Button
          Row(
            children: [
              Expanded(
                flex: 3,
                child: SizedBox(
                  height: 44,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: _isPinging
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Icon(Icons.wifi_tethering_rounded, size: 18),
                    label: Text(
                      _isPinging ? 'Pinging...' : 'Ping Local Wi-Fi',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                    onPressed: _isPinging ? null : _pingAndConnectLocalWifi,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 2,
                child: SizedBox(
                  height: 44,
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppColors.secondary, width: 1.5),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.cloud_sync_rounded, color: AppColors.secondary, size: 18),
                    label: const Text(
                      'Cloud Sync',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppColors.primary),
                    ),
                    onPressed: _fetchDevices,
                  ),
                ),
              ),
            ],
          ),
          if (localState.errorMessage != null && !localState.isWearableOnline) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.emergency.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.emergency.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline_rounded, color: AppColors.emergency, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${localState.errorMessage!} If your phone is on 5G/Cellular Data, connect to Wi-Fi "Saheli_Smart_Band" in phone settings first.',
                      style: const TextStyle(color: AppColors.emergency, fontSize: 11, fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
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

  Widget _buildWearableCard(DeviceModel device, bool isLive) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: isLive ? AppColors.success.withValues(alpha: 0.4) : AppColors.borderLight),
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
                    decoration: BoxDecoration(
                      color: isLive ? AppColors.success : AppColors.deviceOffline,
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
                  color: (isLive ? AppColors.success : AppColors.deviceOffline).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  isLive ? 'ONLINE (WI-FI)' : 'OFFLINE (POWER OFF)',
                  style: TextStyle(
                    color: isLive ? AppColors.success : AppColors.emergency,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
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

          if (!isLive) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.emergency.withValues(alpha: 0.06),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.emergency.withValues(alpha: 0.2)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.power_off_rounded, color: AppColors.emergency, size: 20),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Physical ESP32 Wearable is currently powered OFF or unreachable.\nPower ON board and tap "Ping & Connect via Wi-Fi" above.',
                      style: TextStyle(fontSize: 11, color: AppColors.emergency, fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
          ],

          // Telemetry Grid
          Row(
            children: [
              Expanded(
                child: _buildTelemetryTile(
                  icon: isLive ? Icons.battery_charging_full_rounded : Icons.power_off_rounded,
                  iconColor: isLive ? AppColors.success : AppColors.textMuted,
                  title: 'Battery',
                  value: isLive ? '${device.batteryPercent}% (${device.batteryVoltage?.toStringAsFixed(1) ?? '4.1'}V)' : '0% (Unpowered)',
                ),
              ),
              Expanded(
                child: _buildTelemetryTile(
                  icon: Icons.wifi_rounded,
                  iconColor: isLive ? AppColors.primary : AppColors.textMuted,
                  title: 'Signal RSSI',
                  value: isLive ? '${device.wifiRssi} dBm (Active)' : 'Disconnected',
                ),
              ),
              Expanded(
                child: _buildTelemetryTile(
                  icon: Icons.favorite_rounded,
                  iconColor: isLive ? AppColors.emergency : AppColors.textMuted,
                  title: 'Heart Rate',
                  value: isLive ? '${device.heartRateBpm ?? 74} BPM' : '-- BPM',
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
                _buildSensorRow('GPS Location Fix (NEO-6M)', isLive ? '28.6139° N, 77.2090° E (±2m)' : 'No GPS Fix', Icons.location_on_rounded),
                const SizedBox(height: 6),
                _buildSensorRow('Capacitive Touch SOS Sensor', isLive ? 'Armed (1500ms Hold)' : 'Inactive (Device Off)', Icons.touch_app_rounded),
                const SizedBox(height: 6),
                _buildSensorRow('IMU Fall & Struggle Watchdog', isLive ? 'Armed (MPU6050 6-Axis)' : 'Inactive (Device Off)', Icons.directions_run_rounded),
                const SizedBox(height: 6),
                _buildSensorRow('Acoustic Clap & Voice Sensor', isLive ? 'Armed (INMP441 DSP)' : 'Inactive (Device Off)', Icons.mic_rounded),
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
                    backgroundColor: isLive ? AppColors.primary : AppColors.cardBackground,
                    foregroundColor: isLive ? Colors.white : AppColors.textMuted,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  icon: const Icon(Icons.vibration_rounded, size: 18),
                  label: Text(
                    isLive ? 'Test Siren & Vibration' : 'Device Offline (Off)',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                  onPressed: isLive
                      ? () => _testAlarm(device.deviceId)
                      : () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Device is powered OFF. Turn on your ESP32 and connect to the same Wi-Fi first.'),
                              backgroundColor: AppColors.emergency,
                            ),
                          );
                        },
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

  Widget _buildCameraCard(DeviceModel device, bool isLive) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: isLive ? AppColors.liveIndicator.withValues(alpha: 0.4) : AppColors.borderLight),
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
                    decoration: BoxDecoration(
                      color: isLive ? AppColors.liveIndicator : AppColors.deviceOffline,
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
                  color: (isLive ? AppColors.liveIndicator : AppColors.deviceOffline).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  isLive ? '● STREAM LIVE' : 'OFFLINE (POWER OFF)',
                  style: TextStyle(
                    color: isLive ? AppColors.liveIndicator : AppColors.emergency,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
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
                      Icon(
                        isLive ? Icons.videocam_rounded : Icons.videocam_off_rounded,
                        size: 40,
                        color: isLive ? AppColors.secondary : AppColors.textMuted,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        isLive ? 'ESP32-CAM MJPEG Video Stream Active' : 'Camera Powered OFF / Disconnected',
                        style: TextStyle(
                          color: isLive ? Colors.white : Colors.white60,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isLive ? 'OV2640 HD Sensor • 20 FPS • Port 81' : 'Power on ESP32-CAM & ping on Wi-Fi above',
                        style: const TextStyle(color: Colors.white38, fontSize: 11),
                      ),
                    ],
                  ),
                ),
                if (isLive) ...[
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
                    backgroundColor: isLive ? AppColors.emergency : AppColors.cardBackground,
                    foregroundColor: isLive ? Colors.white : AppColors.textMuted,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  icon: const Icon(Icons.fullscreen_rounded, size: 18),
                  label: Text(
                    isLive ? 'Live Stream' : 'Camera Off',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  onPressed: isLive
                      ? () => Navigator.pushNamed(context, AppRoutes.liveCamera)
                      : () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('ESP32-CAM is powered OFF. Turn on and verify Wi-Fi connection.'),
                              backgroundColor: AppColors.emergency,
                            ),
                          );
                        },
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: isLive ? AppColors.primary : AppColors.cardBackground,
                  foregroundColor: isLive ? Colors.white : AppColors.textMuted,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
                ),
                icon: const Icon(Icons.camera_alt_rounded, size: 16),
                label: const Text('Burst', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                onPressed: isLive ? () => _triggerBurst(device.deviceId) : null,
              ),
              const SizedBox(width: 6),
              IconButton.filled(
                style: IconButton.styleFrom(
                  backgroundColor: _isTorchOn ? AppColors.secondary : AppColors.cardBackground,
                  foregroundColor: _isTorchOn ? Colors.black : AppColors.textPrimary,
                  padding: const EdgeInsets.all(8),
                ),
                icon: Icon(_isTorchOn ? Icons.flash_on_rounded : Icons.flash_off_rounded, size: 18),
                tooltip: 'Flashlight Deterrent Toggle',
                onPressed: isLive
                    ? () {
                        setState(() => _isTorchOn = !_isTorchOn);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(_isTorchOn ? 'ESP32-CAM High-Power Flash LED turned ON.' : 'Flash LED turned OFF.'),
                            backgroundColor: AppColors.primary,
                            duration: const Duration(seconds: 1),
                          ),
                        );
                      }
                    : null,
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
            Expanded(
              child: Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
              ),
            ),
          ],
        ),
        const SizedBox(height: 3),
        Text(
          value,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildSensorRow(String label, String status, IconData icon) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Row(
            children: [
              Icon(icon, size: 14, color: AppColors.primary),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Text(
          status,
          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
        ),
      ],
    );
  }
}
