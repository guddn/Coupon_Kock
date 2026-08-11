import 'dart:async';

import 'package:geolocator/geolocator.dart';

import 'location_gateway.dart';

class GeolocatorLocationGateway implements LocationGateway {
  const GeolocatorLocationGateway();

  static const _settings = LocationSettings(
    accuracy: LocationAccuracy.high,
    timeLimit: Duration(seconds: 12),
  );

  static const _streamSettings = LocationSettings(
    accuracy: LocationAccuracy.high,
    distanceFilter: 5,
  );

  @override
  Future<LocationAccessResult> requestAtStartup() {
    return _resolvePosition(requestPermission: true);
  }

  @override
  Future<LocationAccessResult> refresh() {
    return _resolvePosition(requestPermission: true);
  }

  @override
  Stream<AppLocation> watch() => Geolocator.getPositionStream(
    locationSettings: _streamSettings,
  ).map((position) => AppLocation(position.latitude, position.longitude));

  Future<LocationAccessResult> _resolvePosition({
    required bool requestPermission,
  }) async {
    try {
      var permission = await Geolocator.checkPermission();
      if (requestPermission &&
          (permission == LocationPermission.denied ||
              permission == LocationPermission.unableToDetermine)) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.denied ||
          permission == LocationPermission.unableToDetermine) {
        return const LocationAccessResult(
          status: LocationAccessStatus.denied,
          message: '주변 혜택을 찾으려면 위치 권한이 필요합니다.',
        );
      }
      if (permission == LocationPermission.deniedForever) {
        return const LocationAccessResult(
          status: LocationAccessStatus.deniedForever,
          message: '앱 설정에서 위치 권한을 허용해 주세요.',
        );
      }

      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return const LocationAccessResult(
          status: LocationAccessStatus.serviceDisabled,
          message: '기기의 위치 서비스를 켜 주세요.',
        );
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: _settings,
      );
      return LocationAccessResult.granted(
        AppLocation(position.latitude, position.longitude),
      );
    } on TimeoutException {
      return const LocationAccessResult(
        status: LocationAccessStatus.timedOut,
        message: '현재 위치를 확인하지 못했습니다. 다시 시도해 주세요.',
      );
    } on LocationServiceDisabledException {
      return const LocationAccessResult(
        status: LocationAccessStatus.serviceDisabled,
        message: '기기의 위치 서비스를 켜 주세요.',
      );
    } on PermissionDeniedException {
      return const LocationAccessResult(
        status: LocationAccessStatus.denied,
        message: '주변 혜택을 찾으려면 위치 권한이 필요합니다.',
      );
    } catch (_) {
      return const LocationAccessResult(
        status: LocationAccessStatus.unavailable,
        message: '현재 위치 기능을 사용할 수 없습니다.',
      );
    }
  }

  @override
  Future<bool> openRelevantSettings(LocationAccessStatus status) async {
    try {
      if (status == LocationAccessStatus.deniedForever) {
        return Geolocator.openAppSettings();
      }
      if (status == LocationAccessStatus.serviceDisabled) {
        return Geolocator.openLocationSettings();
      }
    } on UnsupportedError {
      return false;
    }
    return false;
  }
}
