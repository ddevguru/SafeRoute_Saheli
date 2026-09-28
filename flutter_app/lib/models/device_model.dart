class DeviceModel {
  final String id;
  final String deviceId;
  final String deviceType; // ESP32_WEARABLE or ESP32_CAM
  final String nickname;
  final String status; // ONLINE or OFFLINE
  final int batteryPercent;
  final double? batteryVoltage;
  final int wifiRssi;
  final String firmwareVersion;
  final bool isPaired;
  final String? lastHeartbeat;
  final String? streamUrl;
  final String? cameraHealth;
  final double? latitude;
  final double? longitude;
  final int? heartRateBpm;
  final int? spo2;
  final String? ipAddress;
  final Map<String, dynamic> sensors;

  DeviceModel({
    required this.id,
    required this.deviceId,
    required this.deviceType,
    required this.nickname,
    required this.status,
    this.batteryPercent = 100,
    this.batteryVoltage,
    this.wifiRssi = -60,
    this.firmwareVersion = '1.0.0',
    this.isPaired = true,
    this.lastHeartbeat,
    this.streamUrl,
    this.cameraHealth,
    this.latitude,
    this.longitude,
    this.heartRateBpm,
    this.spo2,
    this.ipAddress,
    this.sensors = const {},
  });

  bool get isOnline => status.toUpperCase() == 'ONLINE';
  bool get isWearable => deviceType.toUpperCase().contains('WEARABLE');
  bool get isCamera => deviceType.toUpperCase().contains('CAM');

  factory DeviceModel.fromJson(Map<String, dynamic> json) {
    return DeviceModel(
      id: json['id'] ?? json['device_id'] ?? '',
      deviceId: json['device_id'] ?? '',
      deviceType: json['device_type'] ?? 'ESP32_WEARABLE',
      nickname: json['nickname'] ?? 'Saheli Device',
      status: json['status'] ?? 'ONLINE',
      batteryPercent: json['battery_percent'] ?? 100,
      batteryVoltage: (json['battery_voltage'] as num?)?.toDouble(),
      wifiRssi: json['wifi_rssi'] ?? -60,
      firmwareVersion: json['firmware_version'] ?? '1.0.0',
      isPaired: json['is_paired'] ?? true,
      lastHeartbeat: json['last_heartbeat'],
      streamUrl: json['stream_url'],
      cameraHealth: json['camera_health'],
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      heartRateBpm: json['heart_rate_bpm'],
      spo2: json['spo2'],
      ipAddress: json['ip_address'],
      sensors: json['sensors'] != null ? Map<String, dynamic>.from(json['sensors']) : {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_id': deviceId,
      'device_type': deviceType,
      'nickname': nickname,
      'status': status,
      'battery_percent': batteryPercent,
      'battery_voltage': batteryVoltage,
      'wifi_rssi': wifiRssi,
      'firmware_version': firmwareVersion,
      'is_paired': isPaired,
      'last_heartbeat': lastHeartbeat,
      'stream_url': streamUrl,
      'camera_health': cameraHealth,
      'latitude': latitude,
      'longitude': longitude,
      'heart_rate_bpm': heartRateBpm,
      'spo2': spo2,
      'sensors': sensors,
    };
  }
}
