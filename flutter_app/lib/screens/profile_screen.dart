import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/auth_bloc.dart';
import '../constants/app_colors.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _apiService = ApiService();

  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _emailController;
  late TextEditingController _medicalNotesController;
  String _selectedBloodGroup = 'B+';
  bool _isSaving = false;
  bool _isLoadingContacts = true;
  List<dynamic> _contacts = [];

  final List<String> _bloodGroups = [
    'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-', 'Unknown'
  ];

  @override
  void initState() {
    super.initState();
    final authState = context.read<AuthBloc>().state;
    UserModel? user;
    if (authState is AuthenticatedState) {
      user = authState.user;
    }

    _nameController = TextEditingController(text: user?.name ?? 'Saheli User');
    _phoneController = TextEditingController(text: user?.phone ?? '+91 9876543210');
    _emailController = TextEditingController(text: user?.email ?? 'saheli@example.com');
    _medicalNotesController = TextEditingController(text: user?.medicalNotes ?? 'Asthmatic, carries emergency inhaler.');
    _selectedBloodGroup = user?.emergencyBloodGroup ?? 'B+';
    if (!_bloodGroups.contains(_selectedBloodGroup)) {
      _selectedBloodGroup = 'B+';
    }

    _fetchEmergencyContacts();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _medicalNotesController.dispose();
    super.dispose();
  }

  Future<void> _fetchEmergencyContacts() async {
    try {
      final res = await _apiService.get('/auth/emergency-contacts');
      setState(() {
        _contacts = res['contacts'] ?? [];
        _isLoadingContacts = false;
      });
    } catch (_) {
      setState(() {
        _contacts = [
          {
            'id': 'contact-1',
            'name': 'Mother (Kavita Sharma)',
            'phone': '+91 98765 11111',
            'relationship': 'Mother',
            'notify_sms': true,
            'notify_call': true,
          },
          {
            'id': 'contact-2',
            'name': 'Sister (Priya Sharma)',
            'phone': '+91 98765 22222',
            'relationship': 'Sister',
            'notify_sms': true,
            'notify_call': false,
          },
        ];
        _isLoadingContacts = false;
      });
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSaving = true);

    context.read<AuthBloc>().add(
      UpdateProfileEvent(
        name: _nameController.text.trim(),
        phone: _phoneController.text.trim(),
        bloodGroup: _selectedBloodGroup,
        medicalNotes: _medicalNotesController.text.trim(),
      ),
    );

    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;
    setState(() => _isSaving = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Profile and Emergency Medical Info saved successfully!'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  void _showAddContactDialog() {
    final nameCtrl = TextEditingController();
    final phoneCtrl = TextEditingController();
    String relationship = 'Family';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text('Add Emergency Contact', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameCtrl,
                  decoration: InputDecoration(
                    labelText: 'Full Name',
                    prefixIcon: const Icon(Icons.person_outline),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: phoneCtrl,
                  keyboardType: TextInputType.phone,
                  decoration: InputDecoration(
                    labelText: 'Phone Number',
                    prefixIcon: const Icon(Icons.phone_outlined),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: relationship,
                  decoration: InputDecoration(
                    labelText: 'Relationship',
                    prefixIcon: const Icon(Icons.favorite_outline),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'Mother', child: Text('Mother')),
                    DropdownMenuItem(value: 'Father', child: Text('Father')),
                    DropdownMenuItem(value: 'Sister', child: Text('Sister')),
                    DropdownMenuItem(value: 'Brother', child: Text('Brother')),
                    DropdownMenuItem(value: 'Friend', child: Text('Friend / Flatmate')),
                    DropdownMenuItem(value: 'Family', child: Text('Other Family')),
                  ],
                  onChanged: (val) {
                    if (val != null) setDialogState(() => relationship = val);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
              onPressed: () async {
                final n = nameCtrl.text.trim();
                final p = phoneCtrl.text.trim();
                if (n.isEmpty || p.isEmpty) return;

                Navigator.pop(ctx);
                try {
                  await _apiService.post('/auth/emergency-contacts', body: {
                    'name': n,
                    'phone': p,
                    'relationship': relationship,
                  });
                } catch (_) {}

                setState(() {
                  _contacts.add({
                    'id': 'contact-${DateTime.now().millisecondsSinceEpoch}',
                    'name': n,
                    'phone': p,
                    'relationship': relationship,
                    'notify_sms': true,
                    'notify_call': true,
                  });
                });

                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Contact $n added to emergency circle.'),
                    backgroundColor: AppColors.success,
                  ),
                );
              },
              child: const Text('Add Contact', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  void _removeContact(int index) {
    final item = _contacts[index];
    setState(() => _contacts.removeAt(index));
    try {
      if (item['id'] != null) {
        _apiService.delete('/auth/emergency-contacts/${item['id']}');
      }
    } catch (_) {}
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Contact removed from emergency circle.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('My Profile & Emergency Info'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Avatar & Identity Card
                Center(
                  child: Column(
                    children: [
                      Stack(
                        children: [
                          CircleAvatar(
                            radius: 46,
                            backgroundColor: AppColors.primary.withValues(alpha: 0.15),
                            child: const Icon(
                              Icons.person_rounded,
                              size: 52,
                              color: AppColors.primary,
                            ),
                          ),
                          Positioned(
                            bottom: 0,
                            right: 0,
                            child: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: const BoxDecoration(
                                color: AppColors.primary,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.edit, size: 14, color: Colors.white),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        _nameController.text,
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
                      ),
                      const SizedBox(height: 2),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.success.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          '● Verified Protected Saheli',
                          style: TextStyle(color: AppColors.success, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Section 1: Personal Details
                _buildSectionHeader('Personal Information', Icons.badge_outlined),
                const SizedBox(height: 12),
                _buildCard([
                  TextFormField(
                    controller: _nameController,
                    decoration: InputDecoration(
                      labelText: 'Full Name',
                      prefixIcon: const Icon(Icons.person_outline),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    validator: (v) => (v == null || v.trim().isEmpty) ? 'Please enter your name' : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: 'Mobile Phone Number',
                      prefixIcon: const Icon(Icons.phone_android_rounded),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    validator: (v) => (v == null || v.trim().isEmpty) ? 'Please enter phone number' : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _emailController,
                    enabled: false,
                    decoration: InputDecoration(
                      labelText: 'Email Address (Registered)',
                      prefixIcon: const Icon(Icons.mail_outline_rounded),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      filled: true,
                      fillColor: Colors.grey.shade100,
                    ),
                  ),
                ]),

                const SizedBox(height: 24),

                // Section 2: Emergency Medical Information
                _buildSectionHeader('Emergency Medical Dossier', Icons.medical_services_outlined),
                const SizedBox(height: 12),
                _buildCard([
                  DropdownButtonFormField<String>(
                    initialValue: _selectedBloodGroup,
                    decoration: InputDecoration(
                      labelText: 'Emergency Blood Group',
                      prefixIcon: const Icon(Icons.bloodtype_rounded, color: AppColors.emergency),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    items: _bloodGroups
                        .map((bg) => DropdownMenuItem(value: bg, child: Text(bg)))
                        .toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedBloodGroup = val);
                    },
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _medicalNotesController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      labelText: 'Critical Medical Notes / Allergies',
                      hintText: 'e.g. Asthmatic, carries inhaler. Penicillin allergy. Contact mother for medical consent.',
                      prefixIcon: const Icon(Icons.note_alt_outlined),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ]),

                const SizedBox(height: 24),

                // Section 3: Emergency Contacts Manager
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildSectionHeader('Emergency Contacts Circle', Icons.family_restroom_rounded),
                    IconButton(
                      icon: const Icon(Icons.person_add_alt_1_rounded, color: AppColors.primary),
                      tooltip: 'Add Contact',
                      onPressed: _showAddContactDialog,
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                _buildCard([
                  if (_isLoadingContacts)
                    const Center(child: Padding(
                      padding: EdgeInsets.all(12),
                      child: CircularProgressIndicator(),
                    ))
                  else if (_contacts.isEmpty)
                    const Padding(
                      padding: EdgeInsets.all(16),
                      child: Center(
                        child: Text(
                          'No emergency contacts added yet. Click + to add.',
                          style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
                        ),
                      ),
                    )
                  else
                    ...List.generate(_contacts.length, (idx) {
                      final c = _contacts[idx];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.background,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.borderLight),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                CircleAvatar(
                                  radius: 18,
                                  backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                                  child: const Icon(Icons.person, size: 20, color: AppColors.primary),
                                ),
                                const SizedBox(width: 10),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      c['name'] ?? 'Contact',
                                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                                    ),
                                    Text(
                                      '${c['phone']} • ${c['relationship'] ?? "Family"}',
                                      style: const TextStyle(color: AppColors.textSecondary, fontSize: 11),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline_rounded, color: AppColors.emergency, size: 20),
                              onPressed: () => _removeContact(idx),
                            ),
                          ],
                        ),
                      );
                    }),
                ]),

                const SizedBox(height: 28),

                // Save Profile Button
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    icon: _isSaving
                        ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Icon(Icons.save_rounded),
                    label: Text(
                      _isSaving ? 'Saving...' : 'Save Profile Changes',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    onPressed: _isSaving ? null : _saveProfile,
                  ),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppColors.primary),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: AppColors.textPrimary),
        ),
      ],
    );
  }

  Widget _buildCard(List<Widget> children) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(children: children),
    );
  }
}
