import '../../domain/models/coupon.dart';
import '../../domain/models/recommendation.dart';

abstract interface class RecommendationRepository {
  Future<List<Coupon>> loadCoupons();
  Future<Recommendation> recommend({required int purchaseAmount});
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
  Future<Recommendation> recommend({required int purchaseAmount}) async {
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
