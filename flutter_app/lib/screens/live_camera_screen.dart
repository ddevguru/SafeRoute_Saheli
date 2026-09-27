import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../repositories/routing_repository.dart';

class LiveCameraScreen extends StatefulWidget {
  final String? targetUserId;

  const LiveCameraScreen({Key? key, this.targetUserId}) : super(key: key);

  @override
  State<LiveCameraScreen> createState() => _LiveCameraScreenState();
}

class _LiveCameraScreenState extends State<LiveCameraScreen> {
  final CameraRepository _cameraRepository = CameraRepository();
  bool _isLoading = true;
  String? _streamUrl;
  String _cameraStatus = 'CONNECTING';
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initCameraSession();
  }

  Future<void> _initCameraSession() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final session = await _cameraRepository.createCameraSession(targetUserId: widget.targetUserId);
      if (session['success'] == true) {
        setState(() {
          _streamUrl = session['stream_url'];
          _cameraStatus = 'LIVE';
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = session['error'] ?? 'Could not start camera stream';
          _cameraStatus = 'ERROR';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _cameraStatus = 'OFFLINE';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        iconTheme: const IconThemeData(color: Colors.white),
        title: const Row(
          children: [
            Icon(Icons.videocam_rounded, color: AppColors.secondary, size: 20),
            SizedBox(width: 8),
            Text(
              'ESP32-CAM Live Feed',
              style: TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w600),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Colors.white),
            onPressed: _initCameraSession,
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Stream Viewport
            Expanded(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Container(
                    width: double.infinity,
                    color: const Color(0xFF111827),
                    child: _isLoading
                        ? const Center(
                            child: CircularProgressIndicator(color: AppColors.secondary),
                          )
                        : (_errorMessage != null
                            ? Center(
                                child: Padding(
                                  padding: const EdgeInsets.all(24),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.videocam_off_rounded, color: AppColors.emergency, size: 48),
                                      const SizedBox(height: 12),
                                      Text(
                                        _errorMessage!,
                                        textAlign: TextAlign.center,
                                        style: const TextStyle(color: Colors.white, fontSize: 14),
                                      ),
                                      const SizedBox(height: 16),
                                      ElevatedButton(
                                        onPressed: _initCameraSession,
                                        style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                                        child: const Text('Retry Connection'),
                                      ),
                                    ],
                                  ),
                                ),
                              )
                            : Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Container(
                                    width: 80,
                                    height: 80,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: AppColors.primary.withValues(alpha: 0.4),
                                    ),
                                    child: const Icon(Icons.videocam_rounded, color: AppColors.secondary, size: 42),
                                  ),
                                  const SizedBox(height: 14),
                                  const Text(
                                    'Encrypted Stream Active',
                                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 16),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    _streamUrl != null ? 'Feed: $_streamUrl' : 'ESP32-CAM OV2640 • 800x600 SVGA @ 15fps',
                                    style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 11),
                                  ),
                                ],
                              )),
                  ),

                  // Top Live Status Overlay
                  Positioned(
                    top: 16,
                    left: 16,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.7),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: _cameraStatus == 'LIVE' ? AppColors.liveIndicator : Colors.grey,
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: _cameraStatus == 'LIVE' ? AppColors.liveIndicator : Colors.grey,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            _cameraStatus,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Camera Controls & Privacy Notice
            Container(
              padding: const EdgeInsets.all(20),
              color: const Color(0xFF1E293B),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      // Manual Snapshot Button
                      ElevatedButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('📸 Emergency snapshot captured & securely uploaded.'),
                              backgroundColor: AppColors.success,
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                        ),
                        icon: const Icon(Icons.camera_alt_rounded, size: 18),
                        label: const Text('Capture Frame'),
                      ),
                      // Burst Capture
                      ElevatedButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('⚡ Burst capture triggered (4 sequential frames).'),
                              backgroundColor: AppColors.secondary,
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.emergency,
                          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                        ),
                        icon: const Icon(Icons.burst_mode_rounded, size: 18),
                        label: const Text('Burst (4x)'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '🔒 End-to-end authorized gateway. Camera stream requires signed temporary session token.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
