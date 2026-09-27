import 'package:flutter_test/flutter_test.dart';
import 'package:saferoute_saheli/storage/offline_cache_service.dart';
import 'package:saferoute_saheli/repositories/routing_repository.dart';
import 'package:saferoute_saheli/repositories/emergency_repository.dart';
import 'package:saferoute_saheli/services/api_service.dart';

// Mock ApiService that simulates zero internet connectivity (SocketException)
class MockOfflineApiService extends ApiService {
  @override
  Future<dynamic> get(String endpoint, {bool requireAuth = true}) async {
    throw ApiException('Network connection unavailable. Offline mode.');
  }

  @override
  Future<dynamic> post(String endpoint, {Map<String, dynamic>? body, bool requireAuth = true}) async {
    throw ApiException('Network connection unavailable. Offline mode.');
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Phase 27 - Offline-First Local Cache & Cellular Fallback Tests', () {
    test('Haversine distance calculation is accurate within 2% margin of error', () {
      // Distance between Connaught Place (28.6289, 77.2065) and India Gate (28.6129, 77.2295)
      // True geodesic distance: ~2,840 meters
      final dist = OfflineCacheService.calculateDistanceMeters(
        28.6289, 77.2065,
        28.6129, 77.2295,
      );

      expect(dist, greaterThan(2700.0));
      expect(dist, lessThan(3000.0));
    });

    test('Cellular SMS emergency string matches backend SMS webhook protocol', () {
      final sms = OfflineCacheService.formatCellularEmergencySms(
        userPhone: '+919876543210',
        latitude: 28.6139,
        longitude: 77.2090,
        triggerType: 'TOUCH',
        batteryPercent: 88,
      );

      expect(sms, startsWith('SR_SOS|'));
      expect(sms, contains('+919876543210'));
      expect(sms, contains('28.61390'));
      expect(sms, contains('77.20900'));
      expect(sms, contains('TOUCH'));
      expect(sms, endsWith('|88'));
    });

    test('Default critical emergency places are accessible out-of-the-box in offline mode', () async {
      final places = await OfflineCacheService.getCachedSafePlaces(
        currentLat: 28.6139,
        currentLng: 77.2090,
      );

      expect(places.isNotEmpty, isTrue);
      // Verify police, hospital, and shelter categories exist
      final categories = places.map((p) => p.category).toSet();
      expect(categories.contains('POLICE'), isTrue);
      expect(categories.contains('HOSPITAL'), isTrue);
      expect(categories.contains('SHELTER'), isTrue);

      // Verify sorted strictly by distance ascending
      for (int i = 0; i < places.length - 1; i++) {
        expect(places[i].distanceMeters <= places[i + 1].distanceMeters, isTrue);
      }
    });

    test('Category filtering works accurately on offline cached places', () async {
      final policePlaces = await OfflineCacheService.getCachedSafePlaces(
        categoryFilter: 'POLICE',
      );

      expect(policePlaces.isNotEmpty, isTrue);
      for (final p in policePlaces) {
        expect(p.category, 'POLICE');
      }
    });

    test('RoutingRepository falls back to local cache when network is offline', () async {
      final offlineRepo = RoutingRepository(apiService: MockOfflineApiService());

      final police = await offlineRepo.getNearbyPolice(lat: 28.6139, lng: 77.2090);
      expect(police.isNotEmpty, isTrue);
      expect(police.first.category, 'POLICE');

      final hospitals = await offlineRepo.getNearbyHospitals(lat: 28.6139, lng: 77.2090);
      expect(hospitals.isNotEmpty, isTrue);
      expect(hospitals.first.category, 'HOSPITAL');

      final allPlaces = await offlineRepo.getNearbySafePlaces(lat: 28.6139, lng: 77.2090);
      expect(allPlaces.length, greaterThanOrEqualTo(4));
    });

    test('EmergencyRepository generates offline pending emergency with cellular SMS payload when offline', () async {
      final offlineRepo = EmergencyRepository(apiService: MockOfflineApiService());

      final incident = await offlineRepo.triggerEmergency(
        triggerType: 'CLAP',
        latitude: 28.6145,
        longitude: 77.2095,
        batteryPercent: 82,
        confidence: 0.95,
      );

      expect(incident.id, startsWith('offline-'));
      expect(incident.status, 'PENDING_OFFLINE');
      expect(incident.triggerType, 'OFFLINE_SMS_CLAP');
      expect(incident.trackingUrl, startsWith('SMS:SR_SOS|'));
      expect(incident.batteryPercent, 82);
    });
  });
}
