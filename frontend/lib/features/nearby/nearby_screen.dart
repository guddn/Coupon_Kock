import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../../domain/models/nearby_store.dart';
import '../../core/config/app_config.dart';
import '../../infrastructure/location/location_gateway.dart';
import '../../infrastructure/recommendations/recommendation_repository.dart';

class NearbyScreen extends StatefulWidget {
  const NearbyScreen({
    super.key,
    required this.repository,
    required this.locationResult,
    required this.locationLoading,
    required this.couponRevision,
    required this.onLocationAction,
  });

  final RecommendationRepository repository;
  final LocationAccessResult? locationResult;
  final bool locationLoading;
  final int couponRevision;
  final VoidCallback onLocationAction;

  @override
  State<NearbyScreen> createState() => _NearbyScreenState();
}

class _NearbyScreenState extends State<NearbyScreen> {
  Future<NearbyStoresResult>? _stores;
  GoogleMapController? _mapController;
  String? _selectedStoreId;

  @override
  void initState() {
    super.initState();
    _loadIfReady();
  }

  @override
  void didUpdateWidget(covariant NearbyScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    final oldLocation = oldWidget.locationResult?.location;
    final newLocation = widget.locationResult?.location;
    final locationChanged =
        newLocation != null &&
        (oldLocation == null || oldLocation.distanceTo(newLocation) >= 5);
    final couponsChanged = oldWidget.couponRevision != widget.couponRevision;
    if (locationChanged || couponsChanged) {
      _loadIfReady();
    }
    if (locationChanged) {
      final controller = _mapController;
      if (controller != null) {
        unawaited(
          controller.animateCamera(
            CameraUpdate.newLatLng(
              LatLng(newLocation.latitude, newLocation.longitude),
            ),
          ),
        );
      }
    }
  }

  void _loadIfReady() {
    final location = widget.locationResult?.location;
    if (location == null) return;
    _selectedStoreId = null;
    _stores = widget.repository.loadNearbyStores(
      latitude: location.latitude,
      longitude: location.longitude,
    );
  }

  void _reload() => setState(_loadIfReady);

