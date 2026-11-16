import 'package:flutter/material.dart';

class AppColors {
  static const bubblePink = Color(0xFFF6E5EB);
  static const bubblePinkLight = Color(0xFFFDF8FA);
  static const bubblePinkBorder = Color(0xFFEDD4DC);
  static const bubbleCream = Color(0xFFFCF9F3);
  static const bubbleCreamDark = Color(0xFFF4EFE6);
  static const bubbleCreamBorder = Color(0xFFE8E1D3);
  static const bubbleSage = Color(0xFFBDCEB8);
  static const bubbleSageLight = Color(0xFFEBF2EA);
  static const bubbleSageBorder = Color(0xFFA7BCA2);
  static const bubbleSageDark = Color(0xFF6D8A6B);
  static const bubbleSageDeep = Color(0xFF486047);
  static const bubbleInk = Color(0xFF1B251D);
  static const bubbleMuted = Color(0xFF637265);
  static const bubbleHeart = Color(0xFFEF4444);
  static const bubbleHeartBg = Color(0xFFFEE2E2);
  static const background = Color(0xFFF7F5F0);
}

class AppTheme {
  static ThemeData light() {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: AppColors.background,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.bubbleSageDark,
        primary: AppColors.bubbleSageDark,
        secondary: AppColors.bubbleSage,
        surface: AppColors.bubbleCream,
        background: AppColors.background,
        error: AppColors.bubbleHeart,
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontWeight: FontWeight.w800, color: AppColors.bubbleInk),
        titleLarge: TextStyle(fontWeight: FontWeight.w800, color: AppColors.bubbleInk),
        titleMedium: TextStyle(fontWeight: FontWeight.w700, color: AppColors.bubbleInk),
        bodyLarge: TextStyle(color: AppColors.bubbleInk),
        bodyMedium: TextStyle(color: AppColors.bubbleInk),
        bodySmall: TextStyle(color: AppColors.bubbleMuted),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.bubbleCream,
        foregroundColor: AppColors.bubbleInk,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AppColors.bubbleCreamBorder),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.bubbleSageDark,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
    );
  }
}
