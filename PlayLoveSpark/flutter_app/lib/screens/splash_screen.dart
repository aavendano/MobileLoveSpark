import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import '../models/app_state.dart';
import '../routes.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    // Get service references
    final apiService = Provider.of<APIService>(context, listen: false);
    final authService = Provider.of<AuthService>(context, listen: false);
    final appState = Provider.of<AppState>(context, listen: false);
    
    // Show splash for at least 2 seconds
    await Future.delayed(const Duration(seconds: 2));
    
    if (!mounted) return;
    
    // If user is logged in, get their profile and current challenge
    if (authService.isLoggedIn) {
      try {
        // Get user profile
        final user = await apiService.getUserProfile();
        
        if (user != null) {
          appState.currentUser = user;
        }
        
        // Get current challenge
        final challenge = await apiService.getCurrentChallenge();
        if (challenge != null) {
          appState.activeChallenge = challenge;
        }
      } catch (e) {
        debugPrint('Error initializing user data: $e');
      }
    }
    
    if (!mounted) return;
    
    // Navigate to appropriate screen based on login status
    if (authService.isLoggedIn) {
      Navigator.of(context).pushReplacementNamed(AppRouter.home);
    } else {
      Navigator.of(context).pushReplacementNamed(AppRouter.onboarding);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF533278), // Primary purple color
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo or App Icon
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Center(
                child: Text(
                  "PL",
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.secondary, // Pink color
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            // App Name
            const Text(
              "PlayLove Spark",
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
                fontFamily: "Roboto",
              ),
            ),
            const SizedBox(height: 8),
            // Tagline
            Text(
              "Ignite connection and intimacy",
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 16,
                fontFamily: "OpenSans",
              ),
            ),
            const SizedBox(height: 48),
            // Loading indicator
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}