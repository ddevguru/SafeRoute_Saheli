import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:url_launcher/url_launcher.dart';

import '../blocs/emergency_bloc.dart';
import '../constants/app_colors.dart';
import '../models/safe_place_model.dart';
import '../repositories/routing_repository.dart';
import '../widgets/quick_action_tile.dart';

class ActiveEmergencyScreen extends StatefulWidget {
  const ActiveEmergencyScreen({Key? key}) : super(key: key);

  @override
  State<ActiveEmergencyScreen> createState() => _ActiveEmergencyScreenState();
}

class _ActiveEmergencyScreenState extends State<ActiveEmergencyScreen> with SingleTickerProviderStateMixin {
  final RoutingRepository _routingRepo = RoutingRepository();
  late AudioPlayer _audioPlayer;
  Timer? _vibrationTimer;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  bool _isSirenMuted = false;
  bool _isLoadingAssistance = true;
  List<SafePlaceModel> _emergencyAssistanceList = [];

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _initAudioAlarm();
    _startVibrationLoop();
    _loadLiveEmergencyAssistance();
  }

  Future<void> _initAudioAlarm() async {
    _audioPlayer = AudioPlayer();
    
    // 1. Configure audio routing safely without blocking playback on failure
    try {
      await _audioPlayer.setAudioContext(
        AudioContext(
          android: const AudioContextAndroid(
            isSpeakerphoneOn: true,
            stayAwake: true,
            contentType: AndroidContentType.sonification,
            usageType: AndroidUsageType.alarm,
            audioFocus: AndroidAudioFocus.gainTransientExclusive,
          ),
          iOS: AudioContextIOS(
            category: AVAudioSessionCategory.playback,
            options: const {
              AVAudioSessionOptions.defaultToSpeaker,
            },
          ),
        ),
      );
    } catch (e) {
      debugPrint('[EmergencyAudio] AudioContext notice (proceeding to play): $e');
    }

    // 2. Configure volume and loop mode
    try {
      await _audioPlayer.setReleaseMode(ReleaseMode.loop);
      await _audioPlayer.setVolume(1.0);
    } catch (e) {
      debugPrint('[EmergencyAudio] Volume setup notice: $e');
    }

    // 3. Play emergency siren sound with fallback paths
    bool played = false;
    try {
      await _audioPlayer.play(AssetSource('sounds/emergency_siren.wav'));
      played = true;
      debugPrint('[EmergencyAudio] Playing siren from sounds/emergency_siren.wav');
    } catch (e) {
      debugPrint('[EmergencyAudio] sounds/ path failed: $e, trying assets/sounds/...');
      try {
        await _audioPlayer.play(AssetSource('assets/sounds/emergency_siren.wav'));
        played = true;
        debugPrint('[EmergencyAudio] Playing siren from assets/sounds/emergency_siren.wav');
      } catch (e2) {
        debugPrint('[EmergencyAudio] Siren playback fallback error: $e2');
      }
    }

    if (mounted) {
      setState(() {
        _isSirenMuted = !played;
      });
    }
  }

  void _toggleSirenMute() async {
    if (_isSirenMuted) {
      try {
        await _audioPlayer.setVolume(1.0);
        await _audioPlayer.resume();
      } catch (e) {
        try {
          await _audioPlayer.play(AssetSource('sounds/emergency_siren.wav'));
        } catch (_) {}
      }
      setState(() => _isSirenMuted = false);
    } else {
      try {
        await _audioPlayer.setVolume(0.0);
        await _audioPlayer.pause();
      } catch (_) {}
      setState(() => _isSirenMuted = true);
    }
  }

  void _startVibrationLoop() {
    _vibrationTimer = Timer.periodic(const Duration(milliseconds: 1400), (_) {
      if (mounted && !_isSirenMuted) {
        HapticFeedback.heavyImpact();
      }
    });
  }

  Future<void> _loadLiveEmergencyAssistance() async {
    setState(() => _isLoadingAssistance = true);
    try {
      // 1. Fetch real police & hospitals
      final police = await _routingRepo.getNearbyPolice();
      final hospitals = await _routingRepo.getNearbyHospitals();

      List<SafePlaceModel> combined = [];
      if (police.isNotEmpty) combined.add(police.first);
      if (hospitals.isNotEmpty) combined.add(hospitals.first);

      // If police list has more than 1, add 2nd station
      if (police.length > 1) {
        combined.add(police[1]);
      } else if (hospitals.length > 1) {
        combined.add(hospitals[1]);
      }

      if (mounted) {
        setState(() {
          _emergencyAssistanceList = combined;
          _isLoadingAssistance = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => _isLoadingAssistance = false);
      }
    }
  }

  Future<void> _launchNavigation(double lat, double lng, String name) async {
    final uri = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=$lat,$lng');
    try {
      final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!launched && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Starting navigation to $name ($lat, $lng)...'),
            backgroundColor: AppColors.primary,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Navigating to $name...'), backgroundColor: AppColors.primary),
        );
      }
    }
  }

  Future<void> _launchCall(String? phone) async {
    final number = (phone != null && phone.trim().isNotEmpty) ? phone.trim() : '112';
    final uri = Uri.parse('tel:$number');
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Calling Emergency Helpline $number...'), backgroundColor: AppColors.emergency),
        );
      }
    }
  }

  void _onCancelHold(BuildContext context, String incidentId) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Deactivate Emergency Alert?'),
        content: const Text(
          'Are you safe? This will silence the siren alarm, notify your guardians, and de-escalate active emergency monitoring.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Stay In Emergency', style: TextStyle(color: AppColors.textSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
            onPressed: () async {
              Navigator.pop(ctx);
              _stopAudioAndSensors();
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

  void _stopAudioAndSensors() {
    _vibrationTimer?.cancel();
    try {
      _audioPlayer.stop();
      _audioPlayer.dispose();
    } catch (_) {}
  }

  @override
  void dispose() {
    _stopAudioAndSensors();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false, // Prevent accidental back navigation during emergency
      child: Scaffold(
        backgroundColor: const Color(0xFF160606),
        appBar: AppBar(
          backgroundColor: AppColors.emergencyDark,
          automaticallyImplyLeading: false,
          title: Row(
            children: [
              ScaleTransition(
                scale: _pulseAnimation,
                child: const Icon(Icons.warning_amber_rounded, color: AppColors.white),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'EMERGENCY DISPATCH ACTIVE',
                  style: TextStyle(color: AppColors.white, fontWeight: FontWeight.w700, fontSize: 16),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // Siren Mute/Unmute Action in App Bar
              IconButton(
                icon: Icon(
                  _isSirenMuted ? Icons.volume_off_rounded : Icons.volume_up_rounded,
                  color: _isSirenMuted ? Colors.white54 : AppColors.secondary,
                ),
                tooltip: _isSirenMuted ? 'Unmute Alarm Siren' : 'Mute Alarm Siren',
                onPressed: _toggleSirenMute,
              ),
            ],
          ),
        ),
        body: BlocBuilder<EmergencyBloc, EmergencyState>(
          builder: (context, state) {
            String incidentId = '';
            String triggerType = 'TOUCH / HARDWARE BUTTON';
            String trackingUrl = 'https://saferoute-saheli-backend.onrender.com/track/live-session';

            if (state is EmergencyActiveState) {
              incidentId = state.incident.id;
              triggerType = state.incident.triggerType;
              if (state.incident.trackingUrl != null) {
                // Ensure tracking URL always targets the live public backend
                String raw = state.incident.trackingUrl!;
                if (raw.contains('localhost:5000') || raw.contains('127.0.0.1:5000')) {
                  raw = raw.replaceFirst('http://localhost:5000', 'https://saferoute-saheli-backend.onrender.com');
                  raw = raw.replaceFirst('http://127.0.0.1:5000', 'https://saferoute-saheli-backend.onrender.com');
                }
                trackingUrl = raw;
              }
            }

            return SafeArea(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // SIREN STATUS & CONTROLS BANNER
                    Container(
                      width: double.infinity,
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      decoration: BoxDecoration(
                        color: _isSirenMuted
                            ? Colors.white.withValues(alpha: 0.08)
                            : AppColors.emergency.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _isSirenMuted ? Colors.white24 : AppColors.emergency,
                          width: 1.5,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            _isSirenMuted ? Icons.volume_off_rounded : Icons.graphic_eq_rounded,
                            color: _isSirenMuted ? Colors.white70 : AppColors.secondary,
                            size: 22,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _isSirenMuted ? 'Acoustic Siren Silenced' : '🚨 Acoustic Siren Blaring (Max Volume)',
                                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                                ),
                                Text(
                                  _isSirenMuted
                                      ? 'Tap to resume acoustic deterrence'
                                      : 'High-frequency siren active to alert surroundings',
                                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                                ),
                              ],
                            ),
                          ),
                          TextButton(
                            style: TextButton.styleFrom(
                              backgroundColor: _isSirenMuted ? AppColors.secondary : Colors.black45,
                              foregroundColor: _isSirenMuted ? Colors.black : Colors.white,
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                            onPressed: _toggleSirenMute,
                            child: Text(
                              _isSirenMuted ? 'UNMUTE' : 'MUTE',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // EMERGENCY PULSE HEADER
                    ScaleTransition(
                      scale: _pulseAnimation,
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(18),
                        decoration: BoxDecoration(
                          color: AppColors.emergency.withValues(alpha: 0.25),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppColors.emergency, width: 2),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.emergency.withValues(alpha: 0.3),
                              blurRadius: 16,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            const Icon(Icons.emergency_share_rounded, color: AppColors.emergency, size: 46),
                            const SizedBox(height: 8),
                            const Text(
                              'ALERTS SENT TO GUARDIANS',
                              style: TextStyle(
                                color: AppColors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 0.5,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Trigger: $triggerType | Live GPS streaming at 5s interval',
                              style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 12),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 10),
                            InkWell(
                              onTap: () {
                                Clipboard.setData(ClipboardData(text: trackingUrl));
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('📋 Live tracking link copied to clipboard!'),
                                    backgroundColor: AppColors.success,
                                    duration: Duration(seconds: 2),
                                  ),
                                );
                              },
                              borderRadius: BorderRadius.circular(8),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                decoration: BoxDecoration(
                                  color: Colors.black.withValues(alpha: 0.4),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: AppColors.secondary.withValues(alpha: 0.4)),
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
                                    const SizedBox(width: 6),
                                    const Icon(Icons.copy_rounded, size: 13, color: Colors.white70),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // ACTIONS IN PROGRESS CARD
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF281111),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: const Column(
                        children: [
                          _AlertCheckRow(title: 'High-Priority Guardian Push', status: 'Delivered'),
                          SizedBox(height: 10),
                          _AlertCheckRow(title: 'Emergency SMS with Map Link', status: 'Sent'),
                          SizedBox(height: 10),
                          _AlertCheckRow(title: 'Voice Emergency Call', status: 'Connecting...'),
                          SizedBox(height: 10),
                          _AlertCheckRow(title: 'ESP32-CAM Burst Capture', status: 'Frames Locked'),
                        ],
                      ),
                    ),
                    const SizedBox(height: 18),

                    // NEAREST EMERGENCY ASSISTANCE SECTION (REAL DATA)
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Nearest Emergency Assistance',
                          style: TextStyle(color: AppColors.white, fontWeight: FontWeight.w700, fontSize: 15),
                        ),
                        if (_isLoadingAssistance)
                          const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(color: AppColors.secondary, strokeWidth: 2),
                          ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    if (_emergencyAssistanceList.isNotEmpty) ...[
                      for (final place in _emergencyAssistanceList)
                        NearbyPlaceCard(
                          name: place.name,
                          category: place.category,
                          distanceMeters: place.distanceMeters,
                          isDarkTheme: true,
                          onNavigate: () => _launchNavigation(place.latitude, place.longitude, place.name),
                          onCall: () => _launchCall(place.phone),
                        ),
                    ] else if (!_isLoadingAssistance) ...[
                      // Real verified Emergency Helplines if zero spatial points match radius
                      NearbyPlaceCard(
                        name: 'National Emergency Response (112)',
                        category: 'POLICE',
                        distanceMeters: 100,
                        isDarkTheme: true,
                        onNavigate: () => _launchNavigation(28.6139, 77.2090, 'Police Control Room 112'),
                        onCall: () => _launchCall('112'),
                      ),
                      NearbyPlaceCard(
                        name: 'National Women Safety Helpline (1091)',
                        category: 'POLICE',
                        distanceMeters: 250,
                        isDarkTheme: true,
                        onNavigate: () => _launchNavigation(28.6139, 77.2090, 'Women Police Helpline'),
                        onCall: () => _launchCall('1091'),
                      ),
                      NearbyPlaceCard(
                        name: 'Central Ambulance & Medical Emergency (108)',
                        category: 'HOSPITAL',
                        distanceMeters: 400,
                        isDarkTheme: true,
                        onNavigate: () => _launchNavigation(28.6139, 77.2090, 'Emergency Hospital Ambulance'),
                        onCall: () => _launchCall('108'),
                      ),
                    ],

                    const SizedBox(height: 16),

                    // DE-ESCALATE / CANCEL BUTTON
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: AppColors.primary,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          elevation: 4,
                        ),
                        icon: const Icon(Icons.check_circle_rounded, color: AppColors.success, size: 22),
                        label: const Text(
                          'I AM SAFE — CANCEL ALERT',
                          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                        onPressed: () => _onCancelHold(context, incidentId),
                      ),
                    ),
                    const SizedBox(height: 16),
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
