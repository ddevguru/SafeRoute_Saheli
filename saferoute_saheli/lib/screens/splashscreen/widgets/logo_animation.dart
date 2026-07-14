import 'dart:math';
import 'package:flutter/material.dart';

class LogoAnimation extends StatefulWidget {
  const LogoAnimation({super.key});

  @override
  State<LogoAnimation> createState() => _LogoAnimationState();
}

class _LogoAnimationState extends State<LogoAnimation>
    with TickerProviderStateMixin {
  late AnimationController floatController;
  late AnimationController rotateController;
  late AnimationController glowController;

  @override
  void initState() {
    super.initState();

    floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 5),
    )..repeat(reverse: true);

    rotateController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 18),
    )..repeat();

    glowController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    floatController.dispose();
    rotateController.dispose();
    glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screen = MediaQuery.of(context).size;

    final logoSize = screen.width * .43;

    return AnimatedBuilder(
      animation: Listenable.merge([
        floatController,
        rotateController,
        glowController,
      ]),
      builder: (_, __) {
        final float =
            sin(floatController.value * pi * 2) * 8;

        final glow =
            25 + glowController.value * 30;

        final angle =
            rotateController.value * 2 * pi;

        return Transform.translate(
          offset: Offset(0, float),
          child: SizedBox(
            width: logoSize + 80,
            height: logoSize + 80,
            child: Stack(
              alignment: Alignment.center,
              children: [

                /// OUTER BLUE GLOW
                Container(
                  width: logoSize + glow,
                  height: logoSize + glow,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [

                      BoxShadow(
                        color: Colors.blueAccent
                            .withOpacity(.30),
                        blurRadius: 80,
                        spreadRadius: 10,
                      ),

                      BoxShadow(
                        color: Colors.purpleAccent
                            .withOpacity(.20),
                        blurRadius: 120,
                        spreadRadius: 25,
                      ),
                    ],
                  ),
                ),

                /// GOLD RING
                Transform.rotate(
                  angle: angle,
                  child: Container(
                    width: logoSize + 35,
                    height: logoSize + 35,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: const Color(0xffD4AF37)
                            .withOpacity(.35),
                        width: 2,
                      ),
                    ),
                  ),
                ),

                /// BLUE RING
                Transform.rotate(
                  angle: -angle * .8,
                  child: Container(
                    width: logoSize + 20,
                    height: logoSize + 20,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Colors.cyanAccent
                            .withOpacity(.25),
                        width: 1.5,
                      ),
                    ),
                  ),
                ),

                /// LIGHT BURST
                Container(
                  width: logoSize + 10,
                  height: logoSize + 10,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [

                        Colors.white.withOpacity(.25),

                        Colors.blueAccent
                            .withOpacity(.15),

                        Colors.transparent,

                      ],
                    ),
                  ),
                ),

                /// LOGO
                Hero(
                  tag: "appLogo",
                  child: Image.asset(
                    "assets/logo/logo.png",
                    width: logoSize,
                    fit: BoxFit.contain,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}