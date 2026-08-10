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

  factory Coupon.fromJson(Map<String, dynamic> json) {
    return Coupon(
      id: json['coupon_id'] as String,
      brand: json['brand'] as String,
      productName: json['product_name'] as String,
      expiryLabel: json['expiry_date'] as String,
      faceValue: (json['face_value'] as num).toInt(),
    );
  }
}

class CouponDraft {
  const CouponDraft({
    required this.brand,
    required this.productName,
    required this.faceValue,
    required this.expiryDate,
  });

  final String brand;
  final String productName;
  final int faceValue;
  final DateTime expiryDate;
}
