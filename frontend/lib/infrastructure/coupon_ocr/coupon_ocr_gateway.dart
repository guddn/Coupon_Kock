abstract interface class CouponOcrGateway {
  /// Android: run ML Kit on-device, then mask PIN and barcode data.
  /// Web demo: accept sanitized text entered by the user.
  Future<String> extractSanitizedText(Object imageReference);
}
