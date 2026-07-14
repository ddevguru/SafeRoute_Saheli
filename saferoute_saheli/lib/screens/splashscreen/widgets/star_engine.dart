import 'dart:math';
import 'package:flutter/material.dart';

class Star {
  double x;
  double y;
  double radius;
  double speed;
  double phase;
  double opacity;
  Color color;

  Star({
    required this.x,
    required this.y,
    required this.radius,
    required this.speed,
    required this.phase,
    required this.opacity,
    required this.color,
  });
}

class StarEngine extends StatefulWidget {
  const StarEngine({super.key});

  @override
  State<StarEngine> createState() => _StarEngineState();
}

class _StarEngineState extends State<StarEngine>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;

  final Random random = Random();

  final List<Star> stars = [];

  static const int starCount = 180;

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

      for (int i = 0; i < starCount; i++) {
        stars.add(
          Star(
            x: random.nextDouble() * size.width,
            y: random.nextDouble() * size.height,
            radius: random.nextDouble() * 1.8 + .5,
            speed: random.nextDouble() * .25,
            phase: random.nextDouble() * pi * 2,
            opacity: random.nextDouble() * .6 + .4,
            color: [
              Colors.white,
              const Color(0xffDDEBFF),
              const Color(0xffFFF3B0),
              const Color(0xffCDB4FF),
            ][random.nextInt(4)],
          ),
        );
      }

      setState(() {});
    });
  }

  void update() {
    if (!mounted) return;

    final size = MediaQuery.of(context).size;

    for (var s in stars) {
      s.y += s.speed * .15;

      if (s.y > size.height + 5) {
        s.y = -5;
        s.x = random.nextDouble() * size.width;
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
        painter: StarPainter(
          stars,
          controller.value,
        ),
      ),
    );
  }
}

class StarPainter extends CustomPainter {
  final List<Star> stars;
  final double animation;

  StarPainter(this.stars, this.animation);

  @override
  void paint(Canvas canvas, Size size) {
    for (var star in stars) {
      final brightness = (.55 +
              .45 *
                  sin(
                    animation * pi * 8 + star.phase,
                  )) *
          star.opacity;

      final glowPaint = Paint()
        ..color = star.color.withOpacity(brightness * .20)
        ..maskFilter = const MaskFilter.blur(
          BlurStyle.normal,
          12,
        );

      canvas.drawCircle(
        Offset(star.x, star.y),
        star.radius * 4,
        glowPaint,
      );

      final paint = Paint()
        ..color = star.color.withOpacity(brightness);

      canvas.drawCircle(
        Offset(star.x, star.y),
        star.radius,
        paint,
      );

      if (star.radius > 1.2) {
        final linePaint = Paint()
          ..color = star.color.withOpacity(brightness * .6)
          ..strokeWidth = .5;

        canvas.drawLine(
          Offset(star.x - 4, star.y),
          Offset(star.x + 4, star.y),
          linePaint,
        );

        canvas.drawLine(
          Offset(star.x, star.y - 4),
          Offset(star.x, star.y + 4),
          linePaint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}