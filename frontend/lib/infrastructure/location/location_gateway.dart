import 'dart:math' as math;

class AppLocation {
  const AppLocation(this.latitude, this.longitude);

  final double latitude;
  final double longitude;

  double distanceTo(AppLocation other) {
    const earthRadiusMeters = 6371000.0;
    double radians(double degrees) => degrees * math.pi / 180;
    final deltaLatitude = radians(other.latitude - latitude);
    final deltaLongitude = radians(other.longitude - longitude);
    final a =
        math.pow(math.sin(deltaLatitude / 2), 2) +
        math.cos(radians(latitude)) *
            math.cos(radians(other.latitude)) *
            math.pow(math.sin(deltaLongitude / 2), 2);
    return 2 * earthRadiusMeters * math.asin(math.sqrt(a));
  }
}

enum LocationAccessStatus {
  granted,
  denied,
  deniedForever,
  serviceDisabled,
  timedOut,
  unavailable,
}

class LocationAccessResult {
  const LocationAccessResult({
    required this.status,
    required this.message,
    this.location,
  });

  const LocationAccessResult.granted(AppLocation location)
    : this(
        status: LocationAccessStatus.granted,
        message: '현재 위치 확인됨 · 실시간 거리 사용 중',
        location: location,
      );

  final LocationAccessStatus status;
  final String message;
  final AppLocation? location;

  bool get isGranted =>
      status == LocationAccessStatus.granted && location != null;
}

abstract interface class LocationGateway {
  /// Called after the first app frame to request foreground location permission.
  Future<LocationAccessResult> requestAtStartup();

  /// Re-check permission, service state, and fetch a fresh foreground position.
  Future<LocationAccessResult> refresh();

  /// Emits foreground position changes after permission has been granted.
  Stream<AppLocation> watch();

  /// Opens app or location settings when the platform supports it.
  Future<bool> openRelevantSettings(LocationAccessStatus status);
}
