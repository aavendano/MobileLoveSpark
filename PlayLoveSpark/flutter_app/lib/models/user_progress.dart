class UserProgress {
  final int? id;
  final int? userId;
  final int streak;
  final DateTime? lastCompleted;
  final double sparkLevel;
  final int totalCompleted;

  UserProgress({
    this.id,
    this.userId,
    required this.streak,
    this.lastCompleted,
    required this.sparkLevel,
    required this.totalCompleted,
  });

  // Create a copy with optional changes
  UserProgress copyWith({
    int? id,
    int? userId,
    int? streak,
    DateTime? lastCompleted,
    double? sparkLevel,
    int? totalCompleted,
  }) {
    return UserProgress(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      streak: streak ?? this.streak,
      lastCompleted: lastCompleted ?? this.lastCompleted,
      sparkLevel: sparkLevel ?? this.sparkLevel,
      totalCompleted: totalCompleted ?? this.totalCompleted,
    );
  }

  // Convert from JSON
  factory UserProgress.fromJson(Map<String, dynamic> json) {
    return UserProgress(
      id: json['id'],
      userId: json['user'],
      streak: json['streak'] ?? 0,
      lastCompleted: json['last_completed'] != null 
          ? DateTime.parse(json['last_completed']) 
          : null,
      sparkLevel: json['spark_level']?.toDouble() ?? 0.0,
      totalCompleted: json['total_completed'] ?? 0,
    );
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'user': userId,
      'streak': streak,
      if (lastCompleted != null) 
        'last_completed': lastCompleted!.toIso8601String(),
      'spark_level': sparkLevel,
      'total_completed': totalCompleted,
    };
  }
}