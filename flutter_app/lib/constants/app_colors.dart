import 'package:flutter/material.dart';

class AppColors {
  // Brand Identity Colors (Specified in SafeRoute Saheli Design System)
  static const Color primary = Color(0xFF002350);       // Deep Premium Navy
  static const Color secondary = Color(0xFFD2AE39);     // Warm Regal Gold
  static const Color background = Color(0xFFF5F7FA);    // Clean Modern Off-White
  static const Color white = Color(0xFFFFFFFF);         // Pure White

  // Functional Semantic Alert Colors
  static const Color emergency = Color(0xFFDC2626);     // Emergency Bright Red
  static const Color emergencyDark = Color(0xFF991B1B); // Deep Blood Crimson
  static const Color warning = Color(0xFFF59E0B);       // Warning Amber / Orange
  static const Color success = Color(0xFF10B981);       // Success Emerald Green

  // Neutral Scales
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cardBackground = Color(0xFFF1F5F9);
  static const Color textPrimary = Color(0xFF111827);
  static const Color textSecondary = Color(0xFF4B5563);
  static const Color textMuted = Color(0xFF9CA3AF);
  static const Color borderLight = Color(0xFFE5E7EB);
  static const Color divider = Color(0xFFF3F4F6);

  // Status Indicators
  static const Color deviceConnected = Color(0xFF10B981);
  static const Color deviceOffline = Color(0xFF6B7280);
  static const Color liveIndicator = Color(0xFFEF4444);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF002350), Color(0xFF0A3C7D)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient secondaryGradient = LinearGradient(
    colors: [Color(0xFFD2AE39), Color(0xFFF0D270)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient emergencyGradient = LinearGradient(
    colors: [Color(0xFFDC2626), Color(0xFF991B1B)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient shieldGlow = LinearGradient(
    colors: [Color(0x33D2AE39), Color(0x05002350)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
