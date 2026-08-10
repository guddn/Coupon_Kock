import 'package:coupon_kock/app.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders coupon and recommendation demo flow', (tester) async {
    await tester.pumpWidget(const CouponKockApp());
    await tester.pumpAndSettle();

    expect(find.text('쿠폰콕'), findsOneWidget);
    expect(find.textContaining('스타카페'), findsOneWidget);

    await tester.tap(find.text('10,000원 혜택 비교'));
    await tester.pumpAndSettle();

    expect(find.text('4,500원'), findsOneWidget);
    expect(find.text('총 5,500원 절약'), findsOneWidget);
  });
}
