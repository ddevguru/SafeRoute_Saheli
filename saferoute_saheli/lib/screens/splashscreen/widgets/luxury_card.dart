import 'dart:math';
import 'dart:ui';

import 'package:flutter/material.dart';

class LuxuryCard extends StatefulWidget {
  final Widget child;

  const LuxuryCard({
    super.key,
    required this.child,
  });

  @override
  State<LuxuryCard> createState() => _LuxuryCardState();
}

class _LuxuryCardState extends State<LuxuryCard>
    with TickerProviderStateMixin {
  late AnimationController floatController;
  late AnimationController shineController;

  @override
  void initState() {
    super.initState();

    floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 5),
    )..repeat(reverse: true);

    shineController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 6),
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
      builder: (_, __) {
        final floatY = sin(floatController.value * pi * 2) * 8;
        final shine = shineController.value;

        return Transform.translate(
          offset: Offset(0, floatY),
          child: SizedBox(
            width: 320,
            height: 560,
            child: Stack(
              alignment: Alignment.center,
              children: [

                /// BACK CARD
                Positioned(
                  top: 25,
                  child: Transform.rotate(
                    angle: -.05,
                    child: _glassLayer(
                      opacity: .04,
                    ),
                  ),
                ),

                /// MIDDLE CARD
                Positioned(
                  top: 12,
                  child: Transform.rotate(
                    angle: .03,
                    child: _glassLayer(
                      opacity: .06,
                    ),
                  ),
                ),

                /// MAIN CARD
                ClipRRect(
                  borderRadius: BorderRadius.circular(34),
                  child: BackdropFilter(
                    filter: ImageFilter.blur(
                      sigmaX: 14,
                      sigmaY: 14,
                    ),
                    child: Container(
                      width: 300,
                      height: 520,
                      decoration: BoxDecoration(
                        borderRadius:
                            BorderRadius.circular(34),
                        color: Colors.white.withOpacity(.08),
                        border: Border.all(
                          color: Colors.white24,
                          width: 1.4,
                        ),
                        boxShadow: [

                          BoxShadow(
                            color: Colors.white.withOpacity(.08),
                            blurRadius: 50,
                          ),

                          BoxShadow(
                            color: Colors.blue.withOpacity(.15),
                            blurRadius: 120,
                            spreadRadius: 10,
                          ),
                        ],
                      ),

                      child: Stack(
                        children: [

                          /// IMAGE / CONTENT
                          Positioned.fill(
                            child: widget.child,
                          ),

                          /// INNER BORDER
                          Positioned.fill(
                            child: Padding(
                              padding: const EdgeInsets.all(8),
                              child: Container(
                                decoration: BoxDecoration(
                                  borderRadius:
                                      BorderRadius.circular(26),
                                  border: Border.all(
                                    color: Colors.white10,
                                  ),
                                ),
                              ),
                            ),
                          ),

                          /// TOP LIGHT
                          Positioned(
                            left: -90,
                            top: -80,
                            child: Transform.rotate(
                              angle: -.45,
                              child: Container(
                                width: 140,
                                height: 500,
                                decoration: BoxDecoration(
                                  gradient:
                                      LinearGradient(
                                    colors: [

                                      Colors.white
                                          .withOpacity(.22),

                                      Colors.transparent,

                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),

                          /// MOVING SHINE
                          Positioned.fill(
                            child: ClipRRect(
                              borderRadius:
                                  BorderRadius.circular(34),
                              child: Stack(
                                children: [

                                  Transform.translate(
                                    offset: Offset(
                                      shine * 520 - 260,
                                      0,
                                    ),
                                    child: Transform.rotate(
                                      angle: -.35,
                                      child: Container(
                                        width: 60,
                                        decoration:
                                            BoxDecoration(
                                          gradient:
                                              LinearGradient(
                                            colors: [

                                              Colors
                                                  .transparent,

                                              Colors.white
                                                  .withOpacity(
                                                      .30),

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
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _glassLayer({
    required double opacity,
  }) {
    return Container(
      width: 300,
      height: 520,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(34),
        color: Colors.white.withOpacity(opacity),
        border: Border.all(
          color: Colors.white10,
        ),
      ),
    );
  }
}