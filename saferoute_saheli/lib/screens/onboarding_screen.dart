import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../blocs/onboarding/onboarding_bloc.dart';
import '../widgets/next_button.dart';
import 'login_screen.dart';

class OnboardingScreen extends StatelessWidget {

  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {

    return BlocConsumer<OnboardingBloc, OnboardingState>(

      listener: (context, state) {

        if (state is NavigateToLogin) {

          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (_) => const LoginScreen(),
            ),
          );

        }

      },

      builder: (context, state) {

        return Scaffold(

          backgroundColor: Colors.black,

          body: SafeArea(

            child: Padding(

              padding: const EdgeInsets.all(20),

              child: Column(

                children: [

                  Expanded(

                    child: Center(

                      child: Image.asset(
                        "assets/images/onboarding.png",
                        fit: BoxFit.contain,
                      ),

                    ),

                  ),

                  NextButton(

                    onPressed: () {

                      context.read<OnboardingBloc>().add(
                        NextPressed(),
                      );

                    },

                  ),

                  const SizedBox(height: 20),

                ],

              ),

            ),

          ),

        );

      },

    );

  }

}