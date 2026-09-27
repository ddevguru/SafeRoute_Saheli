import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/safe_place_model.dart';
import '../models/emergency_incident_model.dart';

class OfflineCacheService {
  static const FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static final Map<String, String> _memoryCache = {};

  static const String _keyCachedSafePlaces = 'saheli_cached_safe_places';
  static const String _keyPendingEmergencyQueue = 'saheli_pending_emergency_queue';

  static Future<void> _safeWrite(String key, String value) async {
    _memoryCache[key] = value;
    try {
      await _storage.write(key: key, value: value);
    } catch (_) {}
  }

  static Future<String?> _safeRead(String key) async {
    try {
      final val = await _storage.read(key: key);
      if (val != null) return val;
    } catch (_) {}
    return _memoryCache[key];
  }

  static Future<void> _safeDelete(String key) async {
    _memoryCache.remove(key);
    try {
      await _storage.delete(key: key);
    } catch (_) {}
  }

  /// Pre-seeded critical emergency points available out-of-the-box in total offline mode
  static final List<SafePlaceModel> defaultEmergencyPlaces = [
    SafePlaceModel(
      id: 'default-police-hq',
      name: 'Delhi Police Central HQ / Women Helpline 1091',
      category: 'POLICE',
      latitude: 28.6289,
      longitude: 77.2065,
      address: 'Jai Singh Road, Connaught Place, New Delhi',
      phoneNumber: '1091',
      distanceMeters: 0.0,
      estimatedTimeMins: 5.0,
    ),
    SafePlaceModel(
      id: 'default-safdarjung-hosp',
      name: 'Safdarjung Hospital Emergency Trauma Center',
      category: 'HOSPITAL',
      latitude: 28.5684,
      longitude: 77.2075,
      address: 'Ring Road, Opposite AIIMS, New Delhi',
      phoneNumber: '102',
      distanceMeters: 0.0,
      estimatedTimeMins: 8.0,
    ),
    SafePlaceModel(
      id: 'default-all-india-shelter',
      name: 'National Women Crisis Intervention & Shelter',
      category: 'SHELTER',
      latitude: 28.6180,
      longitude: 77.2150,
      address: 'Ashoka Road, New Delhi',
      phoneNumber: '181',
      distanceMeters: 0.0,
      estimatedTimeMins: 6.0,
    ),
    SafePlaceModel(
      id: 'default-24x7-pharmacy',
      name: 'Apollo 24x7 Emergency Pharmacy & First Aid',
      category: 'PHARMACY',
      latitude: 28.6250,
      longitude: 77.2180,
      address: 'Connaught Place Outer Circle, New Delhi',
      phoneNumber: '011-23456789',
      distanceMeters: 0.0,
      estimatedTimeMins: 4.0,
    ),
  ];

  /// High-precision Haversine distance in meters
  static double calculateDistanceMeters(double lat1, double lon1, double lat2, double lon2) {
    const double earthRadiusMeters = 6371000.0;
    final dLat = (lat2 - lat1) * (math.pi / 180.0);
    final dLon = (lon2 - lon1) * (math.pi / 180.0);
    final a = math.sin(dLat / 2) * math.sin(dLat / 2) +
        math.cos(lat1 * (math.pi / 180.0)) *
            math.cos(lat2 * (math.pi / 180.0)) *
            math.sin(dLon / 2) *
            math.sin(dLon / 2);
    final c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    return earthRadiusMeters * c;
  }

  /// Caches safe places retrieved when online
  static Future<void> cacheSafePlaces(List<SafePlaceModel> places) async {
    try {
      final listMap = places.map((p) => {
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'latitude': p.latitude,
        'longitude': p.longitude,
        'address': p.address,
        'phone_number': p.phoneNumber,
        'distance_meters': p.distanceMeters,
        'estimated_time_mins': p.estimatedTimeMins,
      }).toList();
      await _safeWrite(_keyCachedSafePlaces, jsonEncode(listMap));
    } catch (_) {}
  }

