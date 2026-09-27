import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../storage/secure_storage_service.dart';

class LocalDeviceState {
  final bool isWearableOnline;
  final bool isCameraOnline;
  final int wearableBattery;
  final double wearableVoltage;
  final int wearableRssi;
  final String wearableIp;
  final String cameraIp;
  final String? lastCheckedTime;
  final String? errorMessage;

  const LocalDeviceState({
    this.isWearableOnline = false,
    this.isCameraOnline = false,
    this.wearableBattery = 0,
    this.wearableVoltage = 0.0,
    this.wearableRssi = 0,
    this.wearableIp = '192.168.1.150',
    this.cameraIp = '192.168.1.151:81',
    this.lastCheckedTime,
    this.errorMessage,
  });

  bool get isAnyConnected => isWearableOnline || isCameraOnline;

  LocalDeviceState copyWith({
    bool? isWearableOnline,
    bool? isCameraOnline,
    int? wearableBattery,
    double? wearableVoltage,
    int? wearableRssi,
    String? wearableIp,
    String? cameraIp,
    String? lastCheckedTime,
    String? errorMessage,
  }) {
    return LocalDeviceState(
      isWearableOnline: isWearableOnline ?? this.isWearableOnline,
      isCameraOnline: isCameraOnline ?? this.isCameraOnline,
      wearableBattery: wearableBattery ?? this.wearableBattery,
      wearableVoltage: wearableVoltage ?? this.wearableVoltage,
      wearableRssi: wearableRssi ?? this.wearableRssi,
      wearableIp: wearableIp ?? this.wearableIp,
      cameraIp: cameraIp ?? this.cameraIp,
      lastCheckedTime: lastCheckedTime ?? this.lastCheckedTime,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class LocalDeviceService {
  static final LocalDeviceService _instance = LocalDeviceService._internal();
  factory LocalDeviceService() => _instance;
  LocalDeviceService._internal();

  final ValueNotifier<LocalDeviceState> connectionState = ValueNotifier<LocalDeviceState>(
    const LocalDeviceState(),
  );

  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;
    try {
      final savedWearableIp = await SecureStorageService.getWearableIp() ?? '192.168.1.150';
      final savedCameraIp = await SecureStorageService.getCameraIp() ?? '192.168.1.151:81';
      connectionState.value = connectionState.value.copyWith(
        wearableIp: savedWearableIp,
        cameraIp: savedCameraIp,
        isWearableOnline: false, // Default is strictly OFFLINE until live ping
        isCameraOnline: false,
      );
    } catch (_) {}
  }

  Future<void> saveIps({required String wearableIp, required String cameraIp}) async {
    try {
      await SecureStorageService.saveDeviceIps(wearableIp: wearableIp.trim(), cameraIp: cameraIp.trim());
      connectionState.value = connectionState.value.copyWith(
        wearableIp: wearableIp.trim(),
        cameraIp: cameraIp.trim(),
      );
    } catch (_) {}
  }

  /// Pings ESP32 Wearable on the same local Wi-Fi network
  Future<bool> pingWearable({String? customIp}) async {
    final ip = customIp ?? connectionState.value.wearableIp;
    final sanitizedIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
    final uri = Uri.parse('http://$sanitizedIp/status');

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 2));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final battery = (data['battery_percent'] as num?)?.toInt() ?? 100;
        final voltage = (data['battery_voltage'] as num?)?.toDouble() ?? 4.2;
        final rssi = (data['wifi_rssi'] as num?)?.toInt() ?? -50;

        connectionState.value = connectionState.value.copyWith(
          isWearableOnline: true,
          wearableBattery: battery,
          wearableVoltage: voltage,
          wearableRssi: rssi,
          lastCheckedTime: DateTime.now().toIso8601String(),
          errorMessage: null,
        );
        return true;
      }
    } catch (e) {
      // Unreachable -> Device is physically powered OFF or on different Wi-Fi
    }

    connectionState.value = connectionState.value.copyWith(
      isWearableOnline: false,
      wearableBattery: 0,
      wearableVoltage: 0.0,
      wearableRssi: 0,
      lastCheckedTime: DateTime.now().toIso8601String(),
      errorMessage: 'Wearable not reachable. Ensure ESP32 is powered ON and on same Wi-Fi.',
    );
    return false;
  }

  /// Pings ESP32-CAM on the same local Wi-Fi network
  Future<bool> pingCamera({String? customIp}) async {
    final ip = customIp ?? connectionState.value.cameraIp;
    final sanitizedIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
    final uri = Uri.parse('http://$sanitizedIp/status');

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 2));
      if (response.statusCode == 200) {
        connectionState.value = connectionState.value.copyWith(
          isCameraOnline: true,
          lastCheckedTime: DateTime.now().toIso8601String(),
          errorMessage: null,
        );
        return true;
      }
    } catch (e) {
      // Unreachable
    }

    connectionState.value = connectionState.value.copyWith(
      isCameraOnline: false,
      lastCheckedTime: DateTime.now().toIso8601String(),
    );
    return false;
  }

  /// Sends test trigger to local ESP32 buzzer and vibration motor
  Future<bool> triggerLocalAlarm() async {
    final ip = connectionState.value.wearableIp.trim().replaceAll('http://', '').replaceAll('/', '');
    final uri = Uri.parse('http://$ip/test-alarm');
    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Ping both devices concurrently
  Future<void> pingAllDevices() async {
    await Future.wait([
      pingWearable(),
      pingCamera(),
    ]);
  }
}
