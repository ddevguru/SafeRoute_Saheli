import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/emergency_bloc.dart';
import '../constants/app_colors.dart';
import '../widgets/quick_action_tile.dart';

class ActiveEmergencyScreen extends StatelessWidget {
  const ActiveEmergencyScreen({Key? key}) : super(key: key);

  void _onCancelHold(BuildContext context, String incidentId) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Deactivate Emergency Alert?'),
        content: const Text('Are you safe? This will notify your guardians and de-escalate active emergency monitoring.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Stay In Emergency', style: TextStyle(color: AppColors.textSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
            onPressed: () {
              Navigator.pop(ctx);
              context.read<EmergencyBloc>().add(
                    CancelEmergencyEvent(incidentId: incidentId, reason: "User verified false alarm or safe condition"),
                  );
              Navigator.pop(context);
            },
            child: const Text('Yes, I am Safe'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false, // Prevent accidental back navigation during emergency
      child: Scaffold(
        backgroundColor: const Color(0xFF1E0A0A),
        appBar: AppBar(
          backgroundColor: AppColors.emergencyDark,
          automaticallyImplyLeading: false,
          title: const Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: AppColors.white),
              SizedBox(width: 8),
              Text(
                'EMERGENCY DISPATCH ACTIVE',
                style: TextStyle(color: AppColors.white, fontWeight: FontWeight.w700, fontSize: 16),
              ),
            ],
          ),
        ),
        body: BlocBuilder<EmergencyBloc, EmergencyState>(
          builder: (context, state) {
            String incidentId = '';
            String triggerType = 'TOUCH / BUTTON';
            String trackingUrl = 'https://saheli.safe/track/live-session';

            if (state is EmergencyActiveState) {
              incidentId = state.incident.id;
              triggerType = state.incident.triggerType;
              if (state.incident.trackingUrl != null) {
                trackingUrl = state.incident.trackingUrl!;
              }
            }

            return SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                child: Column(
                  children: [
                    // Emergency Pulse Header
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: AppColors.emergency.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.emergency, width: 2),
                      ),
                      child: Column(
                        children: [
                          const Icon(Icons.emergency_share_rounded, color: AppColors.emergency, size: 48),
                          const SizedBox(height: 8),
                          const Text(
                            'ALERTS SENT TO GUARDIANS',
                            style: TextStyle(
                              color: AppColors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Trigger: $triggerType | Live GPS streaming at 5s interval',
                            style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 13),
                          ),
                          const SizedBox(height: 10),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.3),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.link_rounded, size: 14, color: AppColors.secondary),
                                const SizedBox(width: 6),
                                Flexible(
                                  child: Text(
                                    trackingUrl,
                                    style: const TextStyle(color: AppColors.secondary, fontSize: 11, fontFamily: 'monospace'),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Actions in Progress Card
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF2A1515),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Column(
                        children: [
                          _AlertCheckRow(title: 'High-Priority Guardian Push', status: 'Delivered'),
                          SizedBox(height: 10),
                          _AlertCheckRow(title: 'Emergency SMS with Map Link', status: 'Sent'),
                          SizedBox(height: 10),
                          _AlertCheckRow(title: 'Voice Emergency Call', status: 'Connecting...'),
                          SizedBox(height: 10),
                          _AlertCheckRow(title: 'ESP32-CAM Burst Capture', status: 'Frames Saved'),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Nearest Safe Places Section
                    const Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'Nearest Emergency Assistance',
                        style: TextStyle(color: AppColors.white, fontWeight: FontWeight.w700, fontSize: 15),
                      ),
                    ),
                    const SizedBox(height: 10),

                    NearbyPlaceCard(
                      name: 'Central Women Police Assistance Booth',
                      category: 'POLICE',
                      distanceMeters: 350,
                      onNavigate: () {},
                    ),
                    NearbyPlaceCard(
                      name: 'City General Multi-Specialty Hospital',
                      category: 'HOSPITAL',
                      distanceMeters: 800,
                      onNavigate: () {},
                    ),

                    const Spacer(),

                    // De-escalate / Cancel Button
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: AppColors.primary,
                        ),
                        icon: const Icon(Icons.check_circle_rounded, color: AppColors.success),
                        label: const Text(
                          'I AM SAFE — CANCEL ALERT',
                          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                        onPressed: () => _onCancelHold(context, incidentId),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _AlertCheckRow extends StatelessWidget {
  final String title;
  final String status;

  const _AlertCheckRow({required this.title, required this.status});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            const Icon(Icons.check_circle_rounded, color: AppColors.success, size: 16),
            const SizedBox(width: 8),
            Text(title, style: const TextStyle(color: AppColors.white, fontSize: 13)),
          ],
        ),
        Text(status, style: const TextStyle(color: Color(0xFFFBBF24), fontSize: 12, fontWeight: FontWeight.w600)),
      ],
    );
  }
}
