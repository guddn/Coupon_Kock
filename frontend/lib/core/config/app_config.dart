class AppConfig {
  const AppConfig._();

  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://coupon-kock-663890381698.asia-northeast3.run.app',
  );
}
