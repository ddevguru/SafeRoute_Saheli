import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../models/emergency_incident_model.dart';
import '../repositories/emergency_repository.dart';
import '../storage/offline_cache_service.dart';

// Events
abstract class EmergencyEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class CheckActiveEmergencyEvent extends EmergencyEvent {}

class TriggerEmergencyEvent extends EmergencyEvent {
  final String triggerType;
  final double latitude;
  final double longitude;
  final int batteryPercent;

  TriggerEmergencyEvent({
    this.triggerType = 'BUTTON',
    required this.latitude,
    required this.longitude,
    this.batteryPercent = 100,
  });

  @override
  List<Object?> get props => [triggerType, latitude, longitude, batteryPercent];
}

class CancelEmergencyEvent extends EmergencyEvent {
  final String incidentId;
  final String reason;
  CancelEmergencyEvent({required this.incidentId, this.reason = "User verified safe condition"});
  @override
  List<Object?> get props => [incidentId, reason];
}

class LocationPingEvent extends EmergencyEvent {
  final double latitude;
  final double longitude;
  LocationPingEvent({required this.latitude, required this.longitude});
  @override
  List<Object?> get props => [latitude, longitude];
}

// States
abstract class EmergencyState extends Equatable {
  @override
  List<Object?> get props => [];
}

class EmergencySafeState extends EmergencyState {}

class EmergencyTriggeringState extends EmergencyState {}

class EmergencyActiveState extends EmergencyState {
  final EmergencyIncidentModel incident;
  EmergencyActiveState(this.incident);
  @override
  List<Object?> get props => [incident];
}

class EmergencyErrorState extends EmergencyState {
  final String message;
  EmergencyErrorState(this.message);
  @override
  List<Object?> get props => [message];
}

// BLoC
class EmergencyBloc extends Bloc<EmergencyEvent, EmergencyState> {
  final EmergencyRepository _emergencyRepository;

  EmergencyBloc({EmergencyRepository? emergencyRepository})
      : _emergencyRepository = emergencyRepository ?? EmergencyRepository(),
        super(EmergencySafeState()) {
    on<CheckActiveEmergencyEvent>(_onCheckActiveEmergency);
    on<TriggerEmergencyEvent>(_onTriggerEmergency);
    on<CancelEmergencyEvent>(_onCancelEmergency);
    on<LocationPingEvent>(_onLocationPing);
  }

  Future<void> _onCheckActiveEmergency(CheckActiveEmergencyEvent event, Emitter<EmergencyState> emit) async {
    try {
      final incident = await _emergencyRepository.getActiveEmergency();
      if (incident != null) {
        emit(EmergencyActiveState(incident));
      } else {
        emit(EmergencySafeState());
      }
    } catch (_) {
      emit(EmergencySafeState());
    }
  }

  Future<void> _onTriggerEmergency(TriggerEmergencyEvent event, Emitter<EmergencyState> emit) async {
    emit(EmergencyTriggeringState());
    try {
      final incident = await _emergencyRepository.triggerEmergency(
        triggerType: event.triggerType,
        latitude: event.latitude,
        longitude: event.longitude,
        batteryPercent: event.batteryPercent,
      );
      await OfflineCacheService.recordLocalIncident({
        'id': incident.id,
        'trigger_type': incident.triggerType,
        'status': incident.status,
        'started_at': incident.startedAt ?? DateTime.now().toIso8601String(),
        'latitude': incident.latitude,
        'longitude': incident.longitude,
        'battery_percent': incident.batteryPercent,
        'confidence': incident.confidence,
        'device_id': incident.deviceId ?? 'SAHELI-WEARABLE-001',
      });
      emit(EmergencyActiveState(incident));
    } catch (e) {
      // Even if network fails, record local fallback incident
      final localFallbackId = 'INC-LOCAL-${DateTime.now().millisecondsSinceEpoch}';
      await OfflineCacheService.recordLocalIncident({
        'id': localFallbackId,
        'trigger_type': event.triggerType,
        'status': 'ACTIVE',
        'started_at': DateTime.now().toIso8601String(),
        'latitude': event.latitude,
        'longitude': event.longitude,
        'battery_percent': event.batteryPercent,
        'confidence': 1.0,
        'device_id': 'SAHELI-WEARABLE-001',
      });
      emit(EmergencyErrorState(e.toString()));
    }
  }

  Future<void> _onCancelEmergency(CancelEmergencyEvent event, Emitter<EmergencyState> emit) async {
    try {
      final success = await _emergencyRepository.cancelEmergency(event.incidentId, reason: event.reason);
      if (success) {
        emit(EmergencySafeState());
      }
    } catch (e) {
      emit(EmergencyErrorState(e.toString()));
    }
  }

  Future<void> _onLocationPing(LocationPingEvent event, Emitter<EmergencyState> emit) async {
    try {
      await _emergencyRepository.updateLocation(
        latitude: event.latitude,
        longitude: event.longitude,
      );
    } catch (_) {}
  }
}
