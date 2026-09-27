import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../models/guardian_model.dart';
import '../repositories/guardian_repository.dart';

class GuardiansManagementScreen extends StatefulWidget {
  const GuardiansManagementScreen({Key? key}) : super(key: key);

  @override
  State<GuardiansManagementScreen> createState() => _GuardiansManagementScreenState();
}

class _GuardiansManagementScreenState extends State<GuardiansManagementScreen> {
  final GuardianRepository _guardianRepository = GuardianRepository();
  bool _isLoading = true;
  List<GuardianModel> _guardians = [];

  @override
  void initState() {
    super.initState();
    _loadGuardians();
  }

  Future<void> _loadGuardians() async {
    setState(() => _isLoading = true);
    try {
      final list = await _guardianRepository.getGuardians();
      setState(() {
        _guardians = list;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  void _showAddGuardianDialog() {
    final nameCtrl = TextEditingController();
    final relCtrl = TextEditingController(text: 'Mother');
    final phoneCtrl = TextEditingController();
    final emailCtrl = TextEditingController();
    final usernameCtrl = TextEditingController();
    final passwordCtrl = TextEditingController();

    bool canLocation = true;
    bool canCamera = false;
    bool isPrimary = false;
    bool obscurePassword = true;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => Container(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            top: 24,
            left: 24,
            right: 24,
          ),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.person_add_alt_1_rounded, color: AppColors.primary),
                    SizedBox(width: 8),
                    Text(
                      'Add & Link Guardian',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.primary),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  'Guardian will receive an independent login to monitor your safety circle.',
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Guardian Full Name *',
                    prefixIcon: Icon(Icons.person_outline_rounded, color: AppColors.primary),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: relCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Relationship (Mother, Father, Sister...) *',
                    prefixIcon: Icon(Icons.family_restroom_rounded, color: AppColors.primary),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: phoneCtrl,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Mobile Phone *',
                    prefixIcon: Icon(Icons.phone_outlined, color: AppColors.primary),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email Address *',
                    prefixIcon: Icon(Icons.email_outlined, color: AppColors.primary),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: usernameCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Guardian Username (Optional - auto-generated if blank)',
                    prefixIcon: Icon(Icons.badge_outlined, color: AppColors.primary),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: passwordCtrl,
                  obscureText: obscurePassword,
                  decoration: InputDecoration(
                    labelText: 'Guardian Password (Optional - default generated)',
                    prefixIcon: const Icon(Icons.lock_outline_rounded, color: AppColors.primary),
                    suffixIcon: IconButton(
                      icon: Icon(obscurePassword ? Icons.visibility_off_rounded : Icons.visibility_rounded),
                      onPressed: () => setModalState(() => obscurePassword = !obscurePassword),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Allow Live Location Access', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  value: canLocation,
                  activeThumbColor: AppColors.primary,
                  onChanged: (val) => setModalState(() => canLocation = val),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Allow 24x7 Live Camera Access', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  subtitle: const Text('If off, camera is only accessible during active emergencies.', style: TextStyle(fontSize: 11)),
                  value: canCamera,
                  activeThumbColor: AppColors.primary,
                  onChanged: (val) => setModalState(() => canCamera = val),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Designate as Primary Guardian', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  value: isPrimary,
                  activeThumbColor: AppColors.secondary,
                  onChanged: (val) => setModalState(() => isPrimary = val),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: () async {
                      if (nameCtrl.text.isNotEmpty && phoneCtrl.text.isNotEmpty && emailCtrl.text.isNotEmpty) {
                        Navigator.pop(ctx);
                        try {
                          await _guardianRepository.addGuardian(
                            name: nameCtrl.text.trim(),
                            relationship: relCtrl.text.trim(),
                            phone: phoneCtrl.text.trim(),
                            email: emailCtrl.text.trim(),
                            username: usernameCtrl.text.trim().isNotEmpty ? usernameCtrl.text.trim() : null,
                            password: passwordCtrl.text.isNotEmpty ? passwordCtrl.text : null,
                            canViewLocation: canLocation,
                            canViewCamera: canCamera,
                            isPrimary: isPrimary,
                          );
                          if (!mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Guardian account linked successfully! Guardian can log in independently.'),
                              backgroundColor: AppColors.success,
                            ),
                          );
                          _loadGuardians();
                        } catch (e) {
                          if (!mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Could not link guardian: $e'),
                              backgroundColor: AppColors.emergency,
                            ),
                          );
                        }
                      }
                    },
                    child: const Text('Link Guardian Account'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('My Trusted Guardians'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_add_rounded),
            onPressed: _showAddGuardianDialog,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : (_guardians.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.family_restroom_rounded, size: 54, color: AppColors.textMuted),
                        const SizedBox(height: 12),
                        const Text(
                          'No Guardians Linked Yet',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Add your mother, father, sister, or close confidants to your safety circle.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 18),
                        ElevatedButton.icon(
                          icon: const Icon(Icons.add_rounded),
                          label: const Text('Add Guardian'),
                          onPressed: _showAddGuardianDialog,
                        ),
                      ],
                    ),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _guardians.length,
                  itemBuilder: (context, index) {
                    final g = _guardians[index];
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.borderLight),
                      ),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                                child: const Icon(Icons.person_rounded, color: AppColors.primary),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Text(g.name, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
                                        if (g.isPrimary)
                                          Container(
                                            margin: const EdgeInsets.only(left: 6),
                                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: AppColors.secondary.withValues(alpha: 0.2),
                                              borderRadius: BorderRadius.circular(4),
                                            ),
                                            child: const Text('PRIMARY',
                                                style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF92400E))),
                                          ),
                                      ],
                                    ),
                                    Text('${g.relationship} • ${g.phone}',
                                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                                  ],
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete_outline_rounded, color: AppColors.emergency),
                                onPressed: () async {
                                  await _guardianRepository.removeGuardian(g.id);
                                  _loadGuardians();
                                },
                              ),
                            ],
                          ),
                          const Divider(height: 18, color: AppColors.divider),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    g.canViewLocation ? Icons.location_on_rounded : Icons.location_off_rounded,
                                    size: 16,
                                    color: g.canViewLocation ? AppColors.success : AppColors.textMuted,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    g.canViewLocation ? 'Live GPS: Allowed' : 'GPS: Emergency only',
                                    style: TextStyle(fontSize: 11, color: g.canViewLocation ? AppColors.success : AppColors.textMuted),
                                  ),
                                ],
                              ),
                              Row(
                                children: [
                                  Icon(
                                    g.canViewCamera ? Icons.videocam_rounded : Icons.videocam_off_rounded,
                                    size: 16,
                                    color: g.canViewCamera ? AppColors.primary : AppColors.textMuted,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    g.canViewCamera ? 'Camera: 24x7 Live' : 'Camera: Emergency only',
                                    style: TextStyle(fontSize: 11, color: g.canViewCamera ? AppColors.primary : AppColors.textMuted),
                                  ),
                                ],
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
