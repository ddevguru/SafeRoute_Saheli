class EmergencyIncidentModel {
  final String id;
  final String userId;
  final String? userName;
  final String? deviceId;
  final String triggerType;
  final String status;
  final double latitude;
  final double longitude;
  final int batteryPercent;
  final double confidence;
  final String? startedAt;
  final String? trackingUrl;

  EmergencyIncidentModel({
    required this.id,
    required this.userId,
    this.userName,
    this.deviceId,
    required this.triggerType,
    required this.status,
    required this.latitude,
    required this.longitude,
    required this.batteryPercent,
    required this.confidence,
    this.startedAt,
    this.trackingUrl,
  });

  factory EmergencyIncidentModel.fromJson(Map<String, dynamic> json) {
    return EmergencyIncidentModel(
      id: json['id'] ?? json['incident_id'] ?? '',
      userId: json['user_id'] ?? '',
      userName: json['user_name'],
      deviceId: json['device_id'],
      triggerType: json['trigger_type'] ?? 'BUTTON',
      status: json['status'] ?? 'ACTIVE',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      batteryPercent: json['battery_percent'] ?? 100,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 1.0,
      startedAt: json['started_at'],
      trackingUrl: json['tracking_url'],
    );
  }
}
