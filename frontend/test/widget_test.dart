import 'package:coupon_knock/app.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders coupon and recommendation demo flow', (tester) async {
    await tester.pumpWidget(const CouponKnockApp());
    await tester.pumpAndSettle();

    expect(find.text('Coupon Knock'), findsOneWidget);
    expect(find.textContaining('스타카페'), findsOneWidget);

    await tester.tap(find.text('10,000원 혜택 비교'));
    await tester.pumpAndSettle();

    expect(find.text('4,500원'), findsOneWidget);
    expect(find.text('총 5,500원 절약'), findsOneWidget);
  });
}
