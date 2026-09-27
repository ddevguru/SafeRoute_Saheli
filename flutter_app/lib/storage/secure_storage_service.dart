import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  static const FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static final Map<String, String> _memoryCache = {};

  static const String _keyAccessToken = 'saheli_access_token';
  static const String _keyRefreshToken = 'saheli_refresh_token';
  static const String _keyUserRole = 'saheli_user_role';
  static const String _keyUserData = 'saheli_user_data';
  static const String _keyActiveIncidentId = 'saheli_active_incident_id';

  static Future<void> _writeSafe(String key, String value) async {
    _memoryCache[key] = value;
    try {
      await _storage.write(key: key, value: value);
    } catch (_) {}
  }

  static Future<String?> _readSafe(String key) async {
    try {
      final val = await _storage.read(key: key);
      if (val != null) return val;
    } catch (_) {}
    return _memoryCache[key];
  }

  static Future<void> _deleteSafe(String key) async {
    _memoryCache.remove(key);
    try {
      await _storage.delete(key: key);
    } catch (_) {}
  }

  // Access Token
  static Future<void> saveAccessToken(String token) async {
    await _writeSafe(_keyAccessToken, token);
  }

  static Future<String?> getAccessToken() async {
    return await _readSafe(_keyAccessToken);
  }

  // Refresh Token
  static Future<void> saveRefreshToken(String token) async {
    await _writeSafe(_keyRefreshToken, token);
  }

  static Future<String?> getRefreshToken() async {
    return await _readSafe(_keyRefreshToken);
  }

  // User Role (SAHELI or GUARDIAN)
  static Future<void> saveUserRole(String role) async {
    await _writeSafe(_keyUserRole, role);
  }

  static Future<String?> getUserRole() async {
    return await _readSafe(_keyUserRole);
  }

  // User Profile Data
  static Future<void> saveUserData(Map<String, dynamic> userMap) async {
    await _writeSafe(_keyUserData, jsonEncode(userMap));
  }

  static Future<Map<String, dynamic>?> getUserData() async {
    final str = await _readSafe(_keyUserData);
    if (str == null) return null;
    try {
      return jsonDecode(str) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  // Active Emergency Incident ID
  static Future<void> saveActiveIncidentId(String incidentId) async {
    await _writeSafe(_keyActiveIncidentId, incidentId);
  }

  static Future<String?> getActiveIncidentId() async {
    return await _readSafe(_keyActiveIncidentId);
  }

  static Future<void> clearActiveIncident() async {
    await _deleteSafe(_keyActiveIncidentId);
  }

  // IoT Device IPs
  static const String _keyWearableIp = 'saheli_wearable_ip';
  static const String _keyCameraIp = 'saheli_camera_ip';

  static Future<void> saveDeviceIps({required String wearableIp, required String cameraIp}) async {
    await _writeSafe(_keyWearableIp, wearableIp);
    await _writeSafe(_keyCameraIp, cameraIp);
  }

  static Future<String?> getWearableIp() async {
    return await _readSafe(_keyWearableIp);
  }

  static Future<String?> getCameraIp() async {
    return await _readSafe(_keyCameraIp);
  }

  // Clear Session
  static Future<void> clearAll() async {
    _memoryCache.clear();
    try {
      await _storage.deleteAll();
    } catch (_) {}
  }
}
