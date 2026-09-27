class GuardianModel {
  final String id;
  final String name;
  final String relationship;
  final String phone;
  final String email;
  final String username;
  final bool isActive;
  final bool canViewCamera;
  final bool canViewLocation;
  final bool emergencyOverrideCamera;
  final bool isPrimary;

  GuardianModel({
    required this.id,
    required this.name,
    required this.relationship,
    required this.phone,
    required this.email,
    required this.username,
    this.isActive = true,
    this.canViewCamera = false,
    this.canViewLocation = true,
    this.emergencyOverrideCamera = true,
    this.isPrimary = false,
  });

  factory GuardianModel.fromJson(Map<String, dynamic> json) {
    final perms = json['link_permissions'] ?? json['permissions'] ?? {};
    return GuardianModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      relationship: json['relationship'] ?? perms['relationship_label'] ?? 'Guardian',
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      username: json['username'] ?? '',
      isActive: json['is_active'] ?? true,
      canViewCamera: perms['can_view_camera'] ?? false,
      canViewLocation: perms['can_view_location'] ?? true,
      emergencyOverrideCamera: perms['emergency_override_camera'] ?? true,
      isPrimary: perms['is_primary'] ?? false,
    );
  }
}
