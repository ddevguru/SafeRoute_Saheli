import 'package:flutter/material.dart';
import '../constants/app_colors.dart';

class QuickActionTile extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  final Color? accentColor;

  const QuickActionTile({
    Key? key,
    required this.title,
    required this.icon,
    required this.onTap,
    this.accentColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.borderLight),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.02),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: (accentColor ?? AppColors.primary).withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: accentColor ?? AppColors.primary,
                size: 22,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              title,
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
                height: 1.15,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class NearbyPlaceCard extends StatelessWidget {
  final String name;
  final String category;
  final double distanceMeters;
  final VoidCallback onNavigate;
  final VoidCallback? onCall;
  final bool isDarkTheme;

  const NearbyPlaceCard({
    Key? key,
    required this.name,
    required this.category,
    required this.distanceMeters,
    required this.onNavigate,
    this.onCall,
    this.isDarkTheme = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isPolice = category.toUpperCase() == 'POLICE';
    final isHospital = category.toUpperCase() == 'HOSPITAL';

    final icon = isPolice
        ? Icons.local_police_rounded
        : (isHospital ? Icons.local_hospital_rounded : Icons.shield_rounded);

    final color = isPolice
        ? (isDarkTheme ? AppColors.secondary : AppColors.primary)
        : (isHospital ? AppColors.emergency : AppColors.secondary);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: isDarkTheme ? const Color(0xFF241010) : AppColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: isDarkTheme ? Colors.white12 : AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.02),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: isDarkTheme ? 0.2 : 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                    color: isDarkTheme ? Colors.white : AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  '${distanceMeters.toStringAsFixed(0)} m away',
                  style: TextStyle(
                    fontSize: 11,
                    color: isDarkTheme ? Colors.white70 : AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          if (onCall != null) ...[
            IconButton.filledTonal(
              style: IconButton.styleFrom(
                backgroundColor: AppColors.secondary.withValues(alpha: 0.2),
                foregroundColor: AppColors.secondary,
                padding: const EdgeInsets.all(8),
                minimumSize: const Size(36, 36),
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              icon: const Icon(Icons.phone_in_talk_rounded, size: 16),
              tooltip: 'Emergency Call',
              onPressed: onCall,
            ),
            const SizedBox(width: 6),
          ],
          ElevatedButton(
            onPressed: onNavigate,
            style: ElevatedButton.styleFrom(
              backgroundColor: isDarkTheme ? AppColors.primary : AppColors.primary,
              foregroundColor: AppColors.white,
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              minimumSize: const Size(38, 36),
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Navigate →', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
