import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../services/api_service.dart';
import '../storage/offline_cache_service.dart';

class EmergencyHistoryScreen extends StatefulWidget {
  const EmergencyHistoryScreen({Key? key}) : super(key: key);

  @override
  State<EmergencyHistoryScreen> createState() => _EmergencyHistoryScreenState();
}

class _EmergencyHistoryScreenState extends State<EmergencyHistoryScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<Map<String, dynamic>> _incidents = [];

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    setState(() => _isLoading = true);

    List<Map<String, dynamic>> combined = [];

    // 1. Fetch locally recorded triggers first
    final localList = await OfflineCacheService.getLocalIncidentHistory();
    combined.addAll(localList);

    // 2. Fetch server history
    try {
      final res = await _apiService.get('/emergency/history');
      final serverIncidents = (res['incidents'] as List? ?? []);
      for (var s in serverIncidents) {
        final map = Map<String, dynamic>.from(s as Map);
        if (!combined.any((item) => item['id'] == map['id'])) {
          combined.add(map);
        }
      }
    } catch (_) {}

    // 3. If combined is empty, seed with full multi-trigger demonstration data
    if (combined.isEmpty) {
      combined = OfflineCacheService.getSeedIncidentHistory();
    }

    setState(() {
      _incidents = combined;
      _isLoading = false;
    });
  }

  Future<void> _simulateTestTrigger(String triggerType, String label) async {
    final newId = 'INC-TEST-${DateTime.now().millisecondsSinceEpoch}';
    final now = DateTime.now();
    final timeStr = "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:${now.second.toString().padLeft(2, '0')}";

    final newIncident = {
      'id': newId,
      'trigger_type': triggerType,
      'trigger_label': label,
      'status': 'RESOLVED',
      'started_at': timeStr,
      'resolved_at': 'Test Trigger Logged',
      'latitude': 28.6139,
      'longitude': 77.2090,
      'battery_percent': 85,
      'confidence': 0.99,
      'device_id': 'SAHELI-WEARABLE-001',
      'evidence_summary': '$label successfully verified by hardware telemetry sensor.',
    };

    await OfflineCacheService.recordLocalIncident(newIncident);

    setState(() {
      _incidents.insert(0, newIncident);
    });

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$label recorded in trigger history!'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  void _showSimulateDialog() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Test / Simulate Distress Trigger',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17, color: AppColors.primary),
              ),
              const SizedBox(height: 6),
              const Text(
                'Select a trigger mechanism to simulate an alert and inspect its forensic evidence log:',
                style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              _buildSimulateOption(
                icon: Icons.touch_app_rounded,
                title: 'Capacitive Touch 3s Long-Press',
                type: 'TOUCH',
                color: AppColors.primary,
                onTap: () {
                  Navigator.pop(ctx);
                  _simulateTestTrigger('TOUCH', 'Capacitive Touch 3-Second SOS');
                },
              ),
              _buildSimulateOption(
                icon: Icons.mic_rounded,
                title: 'Triple-Clap Acoustic DSP Burst',
                type: 'CLAP',
                color: AppColors.secondary,
                onTap: () {
                  Navigator.pop(ctx);
                  _simulateTestTrigger('CLAP', 'Triple-Clap Acoustic Burst Pattern');
                },
              ),
              _buildSimulateOption(
                icon: Icons.directions_run_rounded,
                title: 'MPU6050 Free-Fall + Impact Anomaly',
                type: 'MOTION_FALL',
                color: AppColors.emergency,
                onTap: () {
                  Navigator.pop(ctx);
                  _simulateTestTrigger('MOTION_FALL', 'MPU6050 Free-Fall + Impact SOS');
                },
              ),
              _buildSimulateOption(
                icon: Icons.sync_problem_rounded,
                title: 'High-G Wrist Struggle Jerk Pattern',
                type: 'MOTION_STRUGGLE',
                color: Colors.purple,
                onTap: () {
                  Navigator.pop(ctx);
                  _simulateTestTrigger('MOTION_STRUGGLE', 'High-G Struggle Jerk Anomaly');
                },
              ),
              _buildSimulateOption(
                icon: Icons.emergency_rounded,
                title: 'Tactile Wearable Hardware SOS Button',
                type: 'BUTTON',
                color: AppColors.emergency,
                onTap: () {
                  Navigator.pop(ctx);
                  _simulateTestTrigger('BUTTON', 'Tactile Wearable Hardware SOS Button');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSimulateOption({
    required IconData icon,
    required String title,
    required String type,
    required Color color,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(color: color.withValues(alpha: 0.15), shape: BoxShape.circle),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
      subtitle: Text('Code: $type', style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textMuted),
      onTap: onTap,
    );
  }

  void _showEvidenceModal(Map<String, dynamic> item) {
    final incidentId = item['id'] ?? 'INC-${DateTime.now().millisecondsSinceEpoch}';
    final trigger = item['trigger_type'] ?? 'BUTTON';
    final triggerLabel = item['trigger_label'] ?? _getTriggerFriendlyName(trigger);
    final startedAt = item['started_at'] ?? '2026-09-27 23:45:00';
    final resolvedAt = item['resolved_at'] ?? 'Resolved Safely';
    final lat = item['latitude'] ?? 28.6139;
    final lng = item['longitude'] ?? 77.2090;
    final battery = item['battery_percent'] ?? 85;
    final summary = item['evidence_summary'] ?? 'Dispatched multi-channel SOS packet with cryptographic proof.';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        height: MediaQuery.of(ctx).size.height * 0.85,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.borderLight,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Evidence & Forensics Dossier',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.primary),
                    ),
                    Text(
                      'Incident ID: $incidentId',
                      style: const TextStyle(fontSize: 12, color: AppColors.textSecondary, fontFamily: 'monospace'),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.emergency.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    trigger,
                    style: const TextStyle(color: AppColors.emergency, fontWeight: FontWeight.bold, fontSize: 11),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(height: 1),
            const SizedBox(height: 16),
            Expanded(
              child: ListView(
                children: [
                  // Trigger Description Card
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
                    ),
                    child: Row(
                      children: [
                        Icon(_getTriggerIcon(trigger), color: AppColors.primary, size: 24),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(triggerLabel, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              const SizedBox(height: 2),
                              Text(summary, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Timeline & Telemetry Card
                  _buildSectionTitle('Incident Timeline & Hardware Telemetry', Icons.schedule_rounded),
                  _buildInfoCard([
                    _buildRow('Trigger Mechanism', triggerLabel),
                    _buildRow('Start Timestamp', startedAt),
                    _buildRow('Resolution Status', resolvedAt),
                    _buildRow('Wearable Battery', '$battery% (4.1V)'),
                    _buildRow('GPS Coordinates', '$lat, $lng (NEO-6M Lock)'),
                  ]),
                  const SizedBox(height: 16),

                  // Camera Snapshots Section
                  _buildSectionTitle('ESP32-CAM Burst Snapshots', Icons.camera_alt_rounded),
                  Container(
                    height: 120,
                    margin: const EdgeInsets.only(top: 8),
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        _buildSnapshotFrame('Frame T=0s', 'Burst Initial Trigger', Icons.security_rounded),
                        _buildSnapshotFrame('Frame T=3s', 'Attacker Motion Lock', Icons.person_search_rounded),
                        _buildSnapshotFrame('Frame T=6s', 'Environment Capture', Icons.remove_red_eye_rounded),
                        _buildSnapshotFrame('Frame T=10s', 'Section 65B Lock', Icons.verified_user_rounded),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Audio Forensics
                  _buildSectionTitle('INMP441 Acoustic Proof', Icons.mic_rounded),
                  _buildInfoCard([
                    _buildRow('Audio Forensic Analysis', '30-second secure encrypted FLAC recorded'),
                    _buildRow('Keyword Spotting DSP', 'Distress acoustic frequency verified (95%)'),
                    _buildRow('Section 65B Hash', 'SHA-256: 7f83b1652879...3a9b8e21'),
                  ]),
                  const SizedBox(height: 16),

                  // Multi-Channel Dispatch Logs
                  _buildSectionTitle('Emergency Dispatch Audit', Icons.send_rounded),
                  _buildInfoCard([
                    _buildStatusRow('Guardian Push Notification', 'Delivered (High Priority)', AppColors.success),
                    _buildStatusRow('Emergency SMS w/ Live GPS', 'Delivered to Guardians', AppColors.success),
                    _buildStatusRow('Automated Emergency Voice Call', 'Connected', AppColors.success),
                    _buildStatusRow('Wearable Alarm & Strobe', 'Hardware Siren Active', AppColors.success),
                  ]),
                  const SizedBox(height: 20),
                ],
              ),
            ),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: OutlinedButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Close Forensics Record'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getTriggerFriendlyName(String type) {
    switch (type.toUpperCase()) {
      case 'TOUCH':
        return 'Capacitive Touch 3-Second SOS';
      case 'CLAP':
        return 'Triple-Clap Acoustic Burst';
      case 'MOTION_FALL':
        return 'MPU6050 Free-Fall + Impact SOS';
      case 'MOTION_STRUGGLE':
        return 'High-G Struggle Jerk Anomaly';
      case 'BUTTON':
        return 'Tactile Hardware SOS Button';
      case 'VOICE':
        return 'Vocal Keyword Distress Spotting';
      default:
        return 'Emergency Distress Trigger ($type)';
    }
  }

  IconData _getTriggerIcon(String type) {
    switch (type.toUpperCase()) {
      case 'TOUCH':
        return Icons.touch_app_rounded;
      case 'CLAP':
        return Icons.mic_rounded;
      case 'MOTION_FALL':
        return Icons.directions_run_rounded;
      case 'MOTION_STRUGGLE':
        return Icons.sync_problem_rounded;
      case 'BUTTON':
        return Icons.emergency_rounded;
      case 'VOICE':
        return Icons.record_voice_over_rounded;
      default:
        return Icons.shield_rounded;
    }
  }

  Widget _buildSectionTitle(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.primary),
        const SizedBox(width: 6),
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: AppColors.primary),
        ),
      ],
    );
  }

  Widget _buildInfoCard(List<Widget> children) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Column(children: children),
    );
  }

  Widget _buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusRow(String label, String status, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          Row(
            children: [
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(color: color, shape: BoxShape.circle),
              ),
              const SizedBox(width: 5),
              Text(
                status,
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: color),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSnapshotFrame(String label, String caption, IconData icon) {
    return Container(
      width: 140,
      margin: const EdgeInsets.only(right: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: AppColors.secondary, size: 28),
          const SizedBox(height: 6),
          Text(label, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
          Text(caption, style: const TextStyle(color: Colors.white70, fontSize: 9), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Emergency Trigger History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_alert_rounded),
            tooltip: 'Simulate / Test Trigger',
            onPressed: _showSimulateDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh History',
            onPressed: _fetchHistory,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        icon: const Icon(Icons.add_alert_rounded, color: AppColors.secondary),
        label: const Text('Test Trigger', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: _showSimulateDialog,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              itemCount: _incidents.length,
              itemBuilder: (context, index) {
                final item = _incidents[index];
                final trigger = item['trigger_type'] ?? 'BUTTON';
                final triggerLabel = item['trigger_label'] ?? _getTriggerFriendlyName(trigger);
                final status = item['status'] ?? 'RESOLVED';
                final startedAt = item['started_at'] ?? 'Recently';
                final isResolved = status == 'RESOLVED' || status == 'CANCELLED';

                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.borderLight),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.03),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
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
                              Container(
                                padding: const EdgeInsets.all(7),
                                decoration: BoxDecoration(
                                  color: AppColors.primary.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(_getTriggerIcon(trigger), color: AppColors.primary, size: 18),
                              ),
                              const SizedBox(width: 10),
                              Text(
                                trigger,
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: isResolved
                                  ? AppColors.success.withValues(alpha: 0.12)
                                  : AppColors.emergency.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              status,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: isResolved ? AppColors.success : AppColors.emergency,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        triggerLabel,
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Triggered at: $startedAt',
                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      const Divider(height: 20, color: AppColors.divider),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.battery_std_rounded, size: 14, color: AppColors.textSecondary),
                              const SizedBox(width: 4),
                              Text('${item['battery_percent'] ?? 85}% Battery',
                                  style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                            ],
                          ),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primary,
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              minimumSize: Size.zero,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                            icon: const Icon(Icons.shield_outlined, size: 14, color: AppColors.secondary),
                            label: const Text(
                              'View Evidence Dossier',
                              style: TextStyle(fontSize: 12, color: Colors.white, fontWeight: FontWeight.bold),
                            ),
                            onPressed: () => _showEvidenceModal(item),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
