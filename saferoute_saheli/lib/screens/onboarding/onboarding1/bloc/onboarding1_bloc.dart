import 'package:flutter_bloc/flutter_bloc.dart';

part 'onboarding1_event.dart';
part 'onboarding1_state.dart';

class Onboarding1Bloc extends Bloc<Onboarding1Event, Onboarding1State> {
  Onboarding1Bloc() : super(Onboarding1Initial()) {
    on<NextPressed>((event, emit) {
      emit(NavigateToNext());
    });
  }
}
