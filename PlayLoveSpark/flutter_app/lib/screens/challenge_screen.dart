import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/challenge.dart';
import '../services/api_service.dart';
import '../widgets/difficulty_indicator.dart';

class ChallengeScreen extends StatefulWidget {
  final Challenge? initialChallenge;

  const ChallengeScreen({
    super.key,
    this.initialChallenge,
  });

  @override
  State<ChallengeScreen> createState() => _ChallengeScreenState();
}

class _ChallengeScreenState extends State<ChallengeScreen> {
  Challenge? _challenge;
  bool _isLoading = false;
  bool _isCompletingChallenge = false;

  @override
  void initState() {
    super.initState();
    _challenge = widget.initialChallenge;
    if (_challenge == null) {
      _fetchCurrentChallenge();
    }
  }

  Future<void> _fetchCurrentChallenge() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final challenge = await apiService.getCurrentChallenge();
      
      if (mounted) {
        setState(() {
          _challenge = challenge;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error fetching challenge: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _generateNewChallenge({String? category}) async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final challenge = await apiService.generateChallenge(category: category);
      
      if (mounted) {
        setState(() {
          _challenge = challenge;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error generating challenge: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _completeChallenge() async {
    if (_challenge == null) return;
    
    setState(() {
      _isCompletingChallenge = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final success = await apiService.completeChallenge(
        _challenge!.id,
        _challenge!.category,
      );
      
      if (mounted) {
        setState(() {
          _isCompletingChallenge = false;
        });
        
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Challenge completed! Great job!'),
              backgroundColor: Colors.green,
            ),
          );
          
          // Automatically generate a new challenge
          _generateNewChallenge();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to complete challenge. Please try again.'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isCompletingChallenge = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error completing challenge: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildCategoryChip(String category) {
    final color = _getCategoryColor(category);
    
    return Chip(
      label: Text(
        category,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
      backgroundColor: color.withOpacity(0.2),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'Communication Boosters':
        return Colors.blue;
      case 'Physical Touch & Affection':
        return Colors.green;
      case 'Creative Date Night Ideas':
        return Colors.purple;
      case 'Sexual Exploration':
        return Colors.red;
      case 'Emotional Connection':
        return Colors.orange;
      default:
        return const Color(0xFF533278);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Challenge'),
        backgroundColor: const Color(0xFF533278),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _challenge == null
              ? _buildNoChallenge()
              : _buildChallengeDetails(),
    );
  }

  Widget _buildNoChallenge() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.sentiment_dissatisfied,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No current challenge found',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Generate a new challenge to get started!',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => _generateNewChallenge(),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF4436C),
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
            child: const Text('Generate Challenge'),
          ),
        ],
      ),
    );
  }

  Widget _buildChallengeDetails() {
    final challenge = _challenge!;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Category and difficulty
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildCategoryChip(challenge.category),
              DifficultyIndicator(difficulty: challenge.difficulty),
            ],
          ),
          const SizedBox(height: 16),
          
          // Title
          Text(
            challenge.title,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          
          // Time required
          Row(
            children: [
              const Icon(
                Icons.access_time,
                size: 16,
                color: Colors.grey,
              ),
              const SizedBox(width: 4),
              Text(
                'Approx. ${challenge.timeRequired} minutes',
                style: const TextStyle(
                  color: Colors.grey,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Description
          const Text(
            'Description',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            challenge.description,
            style: const TextStyle(
              fontSize: 16,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 24),
          
          // Tips
          if (challenge.tips.isNotEmpty) ...[
            const Text(
              'Tips & Suggestions',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            ...challenge.tips.map((tip) => Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(
                    Icons.lightbulb_outline,
                    color: Color(0xFFF4436C),
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      tip,
                      style: const TextStyle(
                        fontSize: 16,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            )),
            const SizedBox(height: 16),
          ],
          
          // Action buttons
          const Divider(),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _isCompletingChallenge 
                      ? null 
                      : () => _generateNewChallenge(),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: const Text('Try Another'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton(
                  onPressed: _isCompletingChallenge 
                      ? null 
                      : _completeChallenge,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF4436C),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: _isCompletingChallenge
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text('Mark Complete'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Category selection
          const Text(
            'Try a different category',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildCategoryButton(
                  label: 'Communication',
                  category: 'Communication Boosters',
                  color: Colors.blue,
                ),
                _buildCategoryButton(
                  label: 'Physical Touch',
                  category: 'Physical Touch & Affection',
                  color: Colors.green,
                ),
                _buildCategoryButton(
                  label: 'Date Night',
                  category: 'Creative Date Night Ideas',
                  color: Colors.purple,
                ),
                _buildCategoryButton(
                  label: 'Intimacy',
                  category: 'Sexual Exploration',
                  color: Colors.red,
                ),
                _buildCategoryButton(
                  label: 'Emotional',
                  category: 'Emotional Connection',
                  color: Colors.orange,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryButton({
    required String label,
    required String category,
    required Color color,
  }) {
    final isSelected = _challenge?.category == category;
    
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: OutlinedButton(
        onPressed: _isLoading || _isCompletingChallenge
            ? null
            : () => _generateNewChallenge(category: category),
        style: OutlinedButton.styleFrom(
          backgroundColor: isSelected ? color.withOpacity(0.1) : null,
          side: BorderSide(
            color: isSelected ? color : Colors.grey,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? color : Colors.grey,
          ),
        ),
      ),
    );
  }
}