class NearbyStore {
  const NearbyStore({
    required this.id,
    required this.name,
    required this.category,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.distanceMeters,
  });

  final String id;
  final String name;
  final String category;
  final String address;
  final double latitude;
  final double longitude;
  final double distanceMeters;

  factory NearbyStore.fromJson(Map<String, dynamic> json) {
    return NearbyStore(
      id: json['store_id'] as String,
      name: json['name'] as String,
      category: json['category'] as String,
      address: json['address'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      distanceMeters: (json['distance_m'] as num).toDouble(),
    );
  }
}

class NearbyStoresResult {
  const NearbyStoresResult({
    required this.stores,
    required this.isFixture,
    this.notice,
  });

  final List<NearbyStore> stores;
  final bool isFixture;
  final String? notice;
}
