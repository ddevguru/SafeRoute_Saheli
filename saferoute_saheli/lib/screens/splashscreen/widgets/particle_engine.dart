import 'dart:math';
import 'package:flutter/material.dart';

class Particle {
  double x;
  double y;
  double radius;
  double speed;
  double opacity;
  double depth;
  double drift;

  Particle({
    required this.x,
    required this.y,
    required this.radius,
    required this.speed,
    required this.opacity,
    required this.depth,
    required this.drift,
  });
}

class ParticleEngine extends StatefulWidget {
  const ParticleEngine({super.key});

  @override
  State<ParticleEngine> createState() => _ParticleEngineState();
}

class _ParticleEngineState extends State<ParticleEngine>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;

  final Random random = Random();

  final List<Particle> particles = [];

  static const int particleCount = 280;

  @override
  void initState() {
    super.initState();

    controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 100),
    )
      ..addListener(updateParticles)
      ..repeat();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final size = MediaQuery.of(context).size;

      for (int i = 0; i < particleCount; i++) {
        particles.add(
          Particle(
            x: random.nextDouble() * size.width,
            y: random.nextDouble() * size.height,
            radius: random.nextDouble() * 2.8 + .4,
            speed: random.nextDouble() * .8 + .2,
            opacity: random.nextDouble() * .8 + .15,
            depth: random.nextDouble(),
            drift: random.nextDouble() * .5 - .25,
          ),
        );
      }

      setState(() {});
    });
  }

  void updateParticles() {
    if (!mounted) return;

    final size = MediaQuery.of(context).size;

    for (var p in particles) {
      p.y -= p.speed;

      p.x += sin(controller.value * pi * 2 + p.depth * 10) * p.drift;

      if (p.y < -10) {
        p.y = size.height + random.nextDouble() * 40;
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
    return CustomPaint(
      size: Size.infinite,
      painter: ParticlePainter(
        particles,
        controller.value,
      ),
    );
  }
}

class ParticlePainter extends CustomPainter {
  final List<Particle> particles;
  final double animation;

  ParticlePainter(this.particles, this.animation);

  @override
  void paint(Canvas canvas, Size size) {
    for (var p in particles) {
      final glow = Paint()
        ..color = Colors.white.withOpacity(p.opacity * .25)
        ..maskFilter = const MaskFilter.blur(
          BlurStyle.normal,
          18,
        );

      canvas.drawCircle(
        Offset(p.x, p.y),
        p.radius * 3,
        glow,
      );

      final paint = Paint()
        ..color = Colors.white.withOpacity(
          p.opacity *
              (.65 +
                  .35 *
                      sin(animation * pi * 12 + p.depth * 20)),
        );

      canvas.drawCircle(
        Offset(p.x, p.y),
        p.radius,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}