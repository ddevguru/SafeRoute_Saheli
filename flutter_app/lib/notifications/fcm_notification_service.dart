import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class FcmNotificationService {
  static final ApiService _apiService = ApiService();

  // High-priority siren notification channel for Android 8+
  static const String emergencyChannelId = 'emergency_channel';
  static const String emergencyChannelName = '🚨 SafeRoute Saheli Emergency Alert';
  static const String emergencyChannelDescription = 'Critical high-priority siren notifications when a Saheli triggers an emergency.';

  // Stream controller to broadcast incoming push notifications to UI components
  static final StreamController<Map<String, dynamic>> _payloadStreamController =
      StreamController<Map<String, dynamic>>.broadcast();

  static Stream<Map<String, dynamic>> get payloadStream => _payloadStreamController.stream;

  /// Initialize notification listeners and channels
  static Future<void> initialize() async {
    debugPrint('[FCM] Notification service initialized with high-priority channel: $emergencyChannelId');
  }

  /// Register or update FCM Token with backend for Guardian or Saheli
  static Future<bool> syncDeviceToken(String fcmToken) async {
    try {
      final platform = defaultTargetPlatform == TargetPlatform.iOS
          ? 'IOS'
          : (kIsWeb ? 'WEB' : 'ANDROID');

      final response = await _apiService.post('/notifications/tokens', body: {
        'fcm_token': fcmToken,
        'platform': platform,
      });

      if (response['success'] == true) {
        debugPrint('[FCM] Device push token synced successfully: ${fcmToken.substring(0, fcmToken.length > 10 ? 10 : fcmToken.length)}...');
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('[FCM] Token sync warning: $e');
      return false;
    }
  }

  /// Revoke device token on logout
  static Future<void> revokeDeviceToken(String fcmToken) async {
    try {
      await _apiService.delete('/notifications/tokens', body: {
        'fcm_token': fcmToken,
      });
      debugPrint('[FCM] Device token revoked from cloud.');
    } catch (e) {
      debugPrint('[FCM] Error revoking token: $e');
    }
  }

  /// Handle incoming foreground or background message payload
  static void handleNotificationPayload(Map<String, dynamic> data) {
    debugPrint('[FCM] Incoming payload: ${jsonEncode(data)}');

    final type = data['type'] ?? 'EMERGENCY_ALERT';
    _payloadStreamController.add(data);

    switch (type) {
      case 'EMERGENCY_ALERT':
        _handleEmergencyAlert(data);
        break;
      case 'BATTERY_WARNING':
        _handleBatteryWarning(data);
        break;
      case 'ROUTE_DEVIATION':
        _handleRouteDeviation(data);
        break;
      case 'DEVICE_OFFLINE':
        _handleDeviceOffline(data);
        break;
      default:
        debugPrint('[FCM] Generic notification received: $type');
    }
  }

  static void _handleEmergencyAlert(Map<String, dynamic> data) {
    final incidentId = data['incident_id'];
    final triggerType = data['trigger_type'];
    final latitude = data['latitude'];
    final longitude = data['longitude'];
    final trackingToken = data['tracking_token'];
    final trackingUrl = data['tracking_url'];

    debugPrint('🚨 [EMERGENCY NOTIFICATION] Incident: $incidentId | Trigger: $triggerType | Coords: $latitude, $longitude | URL: $trackingUrl | Token: $trackingToken');
  }

  static void _handleBatteryWarning(Map<String, dynamic> data) {
    final percent = data['battery_percent'];
    final isCritical = data['is_critical'] == 'True' || data['is_critical'] == 'true';
    debugPrint('🔋 [BATTERY WARNING] Level: $percent% | Critical: $isCritical');
  }

  static void _handleRouteDeviation(Map<String, dynamic> data) {
    final deviation = data['deviation_meters'];
    final routeId = data['route_id'];
    debugPrint('⚠️ [ROUTE DEVIATION] Deviation: ${deviation}m on Route: $routeId');
  }

  static void _handleDeviceOffline(Map<String, dynamic> data) {
    final deviceId = data['device_id'];
    final lastSeen = data['last_seen'];
    debugPrint('📡 [DEVICE OFFLINE] Device: $deviceId | Last Seen: $lastSeen');
  }

  /// Dispose stream on teardown if required
  static void dispose() {
    _payloadStreamController.close();
  }
}
