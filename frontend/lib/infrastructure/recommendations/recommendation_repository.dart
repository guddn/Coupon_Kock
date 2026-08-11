import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../domain/models/coupon.dart';
import '../../domain/models/nearby_store.dart';
import '../../domain/models/recommendation.dart';

abstract interface class RecommendationRepository {
  Future<List<Coupon>> loadCoupons();
  Future<Coupon> createCoupon(CouponDraft draft);
  Future<NearbyStoresResult> loadNearbyStores({
    required double latitude,
    required double longitude,
    int radiusMeters = 1000,
  });
  Future<Recommendation> recommend({
    required int purchaseAmount,
    required double latitude,
    required double longitude,
  });
}

class RecommendationException implements Exception {
  const RecommendationException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ApiRecommendationRepository implements RecommendationRepository {
  ApiRecommendationRepository({required this.baseUrl, http.Client? client})
    : _client = client ?? http.Client();

  final Uri baseUrl;
  final http.Client _client;

  Uri get _recommendationEndpoint {
    final normalizedBase = baseUrl.toString().replaceFirst(RegExp(r'/$'), '');
    return Uri.parse('$normalizedBase/api/recommendations');
  }

  String get _normalizedBase =>
      baseUrl.toString().replaceFirst(RegExp(r'/$'), '');

  Uri get _couponsEndpoint => Uri.parse('$_normalizedBase/api/coupons');

  Uri _nearbyStoresEndpoint(
    double latitude,
    double longitude,
    int radiusMeters,
  ) {
    return Uri.parse('$_normalizedBase/api/stores/nearby').replace(
      queryParameters: {
        'latitude': '$latitude',
        'longitude': '$longitude',
        'radius_m': '$radiusMeters',
        'limit': '5',
      },
    );
  }

  @override
  Future<List<Coupon>> loadCoupons() async {
    final response = await _send(
      () => _client.get(
        _couponsEndpoint.replace(queryParameters: {'user_id': 'demo-user'}),
      ),
    );
    _requireStatus(response, 200, '쿠폰을 불러오지 못했습니다.');
    try {
      final payload = jsonDecode(response.body) as List<dynamic>;
      return payload
          .map((item) => Coupon.fromJson(item as Map<String, dynamic>))
          .toList();
    } on Object {
      throw const RecommendationException('쿠폰 응답 형식이 예상과 다릅니다.');
    }
  }

  @override
  Future<Coupon> createCoupon(CouponDraft draft) async {
    final response = await _send(
      () => _client.post(
        _couponsEndpoint,
        headers: const {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': 'demo-user',
          'brand': draft.brand,
          'product_name': draft.productName,
          'coupon_type': 'fixed',
          'face_value': draft.faceValue,
          'expiry_date': _dateOnly(draft.expiryDate),
        }),
      ),
    );
    _requireStatus(response, 201, '쿠폰 등록에 실패했습니다.');
    try {
      return Coupon.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } on Object {
      throw const RecommendationException('쿠폰 응답 형식이 예상과 다릅니다.');
    }
  }

  @override
  Future<NearbyStoresResult> loadNearbyStores({
    required double latitude,
    required double longitude,
    int radiusMeters = 1000,
  }) async {
    final response = await _send(
      () =>
          _client.get(_nearbyStoresEndpoint(latitude, longitude, radiusMeters)),
    );
    _requireStatus(response, 200, '주변 매장을 불러오지 못했습니다.');
    try {
      final payload = jsonDecode(response.body) as Map<String, dynamic>;
      final stores = (payload['stores'] as List<dynamic>)
          .map((item) => NearbyStore.fromJson(item as Map<String, dynamic>))
          .toList();
      return NearbyStoresResult(
        stores: stores,
        isFixture: payload['data_source'] == 'fixture',
        notice: payload['notice'] as String?,
      );
    } on Object {
      throw const RecommendationException('매장 응답 형식이 예상과 다릅니다.');
    }
  }

  Future<http.Response> _send(Future<http.Response> Function() request) async {
    try {
      return await request().timeout(const Duration(seconds: 10));
    } on TimeoutException {
      throw const RecommendationException('서버 응답 시간이 초과되었습니다.');
    } on http.ClientException {
      throw const RecommendationException('백엔드에 연결할 수 없습니다.');
    }
  }

  void _requireStatus(http.Response response, int expected, String message) {
    if (response.statusCode != expected) {
      throw RecommendationException('$message (HTTP ${response.statusCode})');
    }
  }

