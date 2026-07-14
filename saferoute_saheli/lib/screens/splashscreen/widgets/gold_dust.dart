import 'dart:math';

import 'package:flutter/material.dart';

class GoldDust extends StatefulWidget {
  const GoldDust({super.key});

  @override
  State<GoldDust> createState() => _GoldDustState();
}

class _GoldDustState extends State<GoldDust>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;

  final Random random = Random();

  final List<GoldParticle> particles = [];

  static const int particleCount = 220;

  @override
  void initState() {
    super.initState();

    controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 25),
    )
      ..addListener(update)
      ..repeat();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final size = MediaQuery.of(context).size;

      for (int i = 0; i < particleCount; i++) {
        particles.add(
          GoldParticle(
            x: random.nextDouble() * size.width,
            y: random.nextDouble() * size.height,
            radius: random.nextDouble() * 2.4 + .4,
            speed: random.nextDouble() * .6 + .2,
            opacity: random.nextDouble() * .6 + .4,
            phase: random.nextDouble() * pi * 2,
          ),
        );
      }

      setState(() {});
    });
  }

  void update() {
    if (!mounted) return;

    final size = MediaQuery.of(context).size;

    for (var p in particles) {
      p.y -= p.speed;

      p.x += sin(
            controller.value * pi * 2 + p.phase,
          ) *
          .25;

      if (p.y < -10) {
        p.y = size.height + 20;
        p.x = random.nextDouble() * size.width;
      }
    }

    setState(() {});
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        size: Size.infinite,
        painter: GoldDustPainter(
          particles,
          controller.value,
        ),
      ),
    );
  }
}

class GoldParticle {
  double x;
  double y;
  double radius;
  double speed;
  double opacity;
  double phase;

  GoldParticle({
    required this.x,
    required this.y,
    required this.radius,
    required this.speed,
    required this.opacity,
    required this.phase,
  });
}

class GoldDustPainter extends CustomPainter {
  final List<GoldParticle> particles;
  final double animation;

  GoldDustPainter(
    this.particles,
    this.animation,
  );

  @override
  void paint(Canvas canvas, Size size) {
    for (final p in particles) {
      final glow = Paint()
        ..color = const Color(0xffFFD54F).withOpacity(
          p.opacity * .25,
        )
        ..maskFilter = const MaskFilter.blur(
          BlurStyle.normal,
          16,
        );

      canvas.drawCircle(
        Offset(p.x, p.y),
        p.radius * 3.5,
        glow,
      );

      final brightness =
          (.55 +
                  .45 *
                      sin(
                        animation * pi * 8 + p.phase,
                      )) *
              p.opacity;

      final paint = Paint()
        ..color = Color.lerp(
          const Color(0xffFFD54F),
          Colors.white,
          .3,
        )!
            .withOpacity(brightness);

      canvas.drawCircle(
        Offset(p.x, p.y),
        p.radius,
        paint,
      );

      if (p.radius > 1.5) {
        final sparkle = Paint()
          ..color = Colors.white.withOpacity(
            brightness,
          )
          ..strokeWidth = .4;

        canvas.drawLine(
          Offset(p.x - 3, p.y),
          Offset(p.x + 3, p.y),
          sparkle,
        );

        canvas.drawLine(
          Offset(p.x, p.y - 3),
          Offset(p.x, p.y + 3),
          sparkle,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}