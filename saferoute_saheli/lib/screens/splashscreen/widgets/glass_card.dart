import 'dart:math';
import 'dart:ui';

import 'package:flutter/material.dart';

class GlassCard extends StatefulWidget {
  final String imagePath;

  const GlassCard({
    super.key,
    required this.imagePath,
  });

  @override
  State<GlassCard> createState() => _GlassCardState();
}

class _GlassCardState extends State<GlassCard>
    with TickerProviderStateMixin {
  late AnimationController floatController;
  late AnimationController shineController;

  @override
  void initState() {
    super.initState();

    floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 6),
    )..repeat(reverse: true);

    shineController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();
  }

  @override
  void dispose() {
    floatController.dispose();
    shineController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        floatController,
        shineController,
      ]),
      builder: (context, child) {
        final t = floatController.value;
        final shine = shineController.value;

        return Transform(
          alignment: Alignment.center,
          transform: Matrix4.identity()
            ..setEntry(3, 2, 0.001)
            ..rotateX(sin(t * pi) * 0.03)
            ..rotateY(cos(t * pi) * 0.03),
          child: Transform.translate(
            offset: Offset(
              0,
              sin(t * pi * 2) * -8,
            ),
            child: SizedBox(
              width: 310,
              height: 560,
              child: Stack(
                children: [
                  // OUTER GLOW
                  Positioned.fill(
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(38),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xff5A7CFF)
                                .withOpacity(.35),
                            blurRadius: 60,
                            spreadRadius: 5,
                          ),
                          BoxShadow(
                            color: Colors.cyan.withOpacity(.18),
                            blurRadius: 120,
                            spreadRadius: 15,
                          ),
                        ],
                      ),
                    ),
                  ),

                  // GLASS
                  ClipRRect(
                    borderRadius: BorderRadius.circular(36),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(
                        sigmaX: 12,
                        sigmaY: 12,
                      ),
                      child: Container(
                        decoration: BoxDecoration(
                          borderRadius:
                              BorderRadius.circular(36),
                          color:
                              Colors.white.withOpacity(.06),
                          border: Border.all(
                            color: Colors.white24,
                            width: 1.2,
                          ),
                        ),
                      ),
                    ),
                  ),

                  // IMAGE
                  ClipRRect(
                    borderRadius: BorderRadius.circular(36),
                    child: Image.asset(
                      widget.imagePath,
                      width: 310,
                      height: 560,
                      fit: BoxFit.cover,
                    ),
                  ),

                  // TOP LIGHT
                  Positioned(
                    top: -120,
                    left: -80,
                    child: Transform.rotate(
                      angle: -.5,
                      child: Container(
                        width: 200,
                        height: 450,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              Colors.white.withOpacity(.18),
                              Colors.transparent,
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),

                  // MOVING SHINE
                  Positioned.fill(
                    child: IgnorePointer(
                      child: ClipRRect(
                        borderRadius:
                            BorderRadius.circular(36),
                        child: Stack(
                          children: [
                            Transform.translate(
                              offset: Offset(
                                (shine * 600) - 300,
                                0,
                              ),
                              child: Transform.rotate(
                                angle: -.35,
                                child: Container(
                                  width: 70,
                                  decoration:
                                      BoxDecoration(
                                    gradient:
                                        LinearGradient(
                                      colors: [
                                        Colors
                                            .transparent,
                                        Colors.white
                                            .withOpacity(
                                                .25),
                                        Colors
                                            .transparent,
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  // INNER BORDER
                  Positioned.fill(
                    child: Padding(
                      padding:
                          const EdgeInsets.all(6),
                      child: IgnorePointer(
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius:
                                BorderRadius.circular(
                                    30),
                            border: Border.all(
                              color: Colors.white
                                  .withOpacity(.15),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}