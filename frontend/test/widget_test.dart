import 'package:coupon_kock/app.dart';
import 'package:coupon_kock/infrastructure/location/location_gateway.dart';
import 'package:coupon_kock/infrastructure/recommendations/recommendation_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders coupon and recommendation demo flow', (tester) async {
    final locationGateway = _FakeLocationGateway();
    await tester.pumpWidget(
      CouponKockApp(
        repository: const DemoRecommendationRepository(),
        locationGateway: locationGateway,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('쿠폰콕'), findsOneWidget);
    expect(find.text('현재 위치 확인됨 · 반경 100m'), findsOneWidget);
    expect(locationGateway.startupRequests, 1);

    await tester.tap(find.text('10,000원 혜택 비교'));
    await tester.pumpAndSettle();
    await tester.drag(find.byType(CustomScrollView), const Offset(0, -900));
    await tester.pumpAndSettle();

    expect(find.textContaining('스타카페'), findsWidgets);
    expect(find.text('4,500원'), findsOneWidget);
    expect(find.text('총 5,500원 절약'), findsOneWidget);
  });
}

class _FakeLocationGateway implements LocationGateway {
  int startupRequests = 0;

  @override
  Future<LocationAccessResult> requestAtStartup() async {
    startupRequests += 1;
    return const LocationAccessResult.granted(AppLocation(37.2822, 127.0437));
  }

  @override
  Future<LocationAccessResult> refresh() async {
    return const LocationAccessResult.granted(AppLocation(37.2822, 127.0437));
  }

  @override
  Future<bool> openRelevantSettings(LocationAccessStatus status) async => false;
}
