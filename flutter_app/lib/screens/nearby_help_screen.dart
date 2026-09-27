import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../models/safe_place_model.dart';
import '../repositories/routing_repository.dart';
import '../widgets/quick_action_tile.dart';

class NearbyHelpScreen extends StatefulWidget {
  const NearbyHelpScreen({Key? key}) : super(key: key);

  @override
  State<NearbyHelpScreen> createState() => _NearbyHelpScreenState();
}

class _NearbyHelpScreenState extends State<NearbyHelpScreen> with SingleTickerProviderStateMixin {
  final RoutingRepository _routingRepository = RoutingRepository();
  late TabController _tabController;
  bool _isLoading = true;
  List<SafePlaceModel> _police = [];
  List<SafePlaceModel> _hospitals = [];
  List<SafePlaceModel> _safePlaces = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadNearbyPlaces();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadNearbyPlaces() async {
    setState(() => _isLoading = true);
    try {
      final policeList = await _routingRepository.getNearbyPolice();
      final hospitalList = await _routingRepository.getNearbyHospitals();
      final safeList = await _routingRepository.getNearbySafePlaces();
      setState(() {
        _police = policeList;
        _hospitals = hospitalList;
        _safePlaces = safeList;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Nearby Safe Places & Help'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _loadNearbyPlaces,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          indicatorColor: AppColors.primary,
          tabs: const [
            Tab(text: 'Police'),
            Tab(text: 'Hospitals'),
            Tab(text: 'Safe Havens'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : TabBarView(
              controller: _tabController,
              children: [
                _buildPlaceList(_police, 'POLICE'),
                _buildPlaceList(_hospitals, 'HOSPITAL'),
                _buildPlaceList(_safePlaces, 'SAFE_PLACE'),
              ],
            ),
    );
  }

  Widget _buildPlaceList(List<SafePlaceModel> places, String category) {
    if (places.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                category == 'POLICE'
                    ? Icons.local_police_outlined
                    : (category == 'HOSPITAL' ? Icons.local_hospital_outlined : Icons.verified_user_outlined),
                size: 50,
                color: AppColors.textMuted,
              ),
              const SizedBox(height: 12),
              const Text(
                'No verified places within immediate range',
                style: TextStyle(fontWeight: FontWeight.w600, color: AppColors.textSecondary),
              ),
            ],
          ),
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: places.length,
      itemBuilder: (context, index) {
        final p = places[index];
        return NearbyPlaceCard(
          name: p.name,
          category: category,
          distanceMeters: p.distanceMeters,
          onNavigate: () {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Starting high-priority navigation to ${p.name}...'),
                backgroundColor: AppColors.primary,
              ),
            );
          },
          onCall: (p.phone != null && p.phone!.isNotEmpty)
              ? () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Initiating direct emergency call to ${p.phone}...'),
                      backgroundColor: AppColors.secondary,
                    ),
                  );
                }
              : null,
        );
      },
    );
  }
}
