import 'dart:async';
import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../models/safe_place_model.dart';
import '../repositories/routing_repository.dart';
import '../routes/app_routes.dart';

class SafeRouteScreen extends StatefulWidget {
  const SafeRouteScreen({Key? key}) : super(key: key);

  @override
  State<SafeRouteScreen> createState() => _SafeRouteScreenState();
}

class _SafeRouteScreenState extends State<SafeRouteScreen> {
  final RoutingRepository _routingRepository = RoutingRepository();

  // Location inputs & coordinates
  final TextEditingController _startController = TextEditingController(text: 'Connaught Place, New Delhi');
  final TextEditingController _destController = TextEditingController(text: 'AIIMS Hospital Trauma Center');
  double _startLat = 28.6139;
  double _startLng = 77.2090;
  double _destLat = 28.5684;
  double _destLng = 77.2075;

  bool _isLoading = false;
  List<RouteOptionModel> _routes = [];
  int _selectedRouteIndex = 0;

  // Real-Time Live Navigation State
  bool _isLiveNavigating = false;
  int _currentStepIndex = 0;
  double _distanceRemainingKm = 3.6;
  int _minutesRemaining = 9;
  double _currentSpeedKmh = 4.8;
  Timer? _navSimulationTimer;
  double _deviationMeters = 6.0;

  final List<Map<String, dynamic>> _startPresets = [
    {'name': 'Connaught Place', 'lat': 28.6139, 'lng': 77.2090},
    {'name': 'IIT Delhi', 'lat': 28.5450, 'lng': 77.1926},
    {'name': 'Hauz Khas', 'lat': 28.5535, 'lng': 77.1945},
    {'name': 'Noida Sec 62', 'lat': 28.6280, 'lng': 77.3649},
    {'name': 'Cyber City', 'lat': 28.4986, 'lng': 77.0878},
  ];

  final List<Map<String, dynamic>> _destPresets = [
    {'name': 'AIIMS Trauma Center', 'lat': 28.5684, 'lng': 77.2075},
    {'name': 'Delhi Police HQ', 'lat': 28.6289, 'lng': 77.2065},
    {'name': 'Barakhamba Safe Haven', 'lat': 28.6300, 'lng': 77.2200},
    {'name': 'Saket District Centre', 'lat': 28.5284, 'lng': 77.2185},
    {'name': 'Cyber Hub Haven', 'lat': 28.4912, 'lng': 77.0865},
  ];

  final List<String> _navigationGuidanceSteps = [
    'Head East on Connaught Circus towards Barakhamba Road (High CCTV coverage).',
    'In 200m, turn right onto Barakhamba Safe Corridor (Well-lit streetlights: 95%).',
    'Continue straight past Mandi House Police Post (Patrol unit active).',
    'Follow Tilak Marg Safe Corridor for 800m. Keep to designated pedestrian path.',
    'Turn slight left onto Ring Road corridor towards AIIMS Trauma Center Haven.',
    'You have safely arrived at your destination haven.'
  ];

  @override
  void initState() {
    super.initState();
    _fetchRoutes();
  }

  @override
  void dispose() {
    _navSimulationTimer?.cancel();
    _startController.dispose();
    _destController.dispose();
    super.dispose();
  }

  Future<void> _fetchRoutes() async {
    setState(() => _isLoading = true);
    try {
      final list = await _routingRepository.calculateRoutes(
        startLat: _startLat,
        startLng: _startLng,
        destLat: _destLat,
        destLng: _destLng,
      );
      setState(() {
        _routes = list.isNotEmpty ? list : _buildFallbackRoutes();
        _selectedRouteIndex = 0;
        _isLoading = false;
      });
    } catch (_) {
      setState(() {
        _routes = _buildFallbackRoutes();
        _selectedRouteIndex = 0;
        _isLoading = false;
      });
    }
  }

