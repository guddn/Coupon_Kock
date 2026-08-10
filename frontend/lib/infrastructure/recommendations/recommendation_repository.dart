import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../domain/models/coupon.dart';
import '../../domain/models/recommendation.dart';

abstract interface class RecommendationRepository {
  Future<List<Coupon>> loadCoupons();
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
              'store_id': 'demo-store',
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
