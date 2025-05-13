import 'package:flutter/foundation.dart';
import 'challenge.dart';
import 'user.dart';

class AppState extends ChangeNotifier {
  bool _isLoggedIn = false;
  bool _isLoading = false;
  User? _currentUser;
  Challenge? _activeChallenge;
  
  // Getters
  bool get isLoggedIn => _isLoggedIn;
  bool get isLoading => _isLoading;
  User? get currentUser => _currentUser;
  Challenge? get activeChallenge => _activeChallenge;
  
  // Setters
  set isLoggedIn(bool value) {
    _isLoggedIn = value;
    notifyListeners();
  }
  
  set isLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
  
  set currentUser(User? user) {
    _currentUser = user;
    notifyListeners();
  }
  
  set activeChallenge(Challenge? challenge) {
    _activeChallenge = challenge;
    notifyListeners();
  }
  
  // Methods
  void logout() {
    _isLoggedIn = false;
    _currentUser = null;
    _activeChallenge = null;
    notifyListeners();
  }
  
  void updateUserProfile(User user) {
    _currentUser = user;
    notifyListeners();
  }
  
  void completeChallenge() {
    // After completing a challenge, set it to null
    _activeChallenge = null;
    
    // If we have user progress data, we could update it here
    if (_currentUser != null && _currentUser!.progress != null) {
      final updatedProgress = _currentUser!.progress!.copyWith(
        streak: _currentUser!.progress!.streak + 1,
        totalCompleted: _currentUser!.progress!.totalCompleted + 1,
        lastCompleted: DateTime.now(),
      );
      
      _currentUser = _currentUser!.copyWith(progress: updatedProgress);
    }
    
    notifyListeners();
  }
}