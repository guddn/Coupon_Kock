class AppLocation {
  const AppLocation(this.latitude, this.longitude);

  final double latitude;
  final double longitude;
}

abstract interface class LocationGateway {
  /// Return foreground location only. Do not persist exact coordinates.
  Future<AppLocation> getForegroundLocation();
}