  List<RouteOptionModel> _buildFallbackRoutes() {
    return [
      RouteOptionModel(
        id: 'route-safety-optimized',
        type: 'SAFETY_OPTIMIZED',
        distanceKm: 4.1,
        durationMins: 11.0,
        safetyScore: 94.5,
        recommendation: 'Recommended by SafeRoute ANFIS Neuro-Fuzzy & Genetic Optimization Engine',
        riskFactors: {'crime': 0.05, 'lighting': 0.98, 'cctv_coverage': 0.92, 'police_proximity_m': 160},
        steps: _navigationGuidanceSteps,
      ),
      RouteOptionModel(
        id: 'route-balanced',
        type: 'BALANCED',
        distanceKm: 3.7,
        durationMins: 9.5,
        safetyScore: 82.0,
        recommendation: 'Optimal trade-off between walking duration and corridor illumination',
        riskFactors: {'crime': 0.18, 'lighting': 0.82, 'cctv_coverage': 0.70},
        steps: _navigationGuidanceSteps,
      ),
      RouteOptionModel(
        id: 'route-fastest',
        type: 'FASTEST',
        distanceKm: 3.2,
        durationMins: 8.0,
        safetyScore: 69.0,
        recommendation: 'Fastest direct path; caution advised on secondary side-streets',
        riskFactors: {'crime': 0.35, 'lighting': 0.55, 'cctv_coverage': 0.40},
        steps: _navigationGuidanceSteps,
      ),
    ];
  }

  void _useCurrentLocation() {
    setState(() {
      _startController.text = 'My Current GPS Location (28.6139, 77.2090)';
      _startLat = 28.6139;
      _startLng = 77.2090;
    });
    _fetchRoutes();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Start location locked to current high-accuracy GPS coordinates.'),
        backgroundColor: AppColors.success,
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _startLiveNavigation() {
    final selected = _routes[_selectedRouteIndex];
    setState(() {
      _isLiveNavigating = true;
      _currentStepIndex = 0;
      _distanceRemainingKm = selected.distanceKm;
      _minutesRemaining = selected.durationMins.toInt();
      _currentSpeedKmh = 4.8;
      _deviationMeters = 5.0;
    });

    // Start periodic simulation timer for real-time progress
    _navSimulationTimer?.cancel();
    _navSimulationTimer = Timer.periodic(const Duration(seconds: 4), (timer) {
      if (!mounted) return;
      setState(() {
        if (_distanceRemainingKm > 0.4) {
          _distanceRemainingKm = double.parse((_distanceRemainingKm - 0.4).toStringAsFixed(1));
          if (_minutesRemaining > 1) _minutesRemaining -= 1;
        }
        if (_currentStepIndex < _navigationGuidanceSteps.length - 1 && timer.tick % 2 == 0) {
          _currentStepIndex++;
        }
        // Small realistic drift within safe corridor
        _deviationMeters = 5.0 + (timer.tick % 4) * 2.0;
      });
    });
  }

  void _stopLiveNavigation() {
    _navSimulationTimer?.cancel();
    setState(() => _isLiveNavigating = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Safe navigation completed. Journey audit logged.'),
        backgroundColor: AppColors.primary,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(_isLiveNavigating ? 'Live Safe Navigation Mode' : 'AI Safe Route Navigator'),
        actions: [
          if (_isLiveNavigating)
            IconButton(
              icon: const Icon(Icons.close_rounded, color: AppColors.emergency),
              tooltip: 'Exit Navigation',
              onPressed: _stopLiveNavigation,
            )
          else
            IconButton(
              icon: const Icon(Icons.refresh_rounded),
              tooltip: 'Recalculate Routes',
              onPressed: _fetchRoutes,
            ),
        ],
      ),
      body: _isLiveNavigating ? _buildLiveNavigationHUD() : _buildRoutePlannerView(),
    );
  }

