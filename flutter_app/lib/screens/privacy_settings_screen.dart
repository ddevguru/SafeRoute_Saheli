import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../services/api_service.dart';

class PrivacySettingsScreen extends StatefulWidget {
  const PrivacySettingsScreen({Key? key}) : super(key: key);

  @override
  State<PrivacySettingsScreen> createState() => _PrivacySettingsScreenState();
}

class _PrivacySettingsScreenState extends State<PrivacySettingsScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  bool _isSaving = false;

  // Settings
  bool _guardianCamera = false;
  bool _emergencyCameraOverride = true;
  bool _audioRecording = true;
  bool _liveLocation = true;
  bool _clapTrigger = true;
  bool _voiceTrigger = true;
  bool _guardianPushAlerts = true;

  @override
  void initState() {
    super.initState();
    _loadPrivacySettings();
  }

  Future<void> _loadPrivacySettings() async {
    setState(() => _isLoading = true);
    try {
      final res = await _apiService.get('/auth/me');
      if (res['success'] == true && res['user'] != null) {
        final u = res['user'];
        setState(() {
          _guardianCamera = u['privacy_guardian_camera'] ?? false;
          _emergencyCameraOverride = u['privacy_emergency_camera_override'] ?? true;
          _audioRecording = u['privacy_audio_recording'] ?? true;
          _liveLocation = u['privacy_live_location'] ?? true;
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveSettings() async {
    setState(() => _isSaving = true);
    try {
      final res = await _apiService.put('/auth/privacy', body: {
        'guardian_camera': _guardianCamera,
        'emergency_camera_override': _emergencyCameraOverride,
        'audio_recording': _audioRecording,
        'live_location': _liveLocation,
      });

      if (!mounted) return;
      setState(() => _isSaving = false);

      if (res['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Privacy & safety preferences saved successfully.'),
            backgroundColor: AppColors.success,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['error'] ?? 'Could not save settings'),
            backgroundColor: AppColors.emergency,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isSaving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error saving preferences: $e'),
          backgroundColor: AppColors.emergency,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Privacy & Safety Settings'),
        actions: [
          TextButton(
            onPressed: (_isLoading || _isSaving) ? null : _saveSettings,
            child: _isSaving
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2),
                  )
                : const Text(
                    'Save',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : SafeArea(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                children: [
                  // Camera Privacy Section
                  _buildSectionHeader('ESP32-CAM Video Privacy', Icons.videocam_rounded),
                  _buildCard([
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('24x7 Guardian Camera Access', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'Allows authorized guardians to request live video anytime. When disabled, camera is inaccessible during non-emergency states.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _guardianCamera,
                      activeThumbColor: AppColors.primary,
                      onChanged: (val) => setState(() => _guardianCamera = val),
                    ),
                    const Divider(height: 1),
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('Emergency Camera Override', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'Automatically streams live camera feed and captures burst snapshots when an active emergency is declared.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _emergencyCameraOverride,
                      activeThumbColor: AppColors.emergency,
                      onChanged: (val) => setState(() => _emergencyCameraOverride = val),
                    ),
                  ]),
                  const SizedBox(height: 20),

                  // Sensor & Microphone Section
                  _buildSectionHeader('Audio & Trigger Controls', Icons.mic_rounded),
                  _buildCard([
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('Emergency Audio Evidence Recording', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'Records encrypted audio via INMP441 microphone during active distress events for legal forensics.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _audioRecording,
                      activeThumbColor: AppColors.primary,
                      onChanged: (val) => setState(() => _audioRecording = val),
                    ),
                    const Divider(height: 1),
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('Clap Pattern Trigger (3 Rapid Claps)', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'Detects high-energy clap burst sequence within 2.5 seconds to trigger discrete alert.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _clapTrigger,
                      activeThumbColor: AppColors.primary,
                      onChanged: (val) => setState(() => _clapTrigger = val),
                    ),
                    const Divider(height: 1),
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('Voice "HELP" & "BACHAO" Detection', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'Edge VAD & keyword spotting triggers emergency protocol upon vocal distress calls.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _voiceTrigger,
                      activeThumbColor: AppColors.primary,
                      onChanged: (val) => setState(() => _voiceTrigger = val),
                    ),
                  ]),
                  const SizedBox(height: 20),

                  // Location & Guardian Alerts Section
                  _buildSectionHeader('Location Sharing & Dispatch', Icons.location_on_rounded),
                  _buildCard([
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('Live GPS Location Sharing', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'Sends continuous 5-10s interval telemetry during active emergency to authorized guardians & dispatch.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _liveLocation,
                      activeThumbColor: AppColors.primary,
                      onChanged: (val) => setState(() => _liveLocation = val),
                    ),
                    const Divider(height: 1),
                    SwitchListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      title: const Text('Guardian High-Priority Push Alerts', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: const Text(
                        'FCM high-priority notifications that pierce silent mode on guardian mobile devices.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      value: _guardianPushAlerts,
                      activeThumbColor: AppColors.primary,
                      onChanged: (val) => setState(() => _guardianPushAlerts = val),
                    ),
                  ]),
                  const SizedBox(height: 28),

                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _isSaving ? null : _saveSettings,
                      child: _isSaving
                          ? const SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(color: AppColors.white, strokeWidth: 2),
                            )
                          : const Text('Save Privacy Preferences'),
                    ),
                  ),
                  const SizedBox(height: 20),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 4),
      child: Row(
        children: [
          Icon(icon, size: 18, color: AppColors.primary),
          const SizedBox(width: 8),
          Text(
            title,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCard(List<Widget> children) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(children: children),
    );
  }
}
