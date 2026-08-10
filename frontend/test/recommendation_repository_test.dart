import 'dart:convert';

import 'package:coupon_kock/infrastructure/recommendations/recommendation_repository.dart';
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
}