  @override
  Future<Recommendation> recommend({
    required int purchaseAmount,
    required double latitude,
    required double longitude,
  }) async {
    late final http.Response response;
    try {
      response = await _client
          .post(
            _recommendationEndpoint,
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode({
              'user_id': 'demo-user',
              'latitude': latitude,
              'longitude': longitude,
              'purchase_amount': purchaseAmount,
            }),
          )
          .timeout(const Duration(seconds: 10));
    } on TimeoutException {
      throw const RecommendationException('서버 응답 시간이 초과되었습니다.');
    } on http.ClientException {
      throw const RecommendationException('백엔드에 연결할 수 없습니다.');
    }

    if (response.statusCode != 200) {
      throw RecommendationException(
        '추천 요청에 실패했습니다. (HTTP ${response.statusCode})',
      );
    }

    try {
      final payload = jsonDecode(response.body) as Map<String, dynamic>;
      final store = payload['store'] as Map<String, dynamic>;
      final option = payload['recommended_option'] as Map<String, dynamic>;
      final componentsJson = option['components'] as List<dynamic>;
      final sourcesJson = payload['sources'] as List<dynamic>;
      final components = componentsJson.map((item) {
        final component = item as Map<String, dynamic>;
        return SavingComponent(
          label: component['name'] as String,
          amount: (component['discount_amount'] as num).toInt(),
        );
      }).toList();
      final sourceTitle = sourcesJson.isEmpty
          ? '공식 출처 없음'
          : (sourcesJson.first as Map<String, dynamic>)['title'] as String;

      return Recommendation(
        storeName: store['name'] as String,
        distanceMeters: (store['distance_m'] as num).round(),
        purchaseAmount: purchaseAmount,
        finalPrice: (option['final_price'] as num).toInt(),
        components: components,
        sourceTitle: sourceTitle,
      );
    } on FormatException {
      throw const RecommendationException('서버 응답을 해석할 수 없습니다.');
    } on TypeError {
      throw const RecommendationException('서버 응답 형식이 예상과 다릅니다.');
    }
  }
}

class DemoRecommendationRepository implements RecommendationRepository {
  const DemoRecommendationRepository();

  @override
  Future<List<Coupon>> loadCoupons() async => const [
    Coupon(
      id: 'demo-coupon',
      brand: '스타카페',
      productName: '모바일 금액권',
      expiryLabel: '2026.12.31',
      faceValue: 5000,
    ),
  ];

  @override
  Future<Coupon> createCoupon(CouponDraft draft) async => Coupon(
    id: 'demo-created-coupon',
    brand: draft.brand,
    productName: draft.productName,
    expiryLabel: _dateOnly(draft.expiryDate),
    faceValue: draft.faceValue,
  );

  @override
  Future<NearbyStoresResult> loadNearbyStores({
    required double latitude,
    required double longitude,
    int radiusMeters = 1000,
  }) async => NearbyStoresResult(
    isFixture: true,
    notice: '테스트용 매장입니다.',
    stores: [
      NearbyStore(
        id: 'demo-store',
        name: '스타카페 아주대점',
        category: '카페',
        address: '경기도 수원시 영통구',
        latitude: latitude + 0.0003,
        longitude: longitude + 0.0002,
        distanceMeters: 42,
      ),
    ],
  );

  @override
  Future<Recommendation> recommend({
    required int purchaseAmount,
    required double latitude,
    required double longitude,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    const couponSaving = 5000;
    final afterCoupon = (purchaseAmount - couponSaving).clamp(
      0,
      purchaseAmount,
    );
    final cardSaving = (afterCoupon * 0.1).floor().clamp(0, 1000);
    return Recommendation(
      storeName: '스타카페 아주대점',
      distanceMeters: 72,
      purchaseAmount: purchaseAmount,
      finalPrice: afterCoupon - cardSaving,
      components: [
        const SavingComponent(label: '보유 쿠폰', amount: couponSaving),
        SavingComponent(label: '카드 10% 할인', amount: cardSaving),
      ],
      sourceTitle: '개발용 공식 혜택 fixture - 배포 전 교체',
    );
  }
}

String _dateOnly(DateTime value) {
  String twoDigits(int number) => number.toString().padLeft(2, '0');
  return '${value.year}-${twoDigits(value.month)}-${twoDigits(value.day)}';
}
