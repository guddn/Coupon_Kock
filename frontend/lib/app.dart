import 'package:flutter/material.dart';

import 'features/home/home_screen.dart';

class CouponKockApp extends StatelessWidget {
  const CouponKockApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF2962FF);
    return MaterialApp(
      title: '쿠폰콕',
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
