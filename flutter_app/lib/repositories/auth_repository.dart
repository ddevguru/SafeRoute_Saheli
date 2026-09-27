import '../models/user_model.dart';
import '../services/api_service.dart';
import '../storage/secure_storage_service.dart';

class AuthRepository {
  final ApiService _apiService;

  AuthRepository({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  Future<UserModel> register({
    required String name,
    required String email,
    required String phone,
    required String password,
    String? confirmPassword,
    String? dateOfBirth,
    String? bloodGroup,
    String? medicalNotes,
  }) async {
    final response = await _apiService.post('/auth/register', body: {
      'name': name,
      'email': email,
      'phone': phone,
      'password': password,
      'confirm_password': confirmPassword ?? password,
      'date_of_birth': dateOfBirth,
      'emergency_blood_group': bloodGroup,
      'medical_notes': medicalNotes,
    }, requireAuth: false);

    final accessToken = response['access_token'];
    final refreshToken = response['refresh_token'];
    final userJson = response['user'];

    await SecureStorageService.saveAccessToken(accessToken);
    await SecureStorageService.saveRefreshToken(refreshToken);
    await SecureStorageService.saveUserRole('SAHELI');
    await SecureStorageService.saveUserData(userJson);

    return UserModel.fromJson(userJson);
  }

  Future<UserModel> login({
    required String identifier,
    required String password,
  }) async {
    final response = await _apiService.post('/auth/login', body: {
      'email': identifier,
      'password': password,
    }, requireAuth: false);

    final accessToken = response['access_token'];
    final refreshToken = response['refresh_token'];
    final userJson = response['user'];

    await SecureStorageService.saveAccessToken(accessToken);
    await SecureStorageService.saveRefreshToken(refreshToken);
    await SecureStorageService.saveUserRole('SAHELI');
    await SecureStorageService.saveUserData(userJson);

    return UserModel.fromJson(userJson);
  }

  Future<UserModel?> getProfile() async {
    try {
      final response = await _apiService.get('/auth/profile');
      final user = UserModel.fromJson(response['user']);
      await SecureStorageService.saveUserData(response['user']);
      return user;
    } catch (_) {
      final cached = await SecureStorageService.getUserData();
      if (cached != null) return UserModel.fromJson(cached);
      return null;
    }
  }

  Future<UserModel> updateProfile({
    String? name,
    String? phone,
    String? bloodGroup,
    String? medicalNotes,
  }) async {
    final response = await _apiService.put('/auth/profile', body: {
      if (name != null) 'name': name,
      if (phone != null) 'phone': phone,
      if (bloodGroup != null) 'emergency_blood_group': bloodGroup,
      if (medicalNotes != null) 'medical_notes': medicalNotes,
    });
    final user = UserModel.fromJson(response['user']);
    await SecureStorageService.saveUserData(response['user']);
    return user;
  }

  Future<void> logout() async {
    await SecureStorageService.clearAll();
  }
}
