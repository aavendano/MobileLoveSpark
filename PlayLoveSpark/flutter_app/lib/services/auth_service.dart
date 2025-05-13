import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService extends ChangeNotifier {
  int? userId;
  bool get isLoggedIn => userId != null;
  
  // Initialize from shared preferences
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    userId = prefs.getInt('user_id');
    notifyListeners();
  }
  
  // Set authenticated user
  Future<void> setUser(int? id) async {
    userId = id;
    
    final prefs = await SharedPreferences.getInstance();
    if (id != null) {
      await prefs.setInt('user_id', id);
    } else {
      await prefs.remove('user_id');
    }
    
    notifyListeners();
  }
  
  // Logout user
  Future<void> logout() async {
    userId = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('user_id');
    notifyListeners();
  }
}