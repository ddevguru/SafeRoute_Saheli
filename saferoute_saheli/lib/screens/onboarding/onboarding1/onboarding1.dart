import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:saferoute_saheli/screens/onboarding/onboarding1/bloc/onboarding1_bloc.dart';
import 'package:saferoute_saheli/screens/onboarding/onboarding1/widgets/next_button.dart';

class Onboarding1Screen extends StatelessWidget {
  const Onboarding1Screen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<Onboarding1Bloc, Onboarding1State>(
      listener: (context, state) {
        if (state is NavigateToNext) {
          // Navigate to next onboarding screen or login
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
                        "assets/images/onboard1.png",
                        fit: BoxFit.contain,
                      ),
                    ),
                  ),
                  Align(
                    alignment: Alignment.bottomRight,
                    child: NextButton(
                      onPressed: () {
                        context.read<Onboarding1Bloc>().add(
                              NextPressed(),
                            );
                      },
                    ),
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
