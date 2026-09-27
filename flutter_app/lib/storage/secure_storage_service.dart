import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  static const FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const String _keyAccessToken = 'saheli_access_token';
  static const String _keyRefreshToken = 'saheli_refresh_token';
  static const String _keyUserRole = 'saheli_user_role';
  static const String _keyUserData = 'saheli_user_data';
  static const String _keyActiveIncidentId = 'saheli_active_incident_id';

  // Access Token
  static Future<void> saveAccessToken(String token) async {
    await _storage.write(key: _keyAccessToken, value: token);
  }

  static Future<String?> getAccessToken() async {
    return await _storage.read(key: _keyAccessToken);
  }

  // Refresh Token
  static Future<void> saveRefreshToken(String token) async {
    await _storage.write(key: _keyRefreshToken, value: token);
  }

  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: _keyRefreshToken);
  }

  // User Role (SAHELI or GUARDIAN)
  static Future<void> saveUserRole(String role) async {
    await _storage.write(key: _keyUserRole, value: role);
  }

  static Future<String?> getUserRole() async {
    return await _storage.read(key: _keyUserRole);
  }

  // User Profile Data
  static Future<void> saveUserData(Map<String, dynamic> userMap) async {
    await _storage.write(key: _keyUserData, value: jsonEncode(userMap));
  }

  static Future<Map<String, dynamic>?> getUserData() async {
    final str = await _storage.read(key: _keyUserData);
    if (str == null) return null;
    try {
      return jsonDecode(str) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  // Active Emergency Incident ID
  static Future<void> saveActiveIncidentId(String incidentId) async {
    await _storage.write(key: _keyActiveIncidentId, value: incidentId);
  }

  static Future<String?> getActiveIncidentId() async {
    return await _storage.read(key: _keyActiveIncidentId);
  }

  static Future<void> clearActiveIncident() async {
    await _storage.delete(key: _keyActiveIncidentId);
  }

  // Clear Session
  static Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
