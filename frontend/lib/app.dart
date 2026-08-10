import 'package:flutter/material.dart';

import 'features/home/home_screen.dart';

class CouponKnockApp extends StatelessWidget {
  const CouponKnockApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF2962FF);
    return MaterialApp(
      title: 'Coupon Knock',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF7F8FC),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(20)),
          ),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
