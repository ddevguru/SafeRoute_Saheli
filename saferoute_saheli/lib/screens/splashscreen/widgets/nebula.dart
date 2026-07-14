import 'dart:math';
import 'dart:ui';

import 'package:flutter/material.dart';

class NebulaBackground extends StatefulWidget {
  const NebulaBackground({super.key});

  @override
  State<NebulaBackground> createState() => _NebulaBackgroundState();
}

class _NebulaBackgroundState extends State<NebulaBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;

  @override
  void initState() {
    super.initState();

    controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 25),
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
        return CustomPaint(
          size: Size.infinite,
          painter: NebulaPainter(controller.value),
        );
      },
    );
  }
}

class NebulaPainter extends CustomPainter {
  final double progress;

  NebulaPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final t = progress * 2 * pi;

    drawGlow(
      canvas,
      size,
      Offset(
        size.width * .28 + sin(t) * 30,
        size.height * .22 + cos(t) * 20,
      ),
      220,
      const Color(0xff5A6CFF).withOpacity(.18),
    );

    drawGlow(
      canvas,
      size,
      Offset(
        size.width * .78 + cos(t * .7) * 40,
        size.height * .30 + sin(t * .6) * 30,
      ),
      260,
      const Color(0xff865CFF).withOpacity(.18),
    );

    drawGlow(
      canvas,
      size,
      Offset(
        size.width * .50 + sin(t * .5) * 20,
        size.height * .72 + cos(t * .5) * 20,
      ),
      320,
      const Color(0xff4FC3F7).withOpacity(.15),
    );

    drawGlow(
      canvas,
      size,
      Offset(
        size.width * .15 + cos(t * .4) * 25,
        size.height * .80 + sin(t * .3) * 25,
      ),
      260,
      const Color(0xff7E57C2).withOpacity(.15),
    );

    drawGlow(
      canvas,
      size,
      Offset(
        size.width * .90 + sin(t * .9) * 20,
        size.height * .75 + cos(t * .8) * 15,
      ),
      220,
      Colors.white.withOpacity(.05),
    );
  }

  void drawGlow(
    Canvas canvas,
    Size size,
    Offset center,
    double radius,
    Color color,
  ) {
    final rect = Rect.fromCircle(
      center: center,
      radius: radius,
    );

    final paint = Paint()
      ..shader = RadialGradient(
        colors: [
          color,
          color.withOpacity(.4),
          Colors.transparent,
        ],
      ).createShader(rect)
      ..maskFilter = const MaskFilter.blur(
        BlurStyle.normal,
        80,
      );

    canvas.drawCircle(
      center,
      radius,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant NebulaPainter oldDelegate) => true;
}