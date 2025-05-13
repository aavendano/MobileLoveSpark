import 'user_progress.dart';

class User {
  final int? id;
  final String partner1Name;
  final String partner2Name;
  final String relationshipStatus;
  final String relationshipDuration;
  final String challengeFrequency;
  final List<String> preferredCategories;
  final List<String> excludedCategories;
  final DateTime? createdAt;
  final DateTime? lastLogin;
  final UserProgress? progress;

  User({
    this.id,
    required this.partner1Name,
    required this.partner2Name,
    required this.relationshipStatus,
    required this.relationshipDuration,
    required this.challengeFrequency,
    required this.preferredCategories,
    required this.excludedCategories,
    this.createdAt,
    this.lastLogin,
    this.progress,
  });

  // Create a copy of the user with optional changes
  User copyWith({
    int? id,
    String? partner1Name,
    String? partner2Name,
    String? relationshipStatus,
    String? relationshipDuration,
    String? challengeFrequency,
    List<String>? preferredCategories,
    List<String>? excludedCategories,
    DateTime? createdAt,
    DateTime? lastLogin,
    UserProgress? progress,
  }) {
    return User(
      id: id ?? this.id,
      partner1Name: partner1Name ?? this.partner1Name,
      partner2Name: partner2Name ?? this.partner2Name,
      relationshipStatus: relationshipStatus ?? this.relationshipStatus,
      relationshipDuration: relationshipDuration ?? this.relationshipDuration,
      challengeFrequency: challengeFrequency ?? this.challengeFrequency,
      preferredCategories: preferredCategories ?? this.preferredCategories,
      excludedCategories: excludedCategories ?? this.excludedCategories,
      createdAt: createdAt ?? this.createdAt,
      lastLogin: lastLogin ?? this.lastLogin,
      progress: progress ?? this.progress,
    );
  }

  // Convert from JSON
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      partner1Name: json['partner1_name'],
      partner2Name: json['partner2_name'],
      relationshipStatus: json['relationship_status'],
      relationshipDuration: json['relationship_duration'],
      challengeFrequency: json['challenge_frequency'],
      preferredCategories: List<String>.from(json['preferred_categories'] ?? []),
      excludedCategories: List<String>.from(json['excluded_categories'] ?? []),
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      lastLogin: json['last_login'] != null ? DateTime.parse(json['last_login']) : null,
      progress: json['progress'] != null ? UserProgress.fromJson(json['progress']) : null,
    );
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'partner1_name': partner1Name,
      'partner2_name': partner2Name,
      'relationship_status': relationshipStatus,
      'relationship_duration': relationshipDuration,
      'challenge_frequency': challengeFrequency,
      'preferred_categories': preferredCategories,
      'excluded_categories': excludedCategories,
    };
  }
}