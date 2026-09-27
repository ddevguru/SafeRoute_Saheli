import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'blocs/auth_bloc.dart';
import 'blocs/emergency_bloc.dart';
import 'config/app_config.dart';
import 'repositories/auth_repository.dart';
import 'repositories/emergency_repository.dart';
import 'repositories/guardian_repository.dart';
import 'routes/app_routes.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SafeRouteSaheliApp());
}

class SafeRouteSaheliApp extends StatelessWidget {
  const SafeRouteSaheliApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<AuthRepository>(create: (_) => AuthRepository()),
        RepositoryProvider<EmergencyRepository>(create: (_) => EmergencyRepository()),
        RepositoryProvider<GuardianRepository>(create: (_) => GuardianRepository()),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<AuthBloc>(
            create: (context) => AuthBloc(
              authRepository: context.read<AuthRepository>(),
              guardianRepository: context.read<GuardianRepository>(),
            ),
          ),
          BlocProvider<EmergencyBloc>(
            create: (context) => EmergencyBloc(
              emergencyRepository: context.read<EmergencyRepository>(),
            ),
          ),
        ],
        child: MaterialApp(
          title: AppConfig.appName,
          debugShowCheckedModeBanner: false,
          theme: AppTheme.lightTheme,
          initialRoute: AppRoutes.splash,
          routes: AppRoutes.routes,
        ),
      ),
    );
  }
}
