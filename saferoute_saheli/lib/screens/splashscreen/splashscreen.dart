import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:saferoute_saheli/screens/splashscreen/bloc/splash_bloc.dart';
import 'package:saferoute_saheli/screens/splashscreen/bloc/splash_event.dart';
import 'package:saferoute_saheli/screens/splashscreen/bloc/splash_state.dart';
import 'package:saferoute_saheli/screens/splashscreen/widgets/animated_background.dart';
import 'package:saferoute_saheli/screens/splashscreen/widgets/logo_animation.dart';
import 'package:saferoute_saheli/screens/splashscreen/widgets/luxury_card.dart';



class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController textController;

  @override
  void initState() {
    super.initState();

    textController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    )..forward();

    context.read<SplashBloc>().add(
          SplashStarted(),
        );
  }

  @override
  void dispose() {
    textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<SplashBloc, SplashState>(
      listener: (context, state) {
        if (state is SplashCompleted) {
          // Navigator.pushReplacement(
          //   context,
          //   MaterialPageRoute(
          //     builder: (_) => const LoginScreen(),
          //   ),
          // );
        }
      },
      child: Scaffold(
        body: Stack(
          children: [
            /// Animated Background
            const AnimatedBackground(),

            /// Center Card with Responsive Width
            Center(
              child: Padding(
                padding: EdgeInsets.symmetric(
                  horizontal: MediaQuery.of(context).size.width > 600 ? 40 : 20,
                ),
                child: LuxuryCard(
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      /// Luxury Frame - Full Background
                      Positioned.fill(
                        child: Image.asset(
                          "assets/frames/luxury_frame.png",
                          fit: BoxFit.cover,
                        ),
                      ),

                      /// Content Stack - Centered in Frame
                      Positioned.fill(
                        child: Padding(
                          padding: EdgeInsets.symmetric(
                            horizontal: MediaQuery.of(context).size.width * 0.08,
                            vertical: MediaQuery.of(context).size.width * 0.06,
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              /// APP NAME - SAFE ROUTE (Gold) - 3D Effect
                              Transform.translate(
                                offset: Offset(MediaQuery.of(context).size.width * 0.12, MediaQuery.of(context).size.width * 0.05),
                                child: FadeTransition(
                                  opacity: CurvedAnimation(
                                    parent: textController,
                                    curve: Curves.easeIn,
                                  ),
                                  child: Stack(
                                    alignment: Alignment.center,
                                    children: [
                                      // Back layer - darkest
                                      Transform.translate(
                                        offset: const Offset(0, 8),
                                        child: Text(
                                          "SAFE ROUTE",
                                          style: TextStyle(
                                            color: Colors.black.withValues(alpha: 0.7),
                                            fontSize: MediaQuery.of(context).size.width * 0.09,
                                            fontWeight: FontWeight.w900,
                                            letterSpacing: 2,
                                          ),
                                        ),
                                      ),
                                      // Mid layer 1
                                      Transform.translate(
                                        offset: const Offset(0, 6),
                                        child: Text(
                                          "SAFE ROUTE",
                                          style: TextStyle(
                                            color: Colors.black.withValues(alpha: 0.6),
                                            fontSize: MediaQuery.of(context).size.width * 0.09,
                                            fontWeight: FontWeight.w900,
                                            letterSpacing: 2,
                                          ),
                                        ),
                                      ),
                                      // Mid layer 2
                                      Transform.translate(
                                        offset: const Offset(0, 4),
                                        child: Text(
                                          "SAFE ROUTE",
                                          style: TextStyle(
                                            color: Colors.black.withValues(alpha: 0.5),
                                            fontSize: MediaQuery.of(context).size.width * 0.09,
                                            fontWeight: FontWeight.w900,
                                            letterSpacing: 2,
                                          ),
                                        ),
                                      ),
                                      // Mid layer 3
                                      Transform.translate(
                                        offset: const Offset(0, 2),
                                        child: Text(
                                          "SAFE ROUTE",
                                          style: TextStyle(
                                            color: Colors.black.withValues(alpha: 0.3),
                                            fontSize: MediaQuery.of(context).size.width * 0.09,
                                            fontWeight: FontWeight.w900,
                                            letterSpacing: 2,
                                          ),
                                        ),
                                      ),
                                      // Front layer - main golden text
                                      Text(
                                        "SAFE ROUTE",
                                        style: TextStyle(
                                          color: const Color(0xFFD4AF37),
                                          fontSize: MediaQuery.of(context).size.width * 0.09,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2,
                                          shadows: [
                                            Shadow(
                                              offset: const Offset(0, 0),
                                              blurRadius: 20,
                                              color: const Color(0xFFD4AF37).withValues(alpha: 0.8),
                                            ),
                                            Shadow(
                                              offset: const Offset(0, -2),
                                              blurRadius: 10,
                                              color: Colors.white.withValues(alpha: 0.3),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),

                              /// Reduced Gap between SAFE ROUTE and SAHELI
                              const SizedBox(height: 4),

                              /// APP NAME - SAHELI (Purple) - 3D Effect
                              FadeTransition(
                                opacity: CurvedAnimation(
                                  parent: textController,
                                  curve: const Interval(0.1, 1, curve: Curves.easeIn),
                                ),
                                child: Stack(
                                  alignment: Alignment.center,
                                  children: [
                                    // Back layer - darkest
                                    Transform.translate(
                                      offset: const Offset(0, 10),
                                      child: Text(
                                        "SAHELI",
                                        style: TextStyle(
                                          color: Colors.black.withValues(alpha: 0.8),
                                          fontSize: MediaQuery.of(context).size.width * 0.11,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2.5,
                                        ),
                                      ),
                                    ),
                                    // Mid layer 1
                                    Transform.translate(
                                      offset: const Offset(0, 8),
                                      child: Text(
                                        "SAHELI",
                                        style: TextStyle(
                                          color: Colors.black.withValues(alpha: 0.7),
                                          fontSize: MediaQuery.of(context).size.width * 0.11,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2.5,
                                        ),
                                      ),
                                    ),
                                    // Mid layer 2
                                    Transform.translate(
                                      offset: const Offset(0, 6),
                                      child: Text(
                                        "SAHELI",
                                        style: TextStyle(
                                          color: Colors.black.withValues(alpha: 0.6),
                                          fontSize: MediaQuery.of(context).size.width * 0.11,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2.5,
                                        ),
                                      ),
                                    ),
                                    // Mid layer 3
                                    Transform.translate(
                                      offset: const Offset(0, 4),
                                      child: Text(
                                        "SAHELI",
                                        style: TextStyle(
                                          color: Colors.black.withValues(alpha: 0.4),
                                          fontSize: MediaQuery.of(context).size.width * 0.11,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2.5,
                                        ),
                                      ),
                                    ),
                                    // Mid layer 4
                                    Transform.translate(
                                      offset: const Offset(0, 2),
                                      child: Text(
                                        "SAHELI",
                                        style: TextStyle(
                                          color: Colors.black.withValues(alpha: 0.2),
                                          fontSize: MediaQuery.of(context).size.width * 0.11,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2.5,
                                        ),
                                      ),
                                    ),
                                    // Front layer - main purple text
                                    Text(
                                      "SAHELI",
                                      style: TextStyle(
                                        color: const Color(0xFFB8A8FF),
                                        fontSize: MediaQuery.of(context).size.width * 0.11,
                                        fontWeight: FontWeight.w900,
                                        letterSpacing: 2.5,
                                        shadows: [
                                          Shadow(
                                            offset: const Offset(0, 0),
                                            blurRadius: 25,
                                            color: const Color(0xFFB8A8FF).withValues(alpha: 1.0),
                                          ),
                                          Shadow(
                                            offset: const Offset(0, -3),
                                            blurRadius: 15,
                                            color: Colors.white.withValues(alpha: 0.4),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              /// Tagline with decorative dividers
                              SizedBox(height: MediaQuery.of(context).size.width * 0.06),

                              FadeTransition(
                                opacity: CurvedAnimation(
                                  parent: textController,
                                  curve: const Interval(
                                    .3,
                                    1,
                                    curve: Curves.easeIn,
                                  ),
                                ),
                                child: Column(
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        Container(
                                          width: 20,
                                          height: 1,
                                          color: const Color(0xFFD4AF37).withValues(alpha: 0.6),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          "◆",
                                          style: TextStyle(
                                            color: const Color(0xFFD4AF37),
                                            fontSize: 12,
                                            shadows: [
                                              Shadow(
                                                blurRadius: 8,
                                                color: const Color(0xFFD4AF37).withValues(alpha: 0.5),
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Container(
                                          width: 20,
                                          height: 1,
                                          color: const Color(0xFFD4AF37).withValues(alpha: 0.6),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                    Stack(
                                      alignment: Alignment.center,
                                      children: [
                                        Text(
                                          "SAFETY. TRUST. RESPONSE.",
                                          style: TextStyle(
                                            color: Colors.black.withValues(alpha: 0.3),
                                            fontSize: MediaQuery.of(context).size.width * 0.032,
                                            letterSpacing: 1.8,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        Text(
                                          "SAFETY. TRUST. RESPONSE.",
                                          style: TextStyle(
                                            color: const Color(0xFFD4AF37),
                                            fontSize: MediaQuery.of(context).size.width * 0.032,
                                            letterSpacing: 1.8,
                                            fontWeight: FontWeight.w600,
                                            shadows: [
                                              Shadow(
                                                offset: const Offset(1, 1),
                                                blurRadius: 4,
                                                color: Colors.black.withValues(alpha: 0.4),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),

                              /// LOGO - Inside Frame
                              SizedBox(height: MediaQuery.of(context).size.width * 0.08),

                              FadeTransition(
                                opacity: CurvedAnimation(
                                  parent: textController,
                                  curve: const Interval(
                                    .2,
                                    1,
                                    curve: Curves.easeIn,
                                  ),
                                ),
                                child: SizedBox(
                                  width: MediaQuery.of(context).size.width * 0.18,
                                  height: MediaQuery.of(context).size.width * 0.18,
                                  child: const LogoAnimation(),
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

            /// Version
            Positioned(
              bottom: 30,
              left: 0,
              right: 0,
              child: Text(
                "Version 1.0.0",
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white.withOpacity(.35),
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}