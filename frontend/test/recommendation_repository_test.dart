import 'dart:convert';

import 'package:coupon_kock/infrastructure/recommendations/recommendation_repository.dart';
import 'package:coupon_kock/domain/models/coupon.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('parses Cloud Run recommendation response', () async {
    final client = MockClient((request) async {
      expect(request.url.path, '/api/recommendations');
      expect(request.method, 'POST');
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      expect(body['latitude'], 37.2819);
      expect(body['longitude'], 127.0441);
      return http.Response(
        '''
        {
          "store": {"name": "데모 매장", "distance_m": 72.4},
          "recommended_option": {
            "final_price": 4500,
            "components": [
              {"name": "보유 쿠폰", "discount_amount": 5000},
              {"name": "카드 할인", "discount_amount": 500}
            ]
          },
          "sources": [{"title": "공식 혜택 문서"}]
        }
        ''',
        200,
        headers: {'content-type': 'application/json'},
      );
    });
    final repository = ApiRecommendationRepository(
      baseUrl: Uri.parse('https://coupon-kock.example'),
      client: client,
    );

    final result = await repository.recommend(
      purchaseAmount: 10000,
      latitude: 37.2819,
      longitude: 127.0441,
    );

    expect(result.storeName, '데모 매장');
    expect(result.distanceMeters, 72);
    expect(result.finalPrice, 4500);
    expect(result.saving, 5500);
    expect(result.sourceTitle, '공식 혜택 문서');
  });

  test('registers and lists coupons through backend API', () async {
    final client = MockClient((request) async {
      if (request.method == 'POST') {
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['brand'], '스타카페');
        return http.Response(
          '{"coupon_id":"coupon-1","brand":"스타카페","product_name":"금액권","face_value":5000,"expiry_date":"2027-12-31"}',
          201,
          headers: {'content-type': 'application/json'},
        );
      }
      expect(request.url.queryParameters['user_id'], 'demo-user');
      return http.Response(
        '[{"coupon_id":"coupon-1","brand":"스타카페","product_name":"금액권","face_value":5000,"expiry_date":"2027-12-31"}]',
        200,
        headers: {'content-type': 'application/json'},
      );
    });
    final repository = ApiRecommendationRepository(
      baseUrl: Uri.parse('https://coupon-kock.example'),
      client: client,
    );

    final created = await repository.createCoupon(
      CouponDraft(
        brand: '스타카페',
        productName: '금액권',
        faceValue: 5000,
        expiryDate: DateTime(2027, 12, 31),
      ),
    );
    final coupons = await repository.loadCoupons();

    expect(created.id, 'coupon-1');
    expect(coupons.single.faceValue, 5000);
  });

  test('parses nearby public stores', () async {
    final client = MockClient((request) async {
      expect(request.url.path, '/api/stores/nearby');
      expect(request.url.queryParameters['radius_m'], '1000');
      return http.Response(
        '{"data_source":"public_data","stores":[{"store_id":"s1","name":"카페","category":"커피","address":"수원시","latitude":37.28,"longitude":127.04,"distance_m":84.2}]}',
        200,
        headers: {'content-type': 'application/json'},
      );
    });
    final repository = ApiRecommendationRepository(
      baseUrl: Uri.parse('https://coupon-kock.example'),
      client: client,
    );

    final result = await repository.loadNearbyStores(
      latitude: 37.2822,
      longitude: 127.0437,
    );

    expect(result.isFixture, isFalse);
    expect(result.stores.single.name, '카페');
  });
}
