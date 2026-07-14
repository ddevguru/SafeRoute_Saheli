import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'bloc/onboarding/onboarding_bloc.dart';
import 'screens/onboarding_screen.dart';

void main() {
  runApp(

    BlocProvider(
      create: (_) => OnboardingBloc(),
      child: const MyApp(),
    ),

  );
}

class MyApp extends StatelessWidget {

  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: OnboardingScreen(),
    );

  }

}