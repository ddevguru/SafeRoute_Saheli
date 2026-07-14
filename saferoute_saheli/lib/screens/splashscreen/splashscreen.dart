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

            /// Center Card
            Center(
              child: LuxuryCard(
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    /// Luxury Frame
                    Positioned.fill(
                      child: Padding(
                        padding: EdgeInsets.all(
                          MediaQuery.of(context).size.width * 0.02,
                        ),
                        child: Image.asset(
                          "assets/frames/luxury_frame.png",
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),

                    /// LOGO
                    const Positioned(
                      top: 70,
                      child: LogoAnimation(),
                    ),

                    /// APP NAME
                    Positioned(
                      bottom: MediaQuery.of(context).size.height * 0.28,
                      left: 0,
                      right: 0,
                      child: FadeTransition(
                        opacity: CurvedAnimation(
                          parent: textController,
                          curve: Curves.easeIn,
                        ),
                        child: Transform(
                          alignment: Alignment.center,
                          transform: Matrix4.identity()
                            ..setEntry(3, 2, 0.001)
                            ..rotateX(0.02),
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              // Shadow layer for 3D effect
                              Text(
                                "SafeRoute Saheli",
                                style: TextStyle(
                                  color: Colors.black.withValues(alpha: 0.3),
                                  fontSize: MediaQuery.of(context).size.width * 0.08,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 1.5,
                                ),
                              ),
                              // Main text
                              Text(
                                "SafeRoute Saheli",
                                style: TextStyle(
                                  color: const Color(0xffE8D8BE),
                                  fontSize: MediaQuery.of(context).size.width * 0.08,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 1.5,
                                  shadows: [
                                    Shadow(
                                      offset: const Offset(2, 2),
                                      blurRadius: 8,
                                      color: Colors.black.withValues(alpha: 0.4),
                                    ),
                                    Shadow(
                                      offset: const Offset(-1, -1),
                                      blurRadius: 10,
                                      color: Colors.white.withValues(alpha: 0.2),
                                    ),
                                    Shadow(
                                      blurRadius: 25,
                                      color: Colors.white24,
                                    )
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),

                    /// TAGLINE
                    Positioned(
                      bottom: MediaQuery.of(context).size.height * 0.22,
                      left: 0,
                      right: 0,
                      child: FadeTransition(
                        opacity: CurvedAnimation(
                          parent: textController,
                          curve: const Interval(
                            .3,
                            1,
                            curve: Curves.easeIn,
                          ),
                        ),
                        child: Transform(
                          alignment: Alignment.center,
                          transform: Matrix4.identity()
                            ..setEntry(3, 2, 0.001)
                            ..rotateX(0.01),
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              // Shadow layer
                              Text(
                                "Safety. Trust. Response.",
                                style: TextStyle(
                                  color: Colors.black.withValues(alpha: 0.2),
                                  fontSize: MediaQuery.of(context).size.width * 0.04,
                                  letterSpacing: 1.5,
                                ),
                              ),
                              // Main text
                              Text(
                                "Safety. Trust. Response.",
                                style: TextStyle(
                                  color: Colors.white70,
                                  fontSize: MediaQuery.of(context).size.width * 0.04,
                                  letterSpacing: 1.5,
                                  shadows: [
                                    Shadow(
                                      offset: const Offset(1, 1),
                                      blurRadius: 4,
                                      color: Colors.black.withValues(alpha: 0.3),
                                    ),
                                  ],
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