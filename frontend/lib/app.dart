import 'package:flutter/material.dart';

import 'core/config/app_config.dart';
import 'features/home/home_screen.dart';
import 'infrastructure/location/geolocator_location_gateway.dart';
import 'infrastructure/location/location_gateway.dart';
import 'infrastructure/recommendations/recommendation_repository.dart';

class CouponKockApp extends StatelessWidget {
  CouponKockApp({
    super.key,
    RecommendationRepository? repository,
    LocationGateway? locationGateway,
  }) : repository =
           repository ??
           ApiRecommendationRepository(
             baseUrl: Uri.parse(AppConfig.apiBaseUrl),
           ),
       locationGateway = locationGateway ?? const GeolocatorLocationGateway();

  final RecommendationRepository repository;
  final LocationGateway locationGateway;

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFFFDB846);
    return MaterialApp(
      title: '쿠폰콕',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFFAFAFA),
        fontFamily: 'sans-serif',
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderSide: BorderSide.none,
            borderRadius: BorderRadius.circular(18),
          ),
          enabledBorder: OutlineInputBorder(
            borderSide: const BorderSide(color: Color(0xFFEEEEEE)),
            borderRadius: BorderRadius.circular(18),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF202020),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
          ),
        ),
        navigationBarTheme: const NavigationBarThemeData(
          backgroundColor: Colors.white,
          indicatorColor: Color(0xFFFFE7B0),
          elevation: 0,
        ),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(20)),
          ),
        ),
      ),
      home: HomeScreen(
        repository: repository,
        locationGateway: locationGateway,
      ),
    );
  }
}
