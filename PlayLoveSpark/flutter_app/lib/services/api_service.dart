import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/challenge.dart';
import '../models/user_progress.dart';

class APIService extends ChangeNotifier {
  // Base URL for API
  // This would be updated for production with the real server address
  final String baseUrl = 'http://localhost:5000/api';
  int? userId;
  String? _authToken;

  // Getters
  bool get isAuthenticated => userId != null;
  
  // Initialize from shared preferences
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    userId = prefs.getInt('user_id');
    _authToken = prefs.getString('auth_token');
    notifyListeners();
  }
  
  // Set authentication
  Future<void> setAuth(int? id, String? token) async {
    userId = id;
    _authToken = token;
    
    final prefs = await SharedPreferences.getInstance();
    if (id != null) {
      await prefs.setInt('user_id', id);
    } else {
      await prefs.remove('user_id');
    }
    
    if (token != null) {
      await prefs.setString('auth_token', token);
    } else {
      await prefs.remove('auth_token');
    }
    
    notifyListeners();
  }
  
  // Clear authentication
  Future<void> clearAuth() async {
    await setAuth(null, null);
  }
  
  // Helper method for HTTP headers
  Map<String, String> get _headers {
    final headers = {
      'Content-Type': 'application/json',
    };
    
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }
  
  // User related API calls
  Future<User?> getUserProfile() async {
    if (userId == null) return null;
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/users-with-progress/$userId/'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return User.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to load user profile: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting user profile: $e');
      return null;
    }
  }
  
  Future<User?> createUserProfile(User user) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/users/'),
        headers: _headers,
        body: json.encode(user.toJson()),
      );
      
      if (response.statusCode == 201) {
        final createdUser = User.fromJson(json.decode(response.body));
        userId = createdUser.id;
        await setAuth(userId, null); // Store the user ID
        return createdUser;
      } else {
        throw Exception('Failed to create user: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error creating user: $e');
      return null;
    }
  }
  
  Future<User?> updateUserProfile(User user) async {
    if (userId == null) return null;
    
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/users/$userId/'),
        headers: _headers,
        body: json.encode(user.toJson()),
      );
      
      if (response.statusCode == 200) {
        return User.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to update user: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error updating user: $e');
      return null;
    }
  }
  
  // Challenge related API calls
  Future<Challenge?> getCurrentChallenge() async {
    if (userId == null) return null;
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/current-challenges/?user=$userId'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['results'] != null && data['results'].isNotEmpty) {
          return Challenge.fromJson(data['results'][0]);
        }
        return null; // No current challenge
      } else {
        throw Exception('Failed to load current challenge: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting current challenge: $e');
      return null;
    }
  }
  
  Future<Challenge?> generateChallenge({String? category}) async {
    if (userId == null) return null;
    
    try {
      final body = {
        'user_id': userId.toString(),
      };
      
      if (category != null) {
        body['category'] = category;
      }
      
      final response = await http.post(
        Uri.parse('$baseUrl/generate-challenge/'),
        headers: _headers,
        body: json.encode(body),
      );
      
      if (response.statusCode == 200) {
        return Challenge.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to generate challenge: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error generating challenge: $e');
      return null;
    }
  }
  
  Future<bool> completeChallenge(String challengeId, String category) async {
    if (userId == null) return false;
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/complete-challenge/'),
        headers: _headers,
        body: json.encode({
          'user_id': userId.toString(),
          'challenge_id': challengeId,
          'category': category,
        }),
      );
      
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Error completing challenge: $e');
      return false;
    }
  }
  
  // Progress related API calls
  Future<UserProgress?> getUserProgress() async {
    if (userId == null) return null;
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/progress/?user=$userId'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['results'] != null && data['results'].isNotEmpty) {
          return UserProgress.fromJson(data['results'][0]);
        }
        return null;
      } else {
        throw Exception('Failed to load user progress: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting user progress: $e');
      return null;
    }
  }
  
  // Article related API calls
  Future<List<dynamic>> getArticles() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/articles/'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load articles: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting articles: $e');
      return [];
    }
  }
  
  Future<dynamic> getArticleById(String articleId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/articles/$articleId/'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load article: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting article: $e');
      return null;
    }
  }
  
  // Product related API calls
  Future<List<dynamic>> getProducts() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/products/'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting products: $e');
      return [];
    }
  }
  
  Future<dynamic> getProductById(String productId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/products/$productId/'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load product: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error getting product: $e');
      return null;
    }
  }
}