  /// Retrieves cached safe places and sorts them by proximity using local Haversine distance
  static Future<List<SafePlaceModel>> getCachedSafePlaces({
    double? currentLat,
    double? currentLng,
    String? categoryFilter,
    double maxRadiusMeters = 15000.0,
  }) async {
    List<SafePlaceModel> places = [];

    try {
      final str = await _safeRead(_keyCachedSafePlaces);
      if (str != null && str.isNotEmpty) {
        final List<dynamic> decoded = jsonDecode(str);
        places = decoded.map((item) => SafePlaceModel.fromJson(item as Map<String, dynamic>)).toList();
      }
    } catch (_) {}

    // Fallback to default emergency places if cache is empty
    if (places.isEmpty) {
      places = List.from(defaultEmergencyPlaces);
    }

    // Filter by category if specified
    if (categoryFilter != null && categoryFilter.isNotEmpty && categoryFilter != 'ALL') {
      places = places.where((p) => p.category.toUpperCase() == categoryFilter.toUpperCase()).toList();
    }

    // Recalculate distance and sort by proximity if user coordinates are provided
    if (currentLat != null && currentLng != null) {
      final updated = places.map((place) {
        final dist = calculateDistanceMeters(currentLat, currentLng, place.latitude, place.longitude);
        final timeMins = (dist / 1000.0) / 30.0 * 60.0; // Assume 30 km/h urban transit
        return SafePlaceModel(
          id: place.id,
          name: place.name,
          category: place.category,
          latitude: place.latitude,
          longitude: place.longitude,
          address: place.address,
          phoneNumber: place.phoneNumber,
          distanceMeters: dist,
          estimatedTimeMins: math.max(1.0, double.parse(timeMins.toStringAsFixed(1))),
        );
      }).toList();

      updated.sort((a, b) => a.distanceMeters.compareTo(b.distanceMeters));
      return updated;
    }

    return places;
  }

  /// Formats cellular SMS emergency packet matching backend's /api/emergency/sms-webhook
  static String formatCellularEmergencySms({
    required String userPhone,
    required double latitude,
    required double longitude,
    required String triggerType,
    int batteryPercent = 100,
  }) {
    return 'SR_SOS|$userPhone|${latitude.toStringAsFixed(5)}|${longitude.toStringAsFixed(5)}|$triggerType|$batteryPercent';
  }

  /// Queues an emergency incident locally when device is in zero-internet zone
  static Future<void> enqueuePendingEmergency(EmergencyIncidentModel incident) async {
    try {
      final queue = await getPendingEmergencies();
      queue.add(incident);
      final jsonList = queue.map((inc) => {
        'id': inc.id,
        'user_id': inc.userId,
        'user_name': inc.userName,
        'device_id': inc.deviceId,
        'trigger_type': inc.triggerType,
        'status': inc.status,
        'latitude': inc.latitude,
        'longitude': inc.longitude,
        'battery_percent': inc.batteryPercent,
        'confidence': inc.confidence,
        'started_at': inc.startedAt,
        'tracking_url': inc.trackingUrl,
      }).toList();
      await _safeWrite(_keyPendingEmergencyQueue, jsonEncode(jsonList));
    } catch (_) {}
  }

