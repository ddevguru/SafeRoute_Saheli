import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../repositories/guardian_repository.dart';
import '../routes/app_routes.dart';

class GuardianDashboardScreen extends StatefulWidget {
  const GuardianDashboardScreen({Key? key}) : super(key: key);

  @override
  State<GuardianDashboardScreen> createState() => _GuardianDashboardScreenState();
}

class _GuardianDashboardScreenState extends State<GuardianDashboardScreen> {
  final GuardianRepository _guardianRepository = GuardianRepository();
  bool _isLoading = true;
  List<Map<String, dynamic>> _sahelis = [];

  @override
  void initState() {
    super.initState();
    _loadMonitoredSahelis();
  }

  Future<void> _loadMonitoredSahelis() async {
    setState(() => _isLoading = true);
    try {
      final list = await _guardianRepository.getMonitoredSahelis();
      setState(() {
        _sahelis = list;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Guardian Safety Portal'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _loadMonitoredSahelis,
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            onPressed: () {
              Navigator.pushReplacementNamed(context, AppRoutes.login);
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : (_sahelis.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.family_restroom_rounded, size: 54, color: AppColors.textMuted),
                        const SizedBox(height: 12),
                        const Text(
                          'No Saheli Accounts Linked Yet',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'When a Saheli links you as her guardian, her live status and emergency telemetry will appear here.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _sahelis.length,
                  itemBuilder: (context, index) {
                    final item = _sahelis[index];
                    final name = item['name'] ?? 'Saheli';
                    final emergency = item['active_emergency'];
                    final bool isEmergency = emergency != null;
                    final permissions = item['permissions'] ?? {};
                    final bool canCamera = permissions['can_view_camera'] ?? false;
                    final bool canLocation = permissions['can_view_location'] ?? true;

                    return Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: AppColors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: isEmergency ? AppColors.emergency : AppColors.borderLight,
                          width: isEmergency ? 2 : 1,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: (isEmergency ? AppColors.emergency : Colors.black).withValues(alpha: 0.04),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  CircleAvatar(
                                    radius: 20,
                                    backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                                    child: const Icon(Icons.person_rounded, color: AppColors.primary),
                                  ),
                                  const SizedBox(width: 12),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        name,
                                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                                      ),
                                      Text(
                                        permissions['relationship_label'] ?? 'Ward',
                                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              // Emergency or Safe Badge
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: isEmergency
                                      ? AppColors.emergency.withValues(alpha: 0.12)
                                      : AppColors.success.withValues(alpha: 0.12),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Text(
                                  isEmergency ? '🚨 EMERGENCY' : '● SAFE',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w800,
                                    color: isEmergency ? AppColors.emergency : AppColors.success,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const Divider(height: 24, color: AppColors.divider),
                          // Stats
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Safety Score: ${item['safety_score'] ?? 82}/100',
                                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                              const Text('Battery: 78%',
                                  style: TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                            ],
                          ),
                          const SizedBox(height: 16),
                          // Action Buttons
                          Row(
                            children: [
                              if (canLocation)
                                Expanded(
                                  child: ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppColors.primary,
                                      padding: const EdgeInsets.symmetric(vertical: 10),
                                    ),
                                    icon: const Icon(Icons.location_on_rounded, size: 16),
                                    label: const Text('Live Location', style: TextStyle(fontSize: 12)),
                                    onPressed: () {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('Streaming live GPS coordinates for $name...')),
                                      );
                                    },
                                  ),
                                ),
                              const SizedBox(width: 8),
                              if (canCamera)
                                Expanded(
                                  child: ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppColors.secondary,
                                      padding: const EdgeInsets.symmetric(vertical: 10),
                                    ),
                                    icon: const Icon(Icons.videocam_rounded, size: 16, color: AppColors.primary),
                                    label: const Text('Live Camera',
                                        style: TextStyle(fontSize: 12, color: AppColors.primary)),
                                    onPressed: () {
                                      Navigator.pushNamed(
                                        context,
                                        AppRoutes.liveCamera,
                                        arguments: item['id'],
                                      );
                                    },
                                  ),
                                ),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                )),
    );
  }
}
