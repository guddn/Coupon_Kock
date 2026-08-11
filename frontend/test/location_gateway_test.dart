import 'package:coupon_kock/infrastructure/location/location_gateway.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('calculates distance between actual coordinates in meters', () {
    const origin = AppLocation(37.2822, 127.0437);
    const nearby = AppLocation(37.2822, 127.0447);

    final distance = origin.distanceTo(nearby);

    expect(distance, greaterThan(80));
    expect(distance, lessThan(100));
  });
}
