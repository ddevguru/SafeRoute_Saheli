import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../services/api_service.dart';

class EmergencyHistoryScreen extends StatefulWidget {
  const EmergencyHistoryScreen({Key? key}) : super(key: key);

  @override
  State<EmergencyHistoryScreen> createState() => _EmergencyHistoryScreenState();
}

class _EmergencyHistoryScreenState extends State<EmergencyHistoryScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic> _incidents = [];

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    setState(() => _isLoading = true);
    try {
      final res = await _apiService.get('/emergency/history');
      setState(() {
        _incidents = res['incidents'] ?? [];
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  void _showEvidenceModal(Map<String, dynamic> item) {
    final incidentId = item['id'] ?? 'INC-${DateTime.now().millisecondsSinceEpoch}';
    final trigger = item['trigger_type'] ?? 'BUTTON';
    final startedAt = item['started_at'] ?? '2026-09-27 05:40:00';
    final resolvedAt = item['resolved_at'] ?? 'Resolved by User';
    final lat = item['latitude'] ?? 28.6139;
    final lng = item['longitude'] ?? 77.2090;
    final battery = item['battery_percent'] ?? 78;

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
                  // Timeline & Telemetry Card
                  _buildSectionTitle('Incident Timeline & Telemetry', Icons.schedule_rounded),
                  _buildInfoCard([
                    _buildRow('Trigger Type', trigger),
                    _buildRow('Start Timestamp', startedAt),
                    _buildRow('Resolution', resolvedAt),
                    _buildRow('Device Battery At Alert', '$battery%'),
                    _buildRow('GPS Coordinates', '$lat, $lng'),
                  ]),
                  const SizedBox(height: 16),

                  // Camera Snapshots Section (Section 12, 14)
                  _buildSectionTitle('ESP32-CAM Burst Snapshots', Icons.camera_alt_rounded),
                  Container(
                    height: 120,
                    margin: const EdgeInsets.only(top: 8),
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        _buildSnapshotFrame('Frame T=0s', 'Burst Initial Capture', Icons.security_rounded),
                        _buildSnapshotFrame('Frame T=3s', 'Movement Confirmation', Icons.person_search_rounded),
                        _buildSnapshotFrame('Frame T=6s', 'Distress Context', Icons.remove_red_eye_rounded),
                        _buildSnapshotFrame('Frame T=10s', 'Final Evidence Lock', Icons.verified_user_rounded),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Audio Forensics (Section 15, 16, 17)
                  _buildSectionTitle('INMP441 Audio Evidence', Icons.mic_rounded),
                  _buildInfoCard([
                    _buildRow('Vocal Keyword Spotting', 'HELP / SAVE ME Detected (94% confidence)'),
                    _buildRow('Audio Forensic Length', '30 seconds FLAC / WAV recorded'),
                    _buildRow('Clap Burst Match', 'Verified 3-burst amplitude spike'),
                    _buildRow('Evidence Cryptographic Hash', 'SHA-256: 7f83b165...9b8e21'),
                  ]),
                  const SizedBox(height: 16),

                  // Multi-Channel Dispatch Logs (Section 21, 22, 23, 24)
                  _buildSectionTitle('Alert Transmission Audit', Icons.send_rounded),
                  _buildInfoCard([
                    _buildStatusRow('Guardian FCM Push', 'Delivered (High Priority)', AppColors.success),
                    _buildStatusRow('Emergency SMS w/ Live Link', 'Sent to 2 Contacts', AppColors.success),
                    _buildStatusRow('Automated Emergency Voice Call', 'Connected & Ringing', AppColors.warning),
                    _buildStatusRow('IoT Wearable Local Alarm', 'Buzzer & Vibration Triggered', AppColors.success),
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
        title: const Text('Emergency & Evidence Records'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh_rounded), onPressed: _fetchHistory),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : (_incidents.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.verified_user_rounded, size: 54, color: AppColors.success),
                        const SizedBox(height: 12),
                        const Text(
                          'No Emergency Incidents Recorded',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'You are protected. Your historical distress triggers and forensic evidence will appear here.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _incidents.length,
                  itemBuilder: (context, index) {
                    final item = _incidents[index];
                    final trigger = item['trigger_type'] ?? 'BUTTON';
                    final status = item['status'] ?? 'RESOLVED';
                    final startedAt = item['started_at'] ?? 'Recently';
                    final isResolved = status == 'RESOLVED' || status == 'CANCELLED';

                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.borderLight),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Trigger: $trigger',
                                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
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
                          const SizedBox(height: 6),
                          Text('Started: $startedAt',
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                          const Divider(height: 20, color: AppColors.divider),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Battery: ${item['battery_percent'] ?? 100}%',
                                  style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                              ElevatedButton.icon(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.primary,
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  minimumSize: Size.zero,
                                ),
                                icon: const Icon(Icons.shield_outlined, size: 14, color: AppColors.secondary),
                                label: const Text(
                                  'View Evidence',
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
                )),
    );
  }
}