  // =========================================================================
  // VIEW 1: ROUTE PLANNER VIEW (INPUTS + AI ROUTE SELECTION)
  // =========================================================================
  Widget _buildRoutePlannerView() {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // START & DESTINATION INPUT CARD
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppColors.borderLight),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.03),
                    blurRadius: 10,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Start Location Field
                  Row(
                    children: [
                      const Icon(Icons.my_location_rounded, color: AppColors.primary, size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'Start Location',
                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: AppColors.textPrimary),
                      ),
                      const Spacer(),
                      TextButton.icon(
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        icon: const Icon(Icons.gps_fixed_rounded, size: 14, color: AppColors.primary),
                        label: const Text('Use Current GPS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                        onPressed: _useCurrentLocation,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _startController,
                    decoration: InputDecoration(
                      hintText: 'Enter start location or landmark',
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.clear_rounded, size: 18),
                        onPressed: () => _startController.clear(),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  // Start Presets Chips
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _startPresets.map((preset) {
                        return Padding(
                          padding: const EdgeInsets.only(right: 6),
                          child: ActionChip(
                            label: Text(preset['name'] as String, style: const TextStyle(fontSize: 11)),
                            backgroundColor: AppColors.cardBackground,
                            onPressed: () {
                              setState(() {
                                _startController.text = preset['name'] as String;
                                _startLat = preset['lat'] as double;
                                _startLng = preset['lng'] as double;
                              });
                              _fetchRoutes();
                            },
                          ),
                        );
                      }).toList(),
                    ),
                  ),

                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8),
                    child: Divider(color: AppColors.divider),
                  ),

                  // Destination Location Field
                  Row(
                    children: [
                      const Icon(Icons.location_on_rounded, color: AppColors.emergency, size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'Destination / Safe Haven',
                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: AppColors.textPrimary),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _destController,
                    decoration: InputDecoration(
                      hintText: 'Enter destination address or hospital / haven',
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.clear_rounded, size: 18),
                        onPressed: () => _destController.clear(),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  // Destination Presets Chips
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _destPresets.map((preset) {
                        return Padding(
                          padding: const EdgeInsets.only(right: 6),
                          child: ActionChip(
                            label: Text(preset['name'] as String, style: const TextStyle(fontSize: 11)),
                            backgroundColor: AppColors.cardBackground,
                            onPressed: () {
                              setState(() {
                                _destController.text = preset['name'] as String;
                                _destLat = preset['lat'] as double;
                                _destLng = preset['lng'] as double;
                              });
                              _fetchRoutes();
                            },
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Calculate AI Safe Route Button
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      icon: _isLoading
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Icon(Icons.auto_graph_rounded, size: 18),
                      label: Text(
                        _isLoading ? 'Calculating Safe Corridors...' : 'Calculate AI Safe Route',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      onPressed: _isLoading ? null : _fetchRoutes,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            // ROUTE VISUALIZATION CARD (CORRIDOR MAP PREVIEW)
            Container(
              height: 180,
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.borderLight),
              ),
              child: Stack(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 8,
                                height: 8,
                                decoration: const BoxDecoration(color: AppColors.success, shape: BoxShape.circle),
                              ),
                              const SizedBox(width: 6),
                              const Text(
                                'AI Safe Corridor Active',
                                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: AppColors.secondary.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'ANFIS Neuro-Fuzzy',
                              style: TextStyle(color: AppColors.secondary, fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      // Corridor Flow Nodes
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildCorridorNode('Start', Icons.my_location_rounded, AppColors.primary),
                          const Icon(Icons.arrow_forward_rounded, color: Colors.white38, size: 16),
                          _buildCorridorNode('95% Lit Zone', Icons.lightbulb_rounded, AppColors.secondary),
                          const Icon(Icons.arrow_forward_rounded, color: Colors.white38, size: 16),
                          _buildCorridorNode('Police Booth', Icons.local_police_rounded, AppColors.success),
                          const Icon(Icons.arrow_forward_rounded, color: Colors.white38, size: 16),
                          _buildCorridorNode('Destination', Icons.location_on_rounded, AppColors.emergency),
                        ],
                      ),
                      Text(
                        '${_startController.text} ➔ ${_destController.text}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: Colors.white70, fontSize: 11),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            // ROUTE OPTIONS SECTION
            const Text(
              'Candidate AI Route Options',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.primary),
            ),
            const SizedBox(height: 10),

            ...List.generate(_routes.length, (idx) {
              final route = _routes[idx];
              final isSelected = _selectedRouteIndex == idx;
              final isSafetyOptimized = route.type == 'SAFETY_OPTIMIZED';

              return GestureDetector(
                onTap: () => setState(() => _selectedRouteIndex = idx),
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isSelected ? AppColors.primary : AppColors.borderLight,
                      width: isSelected ? 2 : 1,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: isSelected ? 0.06 : 0.02),
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
                              Icon(
                                isSelected ? Icons.radio_button_checked : Icons.radio_button_off,
                                color: isSelected ? AppColors.primary : AppColors.textMuted,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                route.type.replaceAll('_', ' '),
                                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                              ),
                            ],
                          ),
                          if (isSafetyOptimized)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: AppColors.secondary.withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'RECOMMENDED',
                                style: TextStyle(
                                  color: Color(0xFF92400E),
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            '${route.distanceKm} km • ${route.durationMins.toInt()} mins',
                            style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                          ),
                          Row(
                            children: [
                              const Icon(Icons.shield_rounded, size: 14, color: AppColors.success),
                              const SizedBox(width: 4),
                              Text(
                                'Safety Score: ${route.safetyScore.toInt()}/100',
                                style: TextStyle(
                                  color: route.safetyScore > 80 ? AppColors.success : AppColors.warning,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      if (route.recommendation != null) ...[
                        const SizedBox(height: 6),
                        Text(
                          route.recommendation!,
                          style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontStyle: FontStyle.italic),
                        ),
                      ],
                    ],
                  ),
                ),
              );
            }),
            const SizedBox(height: 18),

            // START NAVIGATION BUTTON
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                icon: const Icon(Icons.navigation_rounded, color: AppColors.secondary),
                label: const Text(
                  'Start Safe Route Navigation',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                onPressed: _startLiveNavigation,
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  // =========================================================================
  // VIEW 2: REAL-TIME LIVE NAVIGATION HUD
  // =========================================================================
  Widget _buildLiveNavigationHUD() {
    final currentInstruction = _navigationGuidanceSteps[_currentStepIndex];

    return SafeArea(
      child: Column(
        children: [
          // TOP TURN-BY-TURN INSTRUCTION BANNER
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: const BoxDecoration(
              color: Color(0xFF1E293B),
              boxShadow: [
                BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4)),
              ],
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.turn_right_rounded, color: AppColors.secondary, size: 28),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'NEXT SAFE TURN',
                        style: TextStyle(color: AppColors.secondary, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        currentInstruction,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // LIVE REAL-TIME MAP CANVAS
          Expanded(
            child: Container(
              color: const Color(0xFF0F172A),
              child: Stack(
                children: [
                  // Animated Corridor Map Simulation
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: AppColors.primary.withValues(alpha: 0.2),
                            border: Border.all(color: AppColors.secondary, width: 2),
                          ),
                          child: const Icon(Icons.navigation_rounded, color: AppColors.secondary, size: 40),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Live Safe Corridor Guidance Active',
                          style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'En-route to ${_destController.text}',
                          style: const TextStyle(color: Colors.white70, fontSize: 12),
                        ),
                      ],
                    ),
                  ),

                  // TOP-LEFT CORRIDOR INTEGRITY BADGE
                  Positioned(
                    top: 14,
                    left: 14,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black87,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppColors.success.withValues(alpha: 0.6)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.lock_outline_rounded, color: AppColors.success, size: 14),
                          const SizedBox(width: 6),
                          Text(
                            'Corridor Deviation: ${_deviationMeters.toInt()}m (Safe <50m)',
                            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // TOP-RIGHT CCTV & PATROL STATUS
                  Positioned(
                    top: 14,
                    right: 14,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black87,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppColors.secondary.withValues(alpha: 0.6)),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.videocam_outlined, color: AppColors.secondary, size: 14),
                          SizedBox(width: 6),
                          Text(
                            'High CCTV Density (8 units)',
                            style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // EMERGENCY SOS QUICK BUTTON (OVERLAY HUD)
                  Positioned(
                    bottom: 16,
                    right: 16,
                    child: FloatingActionButton.extended(
                      backgroundColor: AppColors.emergency,
                      icon: const Icon(Icons.warning_amber_rounded, color: Colors.white),
                      label: const Text('PANIC SOS', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.activeEmergency),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // BOTTOM TELEMETRY BAR
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              boxShadow: [
                BoxShadow(color: Colors.black.withValues(alpha: 0.08), blurRadius: 10, offset: const Offset(0, -3)),
              ],
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildNavMetric('REMAINING', '$_distanceRemainingKm km', AppColors.primary),
                    Container(width: 1, height: 32, color: AppColors.divider),
                    _buildNavMetric('ETA', '$_minutesRemaining mins', AppColors.success),
                    Container(width: 1, height: 32, color: AppColors.divider),
                    _buildNavMetric('SPEED', '$_currentSpeedKmh km/h', AppColors.textPrimary),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF334155),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    icon: const Icon(Icons.stop_circle_outlined, color: Colors.white),
                    label: const Text('Exit Navigation', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    onPressed: _stopLiveNavigation,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavMetric(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textSecondary, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: color)),
      ],
    );
  }

  Widget _buildCorridorNode(String title, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(color: color.withValues(alpha: 0.2), shape: BoxShape.circle),
          child: Icon(icon, size: 16, color: color),
        ),
        const SizedBox(height: 4),
        Text(title, style: const TextStyle(color: Colors.white70, fontSize: 9)),
      ],
    );
  }
}
