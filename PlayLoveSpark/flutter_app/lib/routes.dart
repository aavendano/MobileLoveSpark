import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/home_screen.dart';
import 'screens/challenge_screen.dart';
import 'screens/progress_screen.dart';
import 'screens/education_screen.dart';
import 'screens/article_detail_screen.dart';
import 'screens/products_screen.dart';
import 'screens/product_detail_screen.dart';
import 'screens/settings_screen.dart';

class AppRouter {
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String home = '/home';
  static const String challenge = '/challenge';
  static const String progress = '/progress';
  static const String education = '/education';
  static const String articleDetail = '/article-detail';
  static const String products = '/products';
  static const String productDetail = '/product-detail';
  static const String settings = '/settings';

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case splash:
        return MaterialPageRoute(builder: (_) => const SplashScreen());
      
      case onboarding:
        return MaterialPageRoute(builder: (_) => const OnboardingScreen());
      
      case home:
        return MaterialPageRoute(builder: (_) => const HomeScreen());
      
      case challenge:
        // Check if there's a challenge being passed
        if (settings.arguments != null) {
          return MaterialPageRoute(
            builder: (_) => ChallengeScreen(
              initialChallenge: settings.arguments as dynamic,
            ),
          );
        }
        return MaterialPageRoute(builder: (_) => const ChallengeScreen());
      
      case progress:
        return MaterialPageRoute(builder: (_) => const ProgressScreen());
      
      case education:
        return MaterialPageRoute(builder: (_) => const EducationScreen());
      
      case articleDetail:
        // Article ID is required for this route
        if (settings.arguments != null) {
          return MaterialPageRoute(
            builder: (_) => ArticleDetailScreen(
              articleId: settings.arguments as String,
            ),
          );
        }
        // If no article ID is provided, go back to education screen
        return MaterialPageRoute(builder: (_) => const EducationScreen());
      
      case products:
        return MaterialPageRoute(builder: (_) => const ProductsScreen());
      
      case productDetail:
        // Product ID is required for this route
        if (settings.arguments != null) {
          return MaterialPageRoute(
            builder: (_) => ProductDetailScreen(
              productId: settings.arguments as String,
            ),
          );
        }
        // If no product ID is provided, go back to products screen
        return MaterialPageRoute(builder: (_) => const ProductsScreen());
      
      case settings:
        return MaterialPageRoute(builder: (_) => const SettingsScreen());
      
      default:
        // If the route is not found, go to splash screen
        return MaterialPageRoute(builder: (_) => const SplashScreen());
    }
  }
}