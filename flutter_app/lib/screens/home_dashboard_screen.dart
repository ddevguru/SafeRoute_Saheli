import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/auth_bloc.dart';
import '../blocs/emergency_bloc.dart';
import '../constants/app_colors.dart';
import '../services/local_device_service.dart';
import '../widgets/emergency_button.dart';
import '../widgets/status_card.dart';
import '../widgets/quick_action_tile.dart';
import '../routes/app_routes.dart';

class HomeDashboardScreen extends StatefulWidget {
  const HomeDashboardScreen({Key? key}) : super(key: key);

  @override
  State<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends State<HomeDashboardScreen> {
  Timer? _emergencyPollTimer;

  @override
  void initState() {
    super.initState();
    LocalDeviceService().init();
    // Check if an emergency was already active immediately
    context.read<EmergencyBloc>().add(CheckActiveEmergencyEvent());
    // Auto-poll cloud backend every 3.5 seconds to detect any emergency triggered by physical wearable
    _emergencyPollTimer = Timer.periodic(const Duration(milliseconds: 3500), (_) {
      if (mounted) {
        context.read<EmergencyBloc>().add(CheckActiveEmergencyEvent());
      }
    });
  }

  @override
  void dispose() {
    _emergencyPollTimer?.cancel();
    super.dispose();
  }

  void _onTriggerEmergency() {
    // Default coordinates (e.g. Connaught Place / current user location)
    context.read<EmergencyBloc>().add(
          TriggerEmergencyEvent(
            triggerType: 'BUTTON',
            latitude: 28.6139,
            longitude: 77.2090,
            batteryPercent: 85,
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<EmergencyBloc, EmergencyState>(
      listener: (context, state) {
        if (state is EmergencyActiveState) {
          Navigator.pushNamed(context, AppRoutes.activeEmergency);
        } else if (state is EmergencyErrorState) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(state.message), backgroundColor: AppColors.emergency),
          );
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          backgroundColor: AppColors.white,
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.shield_rounded, color: AppColors.secondary, size: 20),
              ),
              const SizedBox(width: 10),
              const Text(
                'SafeRoute Saheli',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.hub_outlined),
              tooltip: 'Connect & Manage IoT Devices',
              onPressed: () => Navigator.pushNamed(context, AppRoutes.devices),
            ),
            IconButton(
              icon: const Icon(Icons.person_outline_rounded),
              tooltip: 'My Profile & Medical Info',
              onPressed: () => Navigator.pushNamed(context, AppRoutes.profile),
            ),
            IconButton(
              icon: const Icon(Icons.settings_outlined),
              tooltip: 'Privacy & Safety Settings',
              onPressed: () => Navigator.pushNamed(context, AppRoutes.privacySettings),
            ),
            IconButton(
              icon: const Icon(Icons.logout_rounded),
              tooltip: 'Sign Out',
              onPressed: () {
                context.read<AuthBloc>().add(LogoutEvent());
                Navigator.pushReplacementNamed(context, AppRoutes.login);
              },
            ),
          ],
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Greeting Header
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (context, state) {
                    final userName = (state is AuthenticatedState && state.user != null)
                        ? state.user!.name.split(' ')[0]
                        : 'Saheli';
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Good Morning, $userName',
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.w700,
                                color: AppColors.primary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            const Text(
                              'Stay connected. Your safety circle is active.',
                              style: TextStyle(
                                fontSize: 13,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                        InkWell(
                          borderRadius: BorderRadius.circular(20),
                          onTap: () => Navigator.pushNamed(context, AppRoutes.profile),
                          child: CircleAvatar(
                            radius: 20,
                            backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                            child: const Icon(Icons.person, color: AppColors.primary, size: 22),
                          ),
                        ),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 18),

                // Device & Protection Overview Card (Clickable to open Devices Screen!)
                ValueListenableBuilder<LocalDeviceState>(
                  valueListenable: LocalDeviceService().connectionState,
                  builder: (context, localDev, _) {
                    return StatusOverviewCard(
                      isDeviceConnected: localDev.isWearableOnline,
                      batteryPercent: localDev.wearableBattery,
                      safetyScore: 92.0,
                      guardianStatus: 'Mother ● Online',
                      isCameraLive: localDev.isCameraOnline,
                      currentLocationName: 'Central Safe Corridor',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.devices),
                    );
                  },
                ),
                const SizedBox(height: 28),

                // Central Large Emergency Button
                EmergencyButton(
                  onTrigger: _onTriggerEmergency,
                ),
                const SizedBox(height: 28),

                // Quick Actions Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Quick Protection Actions',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppColors.primary,
                      ),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.devices),
                      child: const Text('IoT Devices ➔', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const SizedBox(height: 10),

                // 8 Action Grid Tiles
                GridView.count(
                  crossAxisCount: 3,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  children: [
                    QuickActionTile(
                      title: 'Safe Route',
                      icon: Icons.alt_route_rounded,
                      accentColor: AppColors.primary,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.safeRoute),
                    ),
                    QuickActionTile(
                      title: 'IoT Devices',
                      icon: Icons.hub_rounded,
                      accentColor: AppColors.secondary,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.devices),
                    ),
                    QuickActionTile(
                      title: 'Live Camera',
                      icon: Icons.videocam_rounded,
                      accentColor: AppColors.emergency,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.liveCamera),
                    ),
                    QuickActionTile(
                      title: 'Trigger History',
                      icon: Icons.history_rounded,
                      accentColor: AppColors.textSecondary,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.emergencyHistory),
                    ),
                    QuickActionTile(
                      title: 'My Profile',
                      icon: Icons.person_outline_rounded,
                      accentColor: AppColors.primary,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.profile),
                    ),
                    QuickActionTile(
                      title: 'My Guardians',
                      icon: Icons.family_restroom_rounded,
                      accentColor: AppColors.secondary,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.guardians),
                    ),
                    QuickActionTile(
                      title: 'Nearby Help',
                      icon: Icons.local_police_rounded,
                      accentColor: AppColors.primary,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.nearbyHelp),
                    ),
                    QuickActionTile(
                      title: 'Privacy Settings',
                      icon: Icons.security_rounded,
                      accentColor: AppColors.success,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.privacySettings),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
