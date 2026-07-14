import 'package:flutter/material.dart';

class OnboardingPage2 extends StatelessWidget {

  const OnboardingPage2({super.key});

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: Center(

        child: Text(
          "Share your location\nonly when needed",
          textAlign: TextAlign.center,
          style: TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.bold),
        ),

      ),

    );

  }

}