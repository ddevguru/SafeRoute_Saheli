import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/onboarding/onboarding_bloc.dart';
import '../bloc/onboarding/onboarding_event.dart';
import '../bloc/onboarding/onboarding_state.dart';

import 'onboarding_page1.dart';
import 'onboarding_page2.dart';
import 'onboarding_page3.dart';

class OnboardingScreen extends StatefulWidget {

  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() =>
      _OnboardingScreenState();

}

class _OnboardingScreenState
    extends State<OnboardingScreen> {

  final PageController controller = PageController();

  @override
  Widget build(BuildContext context) {

    return BlocListener<OnboardingBloc, OnboardingState>(

      listener: (context, state) {

        controller.animateToPage(
          state.currentPage,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );

      },

      child: Scaffold(

        body: Stack(

          children: [

            PageView(

              controller: controller,
              physics: NeverScrollableScrollPhysics(),

              children: const [

                OnboardingPage1(),
                OnboardingPage2(),
                OnboardingPage3(),

              ],

            ),

            Positioned(

              bottom: 50,
              right: 25,

              child: BlocBuilder<
                  OnboardingBloc,
                  OnboardingState>(

                builder: (context, state) {

                  return ElevatedButton(

                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 35,
                          vertical: 15),
                    ),

                    onPressed: () {

                      if (state.currentPage == 2) {

                        Navigator.pushReplacementNamed(
                            context,
                            "/login");

                      } else {

                        context
                            .read<OnboardingBloc>()
                            .add(NextPageEvent());

                      }

                    },

                    child: Text(
                      state.currentPage == 2
                          ? "Get Started"
                          : "Next",
                    ),

                  );

                },

              ),

            ),

          ],

        ),

      ),

    );

  }

}