class Coupon {
  const Coupon({
    required this.id,
    required this.brand,
    required this.productName,
    required this.expiryLabel,
    required this.faceValue,
    this.used = false,
  });

  final String id;
  final String brand;
  final String productName;
  final String expiryLabel;
  final int faceValue;
  final bool used;
}
