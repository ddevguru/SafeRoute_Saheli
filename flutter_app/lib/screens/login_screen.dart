import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/auth_bloc.dart';
import '../constants/app_colors.dart';
import '../routes/app_routes.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _saheliFormKey = GlobalKey<FormState>();
  final _guardianFormKey = GlobalKey<FormState>();

  final _saheliIdentifierController = TextEditingController();
  final _saheliPasswordController = TextEditingController();

  final _guardianIdentifierController = TextEditingController();
  final _guardianPasswordController = TextEditingController();

  bool _obscurePassword = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _saheliIdentifierController.dispose();
    _saheliPasswordController.dispose();
    _guardianIdentifierController.dispose();
    _guardianPasswordController.dispose();
    super.dispose();
  }

  void _onSaheliLogin() {
    if (_saheliFormKey.currentState?.validate() ?? false) {
      context.read<AuthBloc>().add(
            LoginEvent(
              identifier: _saheliIdentifierController.text.trim(),
              password: _saheliPasswordController.text,
            ),
          );
    }
  }

  void _onGuardianLogin() {
    if (_guardianFormKey.currentState?.validate() ?? false) {
      context.read<AuthBloc>().add(
            GuardianLoginEvent(
              identifier: _guardianIdentifierController.text.trim(),
              password: _guardianPasswordController.text,
            ),
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: BlocConsumer<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthenticatedState) {
            if (state.role == 'GUARDIAN') {
              Navigator.pushReplacementNamed(context, AppRoutes.guardianDashboard);
            } else {
              Navigator.pushReplacementNamed(context, AppRoutes.home);
            }
          } else if (state is AuthErrorState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: AppColors.emergency,
              ),
            );
          }
        },
        builder: (context, state) {
          final isLoading = state is AuthLoading;

          return SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 16),
                  // App Emblem
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.shield_rounded, color: AppColors.secondary, size: 28),
                      ),
                      const SizedBox(width: 12),
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'SafeRoute Saheli',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w700,
                              color: AppColors.primary,
                            ),
                          ),
                          Text(
                            'Welcome back, please sign in',
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Role Tab Selector
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.borderLight),
                    ),
                    child: TabBar(
                      controller: _tabController,
                      indicator: BoxDecoration(
                        color: AppColors.primary,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      labelColor: AppColors.white,
                      unselectedLabelColor: AppColors.textSecondary,
                      labelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                      tabs: const [
                        Tab(text: 'Saheli Sign In'),
                        Tab(text: 'Guardian Sign In'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 28),

                  // Tab Views
                  SizedBox(
                    height: 420,
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        // Saheli Form
                        _buildSaheliForm(isLoading),
                        // Guardian Form
                        _buildGuardianForm(isLoading),
                      ],
                    ),
                  ),

                  // Switch to Sign Up
                  Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Don't have a Saheli account? ",
                          style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
                        ),
                        GestureDetector(
                          onTap: () {
                            Navigator.pushNamed(context, AppRoutes.register);
                          },
                          child: const Text(
                            'Sign Up',
                            style: TextStyle(
                              color: AppColors.primary,
                              fontWeight: FontWeight.w700,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSaheliForm(bool isLoading) {
    return Form(
      key: _saheliFormKey,
      child: Column(
        children: [
          TextFormField(
            controller: _saheliIdentifierController,
            decoration: const InputDecoration(
              labelText: 'Email or Phone Number',
              prefixIcon: Icon(Icons.person_outline_rounded, color: AppColors.primary),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Please enter email or phone' : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _saheliPasswordController,
            obscureText: _obscurePassword,
            decoration: InputDecoration(
              labelText: 'Password',
              prefixIcon: const Icon(Icons.lock_outline_rounded, color: AppColors.primary),
              suffixIcon: IconButton(
                icon: Icon(_obscurePassword ? Icons.visibility_off_rounded : Icons.visibility_rounded),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              ),
            ),
            validator: (val) => (val == null || val.length < 6) ? 'Password is required' : null,
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: () => Navigator.pushNamed(context, AppRoutes.forgotPassword),
              child: const Text(
                'Forgot Password?',
                style: TextStyle(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
            ),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: isLoading ? null : _onSaheliLogin,
              child: isLoading
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(color: AppColors.white, strokeWidth: 2),
                    )
                  : const Text('Sign In as Saheli'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGuardianForm(bool isLoading) {
    return Form(
      key: _guardianFormKey,
      child: Column(
        children: [
          TextFormField(
            controller: _guardianIdentifierController,
            decoration: const InputDecoration(
              labelText: 'Guardian Username / Email',
              prefixIcon: Icon(Icons.family_restroom_rounded, color: AppColors.primary),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Please enter username or email' : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _guardianPasswordController,
            obscureText: _obscurePassword,
            decoration: InputDecoration(
              labelText: 'Guardian Password',
              prefixIcon: const Icon(Icons.lock_outline_rounded, color: AppColors.primary),
              suffixIcon: IconButton(
                icon: Icon(_obscurePassword ? Icons.visibility_off_rounded : Icons.visibility_rounded),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              ),
            ),
            validator: (val) => (val == null || val.isEmpty) ? 'Password is required' : null,
          ),
          const SizedBox(height: 28),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: isLoading ? null : _onGuardianLogin,
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.secondary),
              child: isLoading
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2),
                    )
                  : const Text('Sign In as Guardian', style: TextStyle(color: AppColors.primary)),
            ),
          ),
        ],
      ),
    );
  }
}
