import 'package:flutter/material.dart';

class OnboardingPage1 extends StatelessWidget {

  const OnboardingPage1({super.key});

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: Stack(

        fit: StackFit.expand,

        children: [

          Image.asset(
            "assets/images/onboard1.png",
            fit: BoxFit.cover,
          ),

        ],

      ),

    );

  }

}