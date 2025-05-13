class Challenge {
  final String id;
  final String title;
  final String description;
  final String category;
  final int difficulty;
  final int timeRequired;
  final String? imageUrl;
  final List<String> tips;
  final DateTime? generatedAt;

  Challenge({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.difficulty,
    required this.timeRequired,
    this.imageUrl,
    required this.tips,
    this.generatedAt,
  });

  // Create a copy with optional changes
  Challenge copyWith({
    String? id,
    String? title,
    String? description,
    String? category,
    int? difficulty,
    int? timeRequired,
    String? imageUrl,
    List<String>? tips,
    DateTime? generatedAt,
  }) {
    return Challenge(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      category: category ?? this.category,
      difficulty: difficulty ?? this.difficulty,
      timeRequired: timeRequired ?? this.timeRequired,
      imageUrl: imageUrl ?? this.imageUrl,
      tips: tips ?? this.tips,
      generatedAt: generatedAt ?? this.generatedAt,
    );
  }

  // Convert from JSON
  factory Challenge.fromJson(Map<String, dynamic> json) {
    return Challenge(
      id: json['id'] ?? json['challenge_id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      category: json['category'] ?? '',
      difficulty: json['difficulty'] ?? 1,
      timeRequired: json['time_required'] ?? 15,
      imageUrl: json['image_url'],
      tips: List<String>.from(json['tips'] ?? []),
      generatedAt: json['generated_at'] != null
          ? DateTime.parse(json['generated_at'])
          : null,
    );
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'category': category,
      'difficulty': difficulty,
      'time_required': timeRequired,
      if (imageUrl != null) 'image_url': imageUrl,
      'tips': tips,
      if (generatedAt != null) 'generated_at': generatedAt!.toIso8601String(),
    };
  }
}