  Future<void> _selectStore(NearbyStore store) async {
    setState(() => _selectedStoreId = store.id);
    await _mapController?.animateCamera(
      CameraUpdate.newLatLngZoom(LatLng(store.latitude, store.longitude), 17),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (kIsWeb && AppConfig.googleMapsApiKey.isEmpty) {
      return _LocationRequired(
        title: 'Google Maps API 키가 필요해요',
        description: 'GOOGLE_MAPS_API_KEY를 dart-define으로 전달한 뒤 앱을 다시 실행해 주세요.',
        buttonLabel: '설정 확인',
        onPressed: () {},
      );
    }
    final location = widget.locationResult?.location;
    if (widget.locationLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (location == null) {
      return _LocationRequired(onPressed: widget.onLocationAction);
    }
    return FutureBuilder<NearbyStoresResult>(
      future: _stores,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return _LocationRequired(
            title: '주변 매장을 불러오지 못했어요',
            description: '${snapshot.error}',
            buttonLabel: '다시 시도',
            onPressed: _reload,
          );
        }
        final result = snapshot.data;
        final sortedStores = [...(result?.stores ?? const <NearbyStore>[])]
          ..sort(
            (first, second) =>
                first.distanceMeters.compareTo(second.distanceMeters),
          );
        final stores = sortedStores.take(5).toList();
        final currentPosition = LatLng(location.latitude, location.longitude);
        final markers = stores.indexed
            .map(
              (entry) => Marker(
                markerId: MarkerId(entry.$2.id),
                position: LatLng(entry.$2.latitude, entry.$2.longitude),
                icon: BitmapDescriptor.defaultMarkerWithHue(
                  entry.$2.id == _selectedStoreId
                      ? BitmapDescriptor.hueOrange
                      : BitmapDescriptor.hueRed,
                ),
                onTap: () => setState(() => _selectedStoreId = entry.$2.id),
                infoWindow: InfoWindow(
                  title: '${entry.$1 + 1}. ${entry.$2.name}',
                  snippet:
                      '${entry.$2.category} · ${entry.$2.distanceMeters.round()}m',
                ),
              ),
            )
            .toSet();
        markers.add(
          Marker(
            markerId: const MarkerId('current-location'),
            position: currentPosition,
            infoWindow: const InfoWindow(title: '현재 위치'),
          ),
        );
        return Scaffold(
          appBar: AppBar(
            title: const Text(
              '내 쿠폰 사용 가능 매장',
              style: TextStyle(fontWeight: FontWeight.w800),
            ),
            actions: [
              IconButton(
                onPressed: _reload,
                icon: const Icon(Icons.refresh_rounded),
              ),
            ],
          ),
          body: Column(
            children: [
              if (result?.notice != null)
                MaterialBanner(
                  content: Text(result!.notice!),
                  leading: Icon(
                    result.isFixture
                        ? Icons.science_outlined
                        : Icons.info_outline,
                  ),
                  actions: [
                    TextButton(
                      onPressed: ScaffoldMessenger.of(
                        context,
                      ).hideCurrentMaterialBanner,
                      child: const Text('확인'),
                    ),
                  ],
                ),
              Expanded(
                flex: 3,
                child: GoogleMap(
                  initialCameraPosition: CameraPosition(
                    target: currentPosition,
                    zoom: 15.5,
                  ),
                  myLocationEnabled: true,
                  myLocationButtonEnabled: true,
                  zoomControlsEnabled: false,
                  markers: markers,
                  onMapCreated: (controller) => _mapController = controller,
                  circles: {
                    Circle(
                      circleId: const CircleId('current-location-radius'),
                      center: currentPosition,
                      radius: 25,
                      fillColor: Colors.blue.withValues(alpha: 0.18),
                      strokeColor: Colors.blue,
                      strokeWidth: 2,
                    ),
                  },
                ),
              ),
              Expanded(
                flex: 2,
                child: snapshot.connectionState != ConnectionState.done
                    ? const Center(child: CircularProgressIndicator())
                    : stores.isEmpty
                    ? const Center(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Text(
                            '반경 1km 안에 등록 쿠폰을 사용할 수 있는 매장이 없습니다.',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : Column(
                        children: [
                          Padding(
                            padding: const EdgeInsets.fromLTRB(16, 12, 16, 6),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    '쿠폰 사용 가능 · 가까운 ${stores.length}곳',
                                    style: const TextStyle(
                                      fontSize: 17,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                ),
                                _DataSourceBadge(isFixture: result!.isFixture),
                              ],
                            ),
                          ),
                          Expanded(
                            child: ListView.separated(
                              padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
                              itemCount: stores.length,
                              separatorBuilder: (_, _) =>
                                  const Divider(height: 1),
                              itemBuilder: (_, index) {
                                final store = stores[index];
                                final selected = store.id == _selectedStoreId;
                                return ListTile(
                                  selected: selected,
                                  selectedTileColor: const Color(0xFFFFF3D4),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(14),
                                  ),
                                  onTap: () => _selectStore(store),
                                  leading: CircleAvatar(
                                    backgroundColor: selected
                                        ? const Color(0xFFFDB846)
                                        : const Color(0xFFFFF3D4),
                                    foregroundColor: Colors.black87,
                                    child: Text(
                                      '${index + 1}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ),
                                  title: Text(
                                    store.name,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                  subtitle: Text(
                                    '${store.category} · ${store.address}',
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  trailing: Text(
                                    '${store.distanceMeters.round()}m',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ],
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _DataSourceBadge extends StatelessWidget {
  const _DataSourceBadge({required this.isFixture});

  final bool isFixture;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
    decoration: BoxDecoration(
      color: isFixture ? const Color(0xFFFFE0B2) : const Color(0xFFC8E6C9),
      borderRadius: BorderRadius.circular(999),
    ),
    child: Text(
      isFixture ? '샘플 데이터' : '공공데이터',
      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
    ),
  );
}

class _LocationRequired extends StatelessWidget {
  const _LocationRequired({
    this.title = '현재 위치가 필요해요',
    this.description = '위치 권한을 허용하면 현재 위치와 반경 1km 주변 매장을 지도에 표시합니다.',
    this.buttonLabel = '위치 권한 확인',
    required this.onPressed,
  });
  final String title;
  final String description;
  final String buttonLabel;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.location_off_outlined, size: 64),
          const SizedBox(height: 16),
          Text(
            title,
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          Text(description, textAlign: TextAlign.center),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: onPressed,
            icon: const Icon(Icons.my_location),
            label: Text(buttonLabel),
          ),
        ],
      ),
    ),
  );
}
