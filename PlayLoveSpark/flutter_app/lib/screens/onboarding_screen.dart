import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/user.dart';
import '../models/app_state.dart';
import '../routes.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _formKey = GlobalKey<FormState>();
  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _isSubmitting = false;
  
  // Form fields
  final TextEditingController _partner1Controller = TextEditingController();
  final TextEditingController _partner2Controller = TextEditingController();
  String _relationshipStatus = '';
  String _relationshipDuration = '';
  String _challengeFrequency = 'daily';
  final List<String> _preferredCategories = [];
  final List<String> _excludedCategories = [];
  
  // Relationship status options
  final List<String> _relationshipStatusOptions = [
    'Dating',
    'Engaged',
    'Married',
    'Long-term partners',
    'Other',
  ];
  
  // Relationship duration options
  final List<String> _relationshipDurationOptions = [
    'Less than 6 months',
    '6 months to 1 year',
    '1-2 years',
    '2-5 years',
    '5-10 years',
    '10+ years',
  ];
  
  // Challenge frequency options
  final List<String> _challengeFrequencyOptions = [
    'daily',
    'weekly',
    'biweekly',
  ];
  
  // Categories
  final List<String> _allCategories = [
    'Communication Boosters',
    'Physical Touch & Affection',
    'Creative Date Night Ideas',
    'Sexual Exploration',
    'Emotional Connection',
  ];
  
  // Submit the form
  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    if (_relationshipStatus.isEmpty || _relationshipDuration.isEmpty) {
      // Go back to relationship page if not filled out
      _pageController.animateToPage(
        1,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
      return;
    }
    
    setState(() {
      _isSubmitting = true;
    });
    
    final apiService = Provider.of<APIService>(context, listen: false);
    final authService = Provider.of<AuthService>(context, listen: false);
    final appState = Provider.of<AppState>(context, listen: false);
    
    try {
      // Create user model
      final user = User(
        partner1Name: _partner1Controller.text,
        partner2Name: _partner2Controller.text,
        relationshipStatus: _relationshipStatus,
        relationshipDuration: _relationshipDuration,
        challengeFrequency: _challengeFrequency,
        preferredCategories: _preferredCategories,
        excludedCategories: _excludedCategories,
      );
      
      // Create user in API
      final createdUser = await apiService.createUserProfile(user);
      
      if (!mounted) return;
      
      if (createdUser != null && createdUser.id != null) {
        // Set authenticated user in auth service
        await authService.setUser(createdUser.id);
        
        // Update app state
        appState.isLoggedIn = true;
        appState.currentUser = createdUser;
        
        // Generate initial challenge
        final challenge = await apiService.generateChallenge();
        if (challenge != null) {
          appState.activeChallenge = challenge;
        }
        
        // Navigate to home screen
        Navigator.of(context).pushReplacementNamed(AppRouter.home);
      } else {
        throw Exception('Failed to create user profile');
      }
    } catch (e) {
      if (mounted) {
        // Show error
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
        
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }
  
  // Next page
  void _nextPage() {
    if (_currentPage < 3) {
      // Validate current page before proceeding
      if (_currentPage == 0) {
        if (_partner1Controller.text.isEmpty || _partner2Controller.text.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Please enter both names to continue'),
              backgroundColor: Colors.red,
            ),
          );
          return;
        }
      } else if (_currentPage == 1) {
        if (_relationshipStatus.isEmpty || _relationshipDuration.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Please select both relationship status and duration'),
              backgroundColor: Colors.red,
            ),
          );
          return;
        }
      }
      
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _submitForm();
    }
  }
  
  // Previous page
  void _previousPage() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  @override
  void dispose() {
    _partner1Controller.dispose();
    _partner2Controller.dispose();
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Create Your Profile'),
        backgroundColor: const Color(0xFF533278),
      ),
      body: Form(
        key: _formKey,
        child: PageView(
          controller: _pageController,
          physics: const NeverScrollableScrollPhysics(),
          onPageChanged: (index) {
            setState(() {
              _currentPage = index;
            });
          },
          children: [
            // Page 1: Names
            _buildNamesPage(),
            
            // Page 2: Relationship Status and Duration
            _buildRelationshipPage(),
            
            // Page 3: Challenge Frequency
            _buildFrequencyPage(),
            
            // Page 4: Categories
            _buildCategoriesPage(),
          ],
        ),
      ),
      bottomNavigationBar: BottomAppBar(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Back button
              TextButton(
                onPressed: (_currentPage > 0 && !_isSubmitting) ? _previousPage : null,
                child: Text(
                  'Back',
                  style: TextStyle(
                    color: (_currentPage > 0 && !_isSubmitting)
                        ? const Color(0xFF533278) 
                        : Colors.grey,
                  ),
                ),
              ),
              
              // Page indicators
              Row(
                children: List.generate(
                  4,
                  (index) => Container(
                    width: 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: index == _currentPage
                          ? const Color(0xFFF4436C)
                          : Colors.grey.shade300,
                    ),
                  ),
                ),
              ),
              
              // Next/Submit button
              _isSubmitting
                  ? const SizedBox(
                      height: 24,
                      width: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                      ),
                    )
                  : ElevatedButton(
                      onPressed: _nextPage,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF4436C),
                      ),
                      child: Text(
                        _currentPage < 3 ? 'Next' : 'Submit',
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
            ],
          ),
        ),
      ),
    );
  }
  
  // Page 1: Names
  Widget _buildNamesPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Let\'s get to know you',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF533278),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'What should we call you and your partner?',
            style: TextStyle(
              fontSize: 16,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 32),
          
          // Partner 1 Name
          TextFormField(
            controller: _partner1Controller,
            decoration: const InputDecoration(
              labelText: 'Your Name',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.person),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your name';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          
          // Partner 2 Name
          TextFormField(
            controller: _partner2Controller,
            decoration: const InputDecoration(
              labelText: 'Partner\'s Name',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.person),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your partner\'s name';
              }
              return null;
            },
          ),
        ],
      ),
    );
  }
  
  // Page 2: Relationship Status and Duration
  Widget _buildRelationshipPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Tell us about your relationship',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF533278),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'This helps us personalize your experience',
            style: TextStyle(
              fontSize: 16,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 32),
          
          // Relationship Status
          const Text(
            'Relationship Status',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _relationshipStatusOptions.map((status) {
              final isSelected = status == _relationshipStatus;
              return ChoiceChip(
                label: Text(status),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() {
                    _relationshipStatus = selected ? status : '';
                  });
                },
                backgroundColor: Colors.grey.shade200,
                selectedColor: const Color(0xFFF4436C).withOpacity(0.2),
                labelStyle: TextStyle(
                  color: isSelected 
                      ? const Color(0xFFF4436C) 
                      : Colors.black87,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              );
            }).toList(),
          ),
          if (_currentPage >= 1 && _relationshipStatus.isEmpty)
            const Padding(
              padding: EdgeInsets.only(top: 8.0),
              child: Text(
                'Please select your relationship status',
                style: TextStyle(
                  color: Colors.red,
                  fontSize: 12,
                ),
              ),
            ),
          
          const SizedBox(height: 24),
          
          // Relationship Duration
          const Text(
            'How long have you been together?',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _relationshipDurationOptions.map((duration) {
              final isSelected = duration == _relationshipDuration;
              return ChoiceChip(
                label: Text(duration),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() {
                    _relationshipDuration = selected ? duration : '';
                  });
                },
                backgroundColor: Colors.grey.shade200,
                selectedColor: const Color(0xFFF4436C).withOpacity(0.2),
                labelStyle: TextStyle(
                  color: isSelected 
                      ? const Color(0xFFF4436C) 
                      : Colors.black87,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              );
            }).toList(),
          ),
          if (_currentPage >= 1 && _relationshipDuration.isEmpty)
            const Padding(
              padding: EdgeInsets.only(top: 8.0),
              child: Text(
                'Please select your relationship duration',
                style: TextStyle(
                  color: Colors.red,
                  fontSize: 12,
                ),
              ),
            ),
        ],
      ),
    );
  }
  
  // Page 3: Challenge Frequency
  Widget _buildFrequencyPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Set your challenge frequency',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF533278),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'How often would you like to receive new challenges?',
            style: TextStyle(
              fontSize: 16,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 32),
          
          // Challenge Frequency
          for (final frequency in _challengeFrequencyOptions)
            RadioListTile<String>(
              title: Text(
                frequency == 'daily' 
                    ? 'Daily'
                    : frequency == 'weekly' 
                        ? 'Weekly' 
                        : 'Twice a week',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Text(
                frequency == 'daily' 
                    ? 'A new challenge every day to keep things exciting'
                    : frequency == 'weekly' 
                        ? 'One challenge per week for a more relaxed pace' 
                        : 'Two challenges per week for a balanced experience',
                style: const TextStyle(
                  fontSize: 14,
                ),
              ),
              value: frequency,
              groupValue: _challengeFrequency,
              activeColor: const Color(0xFFF4436C),
              onChanged: (value) {
                setState(() {
                  _challengeFrequency = value ?? 'daily';
                });
              },
            ),
        ],
      ),
    );
  }
  
  // Page 4: Categories
  Widget _buildCategoriesPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Select your preferences',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF533278),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Which categories are you interested in?',
            style: TextStyle(
              fontSize: 16,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 32),
          
          // Preferred Categories
          const Text(
            'Preferred Categories (select all that apply)',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          for (final category in _allCategories)
            CheckboxListTile(
              title: Text(category),
              value: _preferredCategories.contains(category),
              activeColor: const Color(0xFFF4436C),
              onChanged: (selected) {
                setState(() {
                  if (selected == true) {
                    if (!_preferredCategories.contains(category)) {
                      _preferredCategories.add(category);
                    }
                    // Remove from excluded if it's now preferred
                    if (_excludedCategories.contains(category)) {
                      _excludedCategories.remove(category);
                    }
                  } else {
                    _preferredCategories.remove(category);
                  }
                });
              },
            ),
            
          const SizedBox(height: 24),
          
          // Excluded Categories
          const Text(
            'Categories to avoid (optional)',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          for (final category in _allCategories)
            CheckboxListTile(
              title: Text(category),
              value: _excludedCategories.contains(category),
              activeColor: Colors.red,
              onChanged: (selected) {
                setState(() {
                  if (selected == true) {
                    if (!_excludedCategories.contains(category)) {
                      _excludedCategories.add(category);
                    }
                    // Remove from preferred if it's now excluded
                    if (_preferredCategories.contains(category)) {
                      _preferredCategories.remove(category);
                    }
                  } else {
                    _excludedCategories.remove(category);
                  }
                });
              },
            ),
        ],
      ),
    );
  }
}