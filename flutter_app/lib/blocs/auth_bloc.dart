import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../models/user_model.dart';
import '../models/guardian_model.dart';
import '../repositories/auth_repository.dart';
import '../repositories/guardian_repository.dart';
import '../storage/secure_storage_service.dart';

// Events
abstract class AuthEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class CheckAuthStatusEvent extends AuthEvent {}

class LoginEvent extends AuthEvent {
  final String identifier;
  final String password;
  LoginEvent({required this.identifier, required this.password});
  @override
  List<Object?> get props => [identifier, password];
}

class GuardianLoginEvent extends AuthEvent {
  final String identifier;
  final String password;
  GuardianLoginEvent({required this.identifier, required this.password});
  @override
  List<Object?> get props => [identifier, password];
}

class RegisterEvent extends AuthEvent {
  final String name;
  final String email;
  final String phone;
  final String password;
  final String? bloodGroup;
  final String? medicalNotes;

  RegisterEvent({
    required this.name,
    required this.email,
    required this.phone,
    required this.password,
    this.bloodGroup,
    this.medicalNotes,
  });

  @override
  List<Object?> get props => [name, email, phone, password];
}

class LogoutEvent extends AuthEvent {}

// States
abstract class AuthState extends Equatable {
  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthenticatedState extends AuthState {
  final String role; // SAHELI or GUARDIAN
  final UserModel? user;
  final GuardianModel? guardian;
  AuthenticatedState({required this.role, this.user, this.guardian});
  @override
  List<Object?> get props => [role, user, guardian];
}

class UnauthenticatedState extends AuthState {}

class AuthErrorState extends AuthState {
  final String message;
  AuthErrorState(this.message);
  @override
  List<Object?> get props => [message];
}

// BLoC
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;
  final GuardianRepository _guardianRepository;

  AuthBloc({
    AuthRepository? authRepository,
    GuardianRepository? guardianRepository,
  })  : _authRepository = authRepository ?? AuthRepository(),
        _guardianRepository = guardianRepository ?? GuardianRepository(),
        super(AuthInitial()) {
    on<CheckAuthStatusEvent>(_onCheckAuthStatus);
    on<LoginEvent>(_onLogin);
    on<GuardianLoginEvent>(_onGuardianLogin);
    on<RegisterEvent>(_onRegister);
    on<LogoutEvent>(_onLogout);
  }

  Future<void> _onCheckAuthStatus(CheckAuthStatusEvent event, Emitter<AuthState> emit) async {
    final token = await SecureStorageService.getAccessToken();
    final role = await SecureStorageService.getUserRole();
    if (token != null && role != null) {
      if (role == 'SAHELI') {
        final user = await _authRepository.getProfile();
        emit(AuthenticatedState(role: 'SAHELI', user: user));
      } else {
        emit(AuthenticatedState(role: 'GUARDIAN'));
      }
    } else {
      emit(UnauthenticatedState());
    }
  }

  Future<void> _onLogin(LoginEvent event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final user = await _authRepository.login(
        identifier: event.identifier,
        password: event.password,
      );
      emit(AuthenticatedState(role: 'SAHELI', user: user));
    } catch (e) {
      emit(AuthErrorState(e.toString()));
    }
  }

  Future<void> _onGuardianLogin(GuardianLoginEvent event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final guardian = await _guardianRepository.guardianLogin(
        identifier: event.identifier,
        password: event.password,
      );
      emit(AuthenticatedState(role: 'GUARDIAN', guardian: guardian));
    } catch (e) {
      emit(AuthErrorState(e.toString()));
    }
  }

  Future<void> _onRegister(RegisterEvent event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final user = await _authRepository.register(
        name: event.name,
        email: event.email,
        phone: event.phone,
        password: event.password,
        bloodGroup: event.bloodGroup,
        medicalNotes: event.medicalNotes,
      );
      emit(AuthenticatedState(role: 'SAHELI', user: user));
    } catch (e) {
      emit(AuthErrorState(e.toString()));
    }
  }

  Future<void> _onLogout(LogoutEvent event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    await _authRepository.logout();
    emit(UnauthenticatedState());
  }
}
