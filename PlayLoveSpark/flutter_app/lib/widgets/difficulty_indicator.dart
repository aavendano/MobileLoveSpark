import 'package:flutter/material.dart';

class DifficultyIndicator extends StatelessWidget {
  final int difficulty;
  final int maxDifficulty;

  const DifficultyIndicator({
    super.key,
    required this.difficulty,
    this.maxDifficulty = 5,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Text(
          'Difficulty: ',
          style: TextStyle(
            color: Colors.grey,
            fontSize: 14,
          ),
        ),
        Row(
          children: List.generate(maxDifficulty, (index) {
            final isActive = index < difficulty;
            return Icon(
              Icons.star,
              size: 16,
              color: isActive ? const Color(0xFFF4436C) : Colors.grey.shade300,
            );
          }),
        ),
      ],
    );
  }
}