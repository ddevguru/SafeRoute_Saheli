import 'package:flutter/material.dart';
import '../screens/splash_screen.dart';
import '../screens/onboarding_screen.dart';
import '../screens/login_screen.dart';
import '../screens/register_screen.dart';
import '../screens/forgot_password_screen.dart';
import '../screens/privacy_settings_screen.dart';
import '../screens/home_dashboard_screen.dart';
import '../screens/active_emergency_screen.dart';
import '../screens/live_camera_screen.dart';
import '../screens/guardian_dashboard_screen.dart';
import '../screens/safe_route_screen.dart';
import '../screens/nearby_help_screen.dart';
import '../screens/guardians_management_screen.dart';
import '../screens/emergency_history_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String privacySettings = '/privacy-settings';
  static const String home = '/home';
  static const String activeEmergency = '/active-emergency';
  static const String liveCamera = '/live-camera';
  static const String guardianDashboard = '/guardian-dashboard';
  static const String safeRoute = '/safe-route';
  static const String nearbyHelp = '/nearby-help';
  static const String guardians = '/guardians';
  static const String emergencyHistory = '/emergency-history';

  static Map<String, WidgetBuilder> get routes {
    return {
      splash: (context) => const SplashScreen(),
      onboarding: (context) => const OnboardingScreen(),
      login: (context) => const LoginScreen(),
      register: (context) => const RegisterScreen(),
      forgotPassword: (context) => const ForgotPasswordScreen(),
      privacySettings: (context) => const PrivacySettingsScreen(),
      home: (context) => const HomeDashboardScreen(),
      activeEmergency: (context) => const ActiveEmergencyScreen(),
      liveCamera: (context) {
        final targetUserId = ModalRoute.of(context)?.settings.arguments as String?;
        return LiveCameraScreen(targetUserId: targetUserId);
      },
      guardianDashboard: (context) => const GuardianDashboardScreen(),
      safeRoute: (context) => const SafeRouteScreen(),
      nearbyHelp: (context) => const NearbyHelpScreen(),
      guardians: (context) => const GuardiansManagementScreen(),
      emergencyHistory: (context) => const EmergencyHistoryScreen(),
    };
  }
}