  /// Retrieves pending offline emergencies
  static Future<List<EmergencyIncidentModel>> getPendingEmergencies() async {
    try {
      final str = await _safeRead(_keyPendingEmergencyQueue);
      if (str == null || str.isEmpty) return [];
      final List<dynamic> list = jsonDecode(str);
      return list.map((item) => EmergencyIncidentModel.fromJson(item as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }

  /// Clears pending emergency queue after successful cloud sync
  static Future<void> clearPendingEmergencies() async {
    await _safeDelete(_keyPendingEmergencyQueue);
  }

  static const String _keyLocalIncidentHistory = 'saheli_local_incident_history';

  /// Records an incident locally so every trigger is preserved in history
  static Future<void> recordLocalIncident(Map<String, dynamic> incident) async {
    try {
      final list = await getLocalIncidentHistory();
      list.insert(0, incident);
      // Keep most recent 50
      if (list.length > 50) list.removeRange(50, list.length);
      await _safeWrite(_keyLocalIncidentHistory, jsonEncode(list));
    } catch (_) {}
  }

  /// Retrieves locally recorded incident triggers
  static Future<List<Map<String, dynamic>>> getLocalIncidentHistory() async {
    try {
      final str = await _safeRead(_keyLocalIncidentHistory);
      if (str != null && str.isNotEmpty) {
        final List<dynamic> decoded = jsonDecode(str);
        return decoded.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Default demonstration seed triggers showing each detection mechanism
  static List<Map<String, dynamic>> getSeedIncidentHistory() {
    return [
      {
        'id': 'INC-TOUCH-9821',
        'trigger_type': 'TOUCH',
        'trigger_label': 'Capacitive Touch 3-Second SOS',
        'status': 'RESOLVED',
        'started_at': '2026-09-27 23:45:10',
        'resolved_at': 'Safe PIN Verified',
        'latitude': 28.6139,
        'longitude': 77.2090,
        'battery_percent': 85,
        'confidence': 0.98,
        'device_id': 'SAHELI-WEARABLE-001',
        'evidence_summary': 'Touch pad sustained press >3000ms. Dispatched GPS & SMS alerts.',
      },
      {
        'id': 'INC-CLAP-9742',
        'trigger_type': 'CLAP',
        'trigger_label': 'Triple-Clap Acoustic Burst Pattern',
        'status': 'RESOLVED',
        'started_at': '2026-09-27 21:18:04',
        'resolved_at': 'User Verified Safe',
        'latitude': 28.6280,
        'longitude': 77.2140,
        'battery_percent': 88,
        'confidence': 0.95,
        'device_id': 'SAHELI-WEARABLE-001',
        'evidence_summary': 'INMP441 detected 3 sharp acoustic transients in 1.4s. Camera burst fired.',
      },
      {
        'id': 'INC-FALL-9610',
        'trigger_type': 'MOTION_FALL',
        'trigger_label': 'MPU6050 Free-Fall + Impact Anomaly',
        'status': 'RESOLVED',
        'started_at': '2026-09-27 18:32:15',
        'resolved_at': 'Resolved by Guardian',
        'latitude': 28.5494,
        'longitude': 77.2001,
        'battery_percent': 91,
        'confidence': 0.92,
        'device_id': 'SAHELI-WEARABLE-001',
        'evidence_summary': '0.12g free-fall followed by 3.8g high-G impact spike & 5s immobility.',
      },
      {
        'id': 'INC-STRUGGLE-9524',
        'trigger_type': 'MOTION_STRUGGLE',
        'trigger_label': 'High-G Struggle & Wrist Jerk Jerk',
        'status': 'RESOLVED',
        'started_at': '2026-09-26 22:10:48',
        'resolved_at': 'Police Patrol Acknowledged',
        'latitude': 28.6310,
        'longitude': 77.2215,
        'battery_percent': 74,
        'confidence': 0.89,
        'device_id': 'SAHELI-WEARABLE-001',
        'evidence_summary': 'Repeated cyclical rotational acceleration >450 deg/s verified by ANFIS classifier.',
      },
      {
        'id': 'INC-BUTTON-9402',
        'trigger_type': 'BUTTON',
        'trigger_label': 'Tactile Wearable Hardware SOS Button',
        'status': 'RESOLVED',
        'started_at': '2026-09-26 14:05:32',
        'resolved_at': 'User Cancelled',
        'latitude': 28.6145,
        'longitude': 77.2085,
        'battery_percent': 96,
        'confidence': 1.0,
        'device_id': 'SAHELI-WEARABLE-001',
        'evidence_summary': 'Instant hardware button interrupt triggered immediate multi-channel dispatch.',
      },
    ];
  }
}
