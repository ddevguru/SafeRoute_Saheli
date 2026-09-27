import '../models/safe_place_model.dart';
import '../services/api_service.dart';
import '../storage/offline_cache_service.dart';

class RoutingRepository {
  final ApiService _apiService;

  RoutingRepository({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  Future<List<SafePlaceModel>> getNearbyPolice({double lat = 28.6139, double lng = 77.2090, double radius = 5000}) async {
    try {
      final response = await _apiService.get('/nearby/police?lat=$lat&lng=$lng&radius_meters=$radius', requireAuth: false);
      final places = (response['places'] as List? ?? []).map((p) => SafePlaceModel.fromJson(p)).toList();
      if (places.isNotEmpty) {
        await OfflineCacheService.cacheSafePlaces(places);
      }
      return places;
    } catch (_) {
      // Offline fallback: load from persistent local cache
      return await OfflineCacheService.getCachedSafePlaces(
        currentLat: lat,
        currentLng: lng,
        categoryFilter: 'POLICE',
        maxRadiusMeters: radius,
      );
    }
  }

  Future<List<SafePlaceModel>> getNearbyHospitals({double lat = 28.6139, double lng = 77.2090, double radius = 5000}) async {
    try {
      final response = await _apiService.get('/nearby/hospitals?lat=$lat&lng=$lng&radius_meters=$radius', requireAuth: false);
      final places = (response['places'] as List? ?? []).map((p) => SafePlaceModel.fromJson(p)).toList();
      if (places.isNotEmpty) {
        await OfflineCacheService.cacheSafePlaces(places);
      }
      return places;
    } catch (_) {
      // Offline fallback
      return await OfflineCacheService.getCachedSafePlaces(
        currentLat: lat,
        currentLng: lng,
        categoryFilter: 'HOSPITAL',
        maxRadiusMeters: radius,
      );
    }
  }

  Future<List<SafePlaceModel>> getNearbySafePlaces({double lat = 28.6139, double lng = 77.2090, double radius = 5000}) async {
    try {
      final response = await _apiService.get('/nearby/safe-places?lat=$lat&lng=$lng&radius_meters=$radius', requireAuth: false);
      final places = (response['places'] as List? ?? []).map((p) => SafePlaceModel.fromJson(p)).toList();
      if (places.isNotEmpty) {
        await OfflineCacheService.cacheSafePlaces(places);
      }
      return places;
    } catch (_) {
      // Offline fallback
      return await OfflineCacheService.getCachedSafePlaces(
        currentLat: lat,
        currentLng: lng,
        maxRadiusMeters: radius,
      );
    }
  }

  Future<List<RouteOptionModel>> calculateRoutes({
    required double startLat,
    required double startLng,
    required double destLat,
    required double destLng,
  }) async {
    final response = await _apiService.post('/routes/calculate', body: {
      'start_lat': startLat,
      'start_lng': startLng,
      'dest_lat': destLat,
      'dest_lng': destLng,
    });
    final routes = response['routes'] as List? ?? [];
    return routes.map((r) => RouteOptionModel.fromJson(r)).toList();
  }
}

class CameraRepository {
  final ApiService _apiService;

  CameraRepository({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  Future<Map<String, dynamic>> createCameraSession({String? targetUserId}) async {
    final response = await _apiService.post('/camera/session', body: {
      if (targetUserId != null) 'target_user_id': targetUserId,
    });
    return response;
  }

  Future<Map<String, dynamic>> getCameraStatus() async {
    final response = await _apiService.get('/camera/status');
    return response;
  }
}
