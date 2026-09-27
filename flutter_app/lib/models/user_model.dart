class UserModel {
  final String id;
  final String name;
  final String email;
  final String phone;
  final String? dateOfBirth;
  final String? profilePhotoUrl;
  final String? emergencyBloodGroup;
  final String? medicalNotes;
  final bool isActive;
  final Map<String, dynamic> privacySettings;

  UserModel({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    this.dateOfBirth,
    this.profilePhotoUrl,
    this.emergencyBloodGroup,
    this.medicalNotes,
    this.isActive = true,
    this.privacySettings = const {},
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      dateOfBirth: json['date_of_birth'],
      profilePhotoUrl: json['profile_photo_url'],
      emergencyBloodGroup: json['emergency_blood_group'],
      medicalNotes: json['medical_notes'],
      isActive: json['is_active'] ?? true,
      privacySettings: json['privacy_settings'] != null
          ? Map<String, dynamic>.from(json['privacy_settings'])
          : {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'date_of_birth': dateOfBirth,
      'profile_photo_url': profilePhotoUrl,
      'emergency_blood_group': emergencyBloodGroup,
      'medical_notes': medicalNotes,
      'is_active': isActive,
      'privacy_settings': privacySettings,
    };
  }
}
