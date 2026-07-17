import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import 'splash_event.dart';
import 'splash_state.dart';

class SplashBloc extends Bloc<SplashEvent, SplashState> {
  SplashBloc() : super(SplashInitial()) {
    on<SplashStarted>(_onStarted);
  }

  Future<void> _onStarted(
      SplashStarted event,
      Emitter<SplashState> emit,
      ) async {

    emit(SplashLoading());

    await Future.delayed(const Duration(seconds: 5));

    emit(SplashCompleted());
  }
}