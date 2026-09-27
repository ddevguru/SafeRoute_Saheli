import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../storage/secure_storage_service.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class ApiService {
  final http.Client _client = http.Client();

  Future<Map<String, String>> _getHeaders({bool requireAuth = true}) async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (requireAuth) {
      final token = await SecureStorageService.getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  Future<dynamic> get(String endpoint, {bool requireAuth = true}) async {
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    try {
      final headers = await _getHeaders(requireAuth: requireAuth);
      final response = await _client.get(url, headers: headers);
      return _handleResponse(response, () => get(endpoint, requireAuth: requireAuth));
    } on SocketException {
      throw ApiException('Network connection unavailable. Please check your internet or local server.');
    }
  }

  Future<dynamic> post(String endpoint, {Map<String, dynamic>? body, bool requireAuth = true}) async {
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    try {
      final headers = await _getHeaders(requireAuth: requireAuth);
      final response = await _client.post(
        url,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );
      return _handleResponse(response, () => post(endpoint, body: body, requireAuth: requireAuth));
    } on SocketException {
      throw ApiException('Network connection unavailable. Please check your internet or local server.');
    }
  }

  Future<dynamic> put(String endpoint, {Map<String, dynamic>? body, bool requireAuth = true}) async {
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    try {
      final headers = await _getHeaders(requireAuth: requireAuth);
      final response = await _client.put(
        url,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );
      return _handleResponse(response, () => put(endpoint, body: body, requireAuth: requireAuth));
    } on SocketException {
      throw ApiException('Network connection unavailable. Please check your internet or local server.');
    }
  }

  Future<dynamic> delete(String endpoint, {Map<String, dynamic>? body, bool requireAuth = true}) async {
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    try {
      final headers = await _getHeaders(requireAuth: requireAuth);
      final response = await _client.delete(
        url,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );
      return _handleResponse(response, () => delete(endpoint, body: body, requireAuth: requireAuth));
    } on SocketException {
      throw ApiException('Network connection unavailable.');
    }
  }

  dynamic _handleResponse(http.Response response, Future<dynamic> Function() retryCall) {
    dynamic decoded;
    try {
      decoded = jsonDecode(response.body);
    } catch (_) {
      decoded = null;
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    } else if (response.statusCode == 401) {
      final errorMsg = decoded is Map && decoded.containsKey('error')
          ? decoded['error']
          : 'Authentication session expired. Please log in again.';
      throw ApiException(errorMsg, 401);
    } else {
      final message = decoded is Map && decoded.containsKey('error')
          ? decoded['error']
          : 'Request failed with status ${response.statusCode}';
      throw ApiException(message, response.statusCode);
    }
  }
}
