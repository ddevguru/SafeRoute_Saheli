import 'dart:math';

import 'package:flutter/material.dart';

import 'nebula.dart';
import 'particle_engine.dart';
import 'star_engine.dart';

class AnimatedBackground extends StatefulWidget {
  const AnimatedBackground({super.key});

  @override
  State<AnimatedBackground> createState() =>
      _AnimatedBackgroundState();
}

class _AnimatedBackgroundState
    extends State<AnimatedBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;

  @override
  void initState() {
    super.initState();

    controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 20),
    )..repeat();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (_, __) {
        final t = controller.value * 2 * pi;

        return Stack(
          children: [

            /// BACKGROUND
            Container(
              decoration: const BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment(0, -0.25),
                  radius: 1.5,
                  colors: [
                    Color(0xff22124A),
                    Color(0xff101938),
                    Color(0xff080C18),
                    Color(0xff02040A),
                  ],
                ),
              ),
            ),

            /// BLUE GLOW
            Positioned(
              left: -130 + sin(t) * 20,
              top: 90,
              child: _orb(
                320,
                const Color(0xff4FC3F7).withOpacity(.18),
              ),
            ),

            /// PURPLE GLOW
            Positioned(
              right: -140 + cos(t) * 25,
              top: 170,
              child: _orb(
                340,
                const Color(0xff7E57C2).withOpacity(.18),
              ),
            ),

            /// BOTTOM BLUE
            Positioned(
              left: 60,
              bottom: -120,
              child: _orb(
                380,
                const Color(0xff42A5F5).withOpacity(.10),
              ),
            ),

            /// GOLD DUST GLOW
            Positioned(
              right: -100,
              bottom: -40,
              child: _orb(
                260,
                const Color(0xffFFD54F).withOpacity(.06),
              ),
            ),

            /// NEBULA
            const NebulaBackground(),

            /// STARS
            const StarEngine(),

            /// PARTICLES
            const ParticleEngine(),

            /// TOP LIGHT
            Align(
              alignment: Alignment.topCenter,
              child: IgnorePointer(
                child: Container(
                  height: 180,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.white.withOpacity(.08),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),

            /// BOTTOM LIGHT
            Align(
              alignment: Alignment.bottomCenter,
              child: IgnorePointer(
                child: Container(
                  height: 150,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      colors: [
                        Colors.white.withOpacity(.03),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _orb(double size, Color color) {
    return IgnorePointer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              color,
              color.withOpacity(.35),
              Colors.transparent,
            ],
          ),
        ),
      ),
    );
  }
}