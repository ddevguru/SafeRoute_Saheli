import '../models/emergency_incident_model.dart';
import '../services/api_service.dart';
import '../storage/secure_storage_service.dart';
import '../storage/offline_cache_service.dart';

class EmergencyRepository {
  final ApiService _apiService;

  EmergencyRepository({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  Future<EmergencyIncidentModel> triggerEmergency({
    required String triggerType,
    required double latitude,
    required double longitude,
    int batteryPercent = 100,
    double confidence = 1.0,
  }) async {
    try {
      final response = await _apiService.post('/emergency/trigger', body: {
        'trigger_type': triggerType,
        'latitude': latitude,
        'longitude': longitude,
        'battery_percent': batteryPercent,
        'confidence': confidence,
      });

      final incident = EmergencyIncidentModel(
        id: response['incident_id'] ?? '',
        userId: '',
        triggerType: triggerType,
        status: response['status'] ?? 'ACTIVE',
        latitude: latitude,
        longitude: longitude,
        batteryPercent: batteryPercent,
        confidence: confidence,
        trackingUrl: response['tracking_url'],
      );

      await SecureStorageService.saveActiveIncidentId(incident.id);
      return incident;
    } catch (_) {
      // Offline fallback: Generate cellular SMS emergency format & enqueue locally
      final userData = await SecureStorageService.getUserData();
      final userPhone = userData?['phone'] ?? '+919999999999';
      final smsPayload = OfflineCacheService.formatCellularEmergencySms(
        userPhone: userPhone,
        latitude: latitude,
        longitude: longitude,
        triggerType: triggerType,
        batteryPercent: batteryPercent,
      );

      final offlineIncident = EmergencyIncidentModel(
        id: 'offline-${DateTime.now().millisecondsSinceEpoch}',
        userId: userData?['id'] ?? 'offline_user',
        userName: userData?['name'],
        triggerType: 'OFFLINE_SMS_$triggerType',
        status: 'PENDING_OFFLINE',
        latitude: latitude,
        longitude: longitude,
        batteryPercent: batteryPercent,
        confidence: confidence,
        trackingUrl: 'SMS:$smsPayload',
      );

      await OfflineCacheService.enqueuePendingEmergency(offlineIncident);
      await SecureStorageService.saveActiveIncidentId(offlineIncident.id);
      return offlineIncident;
    }
  }

  Future<EmergencyIncidentModel?> getActiveEmergency() async {
    try {
      final response = await _apiService.get('/emergency/active');
      if (response['active'] == true && response['incident'] != null) {
        final incident = EmergencyIncidentModel.fromJson(response['incident']);
        await SecureStorageService.saveActiveIncidentId(incident.id);
        return incident;
      }
      await SecureStorageService.clearActiveIncident();
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<bool> cancelEmergency(String incidentId, {String reason = "User confirmed safe"}) async {
    final response = await _apiService.post('/emergency/$incidentId/cancel', body: {
      'reason': reason,
    });
    if (response['success'] == true) {
      await SecureStorageService.clearActiveIncident();
      return true;
    }
    return false;
  }

  Future<void> updateLocation({
    required double latitude,
    required double longitude,
    double accuracy = 5.0,
    int battery = 100,
  }) async {
    await _apiService.post('/location/update', body: {
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'battery': battery,
    });
  }
}
