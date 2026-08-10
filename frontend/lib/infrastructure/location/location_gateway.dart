class AppLocation {
  const AppLocation(this.latitude, this.longitude);

  final double latitude;
  final double longitude;
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
        message: '현재 위치 확인됨 · 반경 100m',
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

  /// Opens app or location settings when the platform supports it.
  Future<bool> openRelevantSettings(LocationAccessStatus status);
}
