import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'routes.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/notification_service.dart';
import 'services/theme_service.dart';
import 'models/app_state.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Create service instances
  final apiService = APIService();
  final authService = AuthService();
  final notificationService = NotificationService();
  final themeService = ThemeService();
  final appState = AppState();
  
  // Initialize services
  await Future.wait([
    notificationService.initialize(),
    apiService.init(),
    authService.init(),
    themeService.init(),
  ]);
  
  // Set initial app state based on auth status
  appState.isLoggedIn = authService.isLoggedIn;
  
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => apiService),
        ChangeNotifierProvider(create: (_) => authService),
        ChangeNotifierProvider(create: (_) => themeService),
        ChangeNotifierProvider(create: (_) => appState),
        Provider(create: (_) => notificationService),
      ],
      child: const PlayLoveSparkApp(),
    ),
  );
}

class PlayLoveSparkApp extends StatelessWidget {
  const PlayLoveSparkApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeService = Provider.of<ThemeService>(context);
    
    return MaterialApp(
      title: 'PlayLove Spark',
      theme: ThemeData(
        // Primary color (Dark Purple)
        primaryColor: const Color(0xFF533278),
        // Secondary color (Pink)
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF533278),
          secondary: const Color(0xFFF4436C),
          brightness: themeService.isDarkMode ? Brightness.dark : Brightness.light,
        ),
        // Text theme using Roboto
        textTheme: GoogleFonts.robotoTextTheme(
          Theme.of(context).textTheme,
        ),
        // AppBar theme
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF533278),
          foregroundColor: Colors.white,
        ),
        // Elevated button theme
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFF4436C),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: 24,
              vertical: 12,
            ),
          ),
        ),
        // Input decoration theme
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(
              color: Color(0xFF533278),
              width: 2,
            ),
          ),
          floatingLabelStyle: const TextStyle(
            color: Color(0xFF533278),
          ),
        ),
        // Theme brightness based on user preference
        brightness: themeService.isDarkMode ? Brightness.dark : Brightness.light,
      ),
      // Set up navigation using the router
      initialRoute: AppRouter.splash,
      onGenerateRoute: AppRouter.generateRoute,
      debugShowCheckedModeBanner: false,
    );
  }
}