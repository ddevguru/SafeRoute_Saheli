import 'package:flutter/material.dart';
import '../constants/app_colors.dart';

class StatusOverviewCard extends StatelessWidget {
  final bool isDeviceConnected;
  final int batteryPercent;
  final double safetyScore;
  final String guardianStatus;
  final bool isCameraLive;
  final String currentLocationName;
  final VoidCallback? onTap;

  const StatusOverviewCard({
    Key? key,
    this.isDeviceConnected = false,
    this.batteryPercent = 0,
    this.safetyScore = 82.0,
    this.guardianStatus = 'Mother ● Online',
    this.isCameraLive = false,
    this.currentLocationName = 'Central Safe Zone',
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 16,
              offset: const Offset(0, 4),
            ),
          ],
          border: Border.all(color: AppColors.borderLight),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Device Connection Badge
                Row(
                  children: [
                    Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isDeviceConnected ? AppColors.deviceConnected : AppColors.deviceOffline,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      isDeviceConnected ? 'Device Connected' : 'Device Offline',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                        color: isDeviceConnected ? AppColors.textPrimary : AppColors.emergency,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      isDeviceConnected ? '(ESP32 Active)' : '(Tap to Connect Wi-Fi)',
                      style: TextStyle(
                        fontSize: 11,
                        color: isDeviceConnected
                            ? AppColors.textSecondary.withValues(alpha: 0.8)
                            : AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                // Battery & Manage Link
                Row(
                  children: [
                    Icon(
                      isDeviceConnected
                          ? (batteryPercent > 20 ? Icons.battery_charging_full : Icons.battery_alert)
                          : Icons.power_off_rounded,
                      color: isDeviceConnected
                          ? (batteryPercent > 20 ? AppColors.success : AppColors.emergency)
                          : AppColors.textMuted,
                      size: 18,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      isDeviceConnected ? '$batteryPercent%' : 'OFF',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                        color: isDeviceConnected
                            ? (batteryPercent > 20 ? AppColors.textPrimary : AppColors.emergency)
                            : AppColors.textMuted,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Icon(Icons.arrow_forward_ios_rounded, size: 12, color: AppColors.primary),
                  ],
                ),
              ],
            ),
            const Divider(height: 24, color: AppColors.divider),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                // Safety Score
                _buildMetricItem(
                  title: 'Safety Score',
                  value: '${safetyScore.toInt()}/100',
                  color: safetyScore > 70 ? AppColors.success : AppColors.warning,
                  icon: Icons.shield_outlined,
                ),
                Container(width: 1, height: 38, color: AppColors.divider),
                // Guardian Status
                _buildMetricItem(
                  title: 'Guardian',
                  value: guardianStatus,
                  color: AppColors.primary,
                  icon: Icons.family_restroom,
                ),
                Container(width: 1, height: 38, color: AppColors.divider),
                // Camera Live State
                _buildMetricItem(
                  title: 'Camera',
                  value: isCameraLive ? '● Live' : 'Idle',
                  color: isCameraLive ? AppColors.liveIndicator : AppColors.textMuted,
                  icon: Icons.videocam_outlined,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricItem({
    required String title,
    required String value,
    required Color color,
    required IconData icon,
  }) {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 11,
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: color,
          ),
        ),
      ],
    );
  }
}
