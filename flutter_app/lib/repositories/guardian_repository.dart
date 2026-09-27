import '../models/guardian_model.dart';
import '../services/api_service.dart';
import '../storage/secure_storage_service.dart';

class GuardianRepository {
  final ApiService _apiService;

  GuardianRepository({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  Future<List<GuardianModel>> getGuardians() async {
    final response = await _apiService.get('/guardians');
    final list = response['guardians'] as List? ?? [];
    return list.map((item) => GuardianModel.fromJson(item)).toList();
  }

  Future<GuardianModel> addGuardian({
    required String name,
    required String relationship,
    required String phone,
    required String email,
    String? username,
    String? password,
    bool isPrimary = false,
    bool canViewCamera = false,
    bool canViewLocation = true,
  }) async {
    final response = await _apiService.post('/guardians', body: {
      'name': name,
      'relationship': relationship,
      'phone': phone,
      'email': email,
      if (username != null && username.isNotEmpty) 'username': username,
      if (password != null && password.isNotEmpty) 'password': password,
      'is_primary': isPrimary,
      'can_view_camera': canViewCamera,
      'can_view_location': canViewLocation,
    });
    return GuardianModel.fromJson(response['guardian']);
  }

  Future<void> updatePermissions(String guardianId, {
    bool? canViewCamera,
    bool? canViewLocation,
    bool? isPrimary,
  }) async {
    await _apiService.put('/guardians/$guardianId', body: {
      if (canViewCamera != null) 'can_view_camera': canViewCamera,
      if (canViewLocation != null) 'can_view_location': canViewLocation,
      if (isPrimary != null) 'is_primary': isPrimary,
    });
  }

  Future<void> removeGuardian(String guardianId) async {
    await _apiService.delete('/guardians/$guardianId');
  }

  // Guardian login
  Future<GuardianModel> guardianLogin({
    required String identifier,
    required String password,
  }) async {
    final response = await _apiService.post('/guardians/login', body: {
      'username': identifier,
      'password': password,
    }, requireAuth: false);

    final accessToken = response['access_token'];
    final refreshToken = response['refresh_token'];
    final guardianJson = response['guardian'];

    await SecureStorageService.saveAccessToken(accessToken);
    await SecureStorageService.saveRefreshToken(refreshToken);
    await SecureStorageService.saveUserRole('GUARDIAN');

    return GuardianModel.fromJson(guardianJson);
  }

  // Fetch list of monitored Saheli users for this Guardian
  Future<List<Map<String, dynamic>>> getMonitoredSahelis() async {
    final response = await _apiService.get('/guardians/saheli-list');
    return List<Map<String, dynamic>>.from(response['sahelis'] ?? []);
  }
}
