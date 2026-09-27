class SafePlaceModel {
  final String id;
  final String name;
  final String category; // POLICE, HOSPITAL, PHARMACY, SHELTER
  final double latitude;
  final double longitude;
  final String address;
  final String? phoneNumber;
  final double distanceMeters;
  final double? estimatedTimeMins;

  SafePlaceModel({
    required this.id,
    required this.name,
    required this.category,
    required this.latitude,
    required this.longitude,
    required this.address,
    this.phoneNumber,
    this.distanceMeters = 0.0,
    this.estimatedTimeMins,
  });

  String? get phone => phoneNumber;

  factory SafePlaceModel.fromJson(Map<String, dynamic> json) {
    return SafePlaceModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      category: json['category'] ?? 'POLICE',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      address: json['address'] ?? '',
      phoneNumber: json['phone_number'],
      distanceMeters: (json['distance_meters'] as num?)?.toDouble() ?? 0.0,
      estimatedTimeMins: (json['estimated_time_mins'] as num?)?.toDouble(),
    );
  }
}

class RouteOptionModel {
  final String id;
  final String type; // SHORTEST, FASTEST, SAFETY_OPTIMIZED
  final double distanceKm;
  final double durationMins;
  final double safetyScore;
  final String? recommendation;
  final Map<String, dynamic> riskFactors;
  final List<Map<String, double>> coordinates;
  final List<String> steps;

  RouteOptionModel({
    required this.id,
    required this.type,
    required this.distanceKm,
    required this.durationMins,
    required this.safetyScore,
    this.recommendation,
    this.riskFactors = const {},
    this.coordinates = const [],
    this.steps = const [],
  });

  factory RouteOptionModel.fromJson(Map<String, dynamic> json) {
    List<Map<String, double>> coords = [];
    if (json['coordinates'] is List) {
      coords = (json['coordinates'] as List).map<Map<String, double>>((c) {
        if (c is Map) {
          return {
            'lat': (c['lat'] as num?)?.toDouble() ?? 0.0,
            'lng': (c['lng'] as num?)?.toDouble() ?? 0.0,
          };
        }
        return {'lat': 0.0, 'lng': 0.0};
      }).toList();
    }

    List<String> stepList = [];
    if (json['steps'] is List) {
      stepList = (json['steps'] as List).map((s) => s.toString()).toList();
    }

    return RouteOptionModel(
      id: json['id'] ?? '',
      type: json['type'] ?? 'SAFETY_OPTIMIZED',
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
      durationMins: (json['duration_mins'] as num?)?.toDouble() ?? 0.0,
      safetyScore: (json['safety_score'] as num?)?.toDouble() ?? 80.0,
      recommendation: json['recommendation'],
      riskFactors: json['risk_factors'] != null ? Map<String, dynamic>.from(json['risk_factors']) : {},
      coordinates: coords,
      steps: stepList,
    );
  }
}
