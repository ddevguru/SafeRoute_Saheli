import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:saferoute_saheli/screens/splashscreen/bloc/splash_bloc.dart';
import 'package:saferoute_saheli/screens/splashscreen/splashscreen.dart';



class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (_) => SplashBloc(),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        home: const SplashScreen(),
      ),
    );
  }
}