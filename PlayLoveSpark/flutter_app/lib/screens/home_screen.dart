import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/challenge.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'challenge_screen.dart';
import 'progress_screen.dart';
import 'education_screen.dart';
import 'products_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  User? _user;
  Challenge? _currentChallenge;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final user = await apiService.getUserProfile();
      final challenge = await apiService.getCurrentChallenge();
      
      if (mounted) {
        setState(() {
          _user = user;
          _currentChallenge = challenge;
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
            content: Text('Error loading data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _logout() async {
    final authService = Provider.of<AuthService>(context, listen: false);
    final apiService = Provider.of<APIService>(context, listen: false);
    
    await authService.logout();
    await apiService.clearAuth();
    
    if (!mounted) return;
    
    Navigator.of(context).pushReplacementNamed('/');
  }

  Future<void> _generateNewChallenge() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final challenge = await apiService.generateChallenge();
      
      if (mounted) {
        setState(() {
          _currentChallenge = challenge;
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

  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return _buildHomeTab();
      case 1:
        return const ChallengeScreen();
      case 2:
        return const ProgressScreen();
      case 3:
        return const EducationScreen();
      case 4:
        return const ProductsScreen();
      default:
        return _buildHomeTab();
    }
  }

  Widget _buildHomeTab() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_user == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Error loading profile'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadUserData,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadUserData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome section
            _buildWelcomeCard(),
            const SizedBox(height: 24),
            
            // Current challenge
            _buildCurrentChallengeCard(),
            const SizedBox(height: 24),
            
            // Quick stats
            _buildQuickStatsCard(),
            const SizedBox(height: 24),
            
            // Categories
            _buildCategoriesSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildWelcomeCard() {
    final progressText = _user?.progress != null 
        ? 'Day ${_user!.progress!.streak} | ${_user!.progress!.sparkLevel.toStringAsFixed(1)}% Spark' 
        : 'Just getting started';
    
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: const Color(0xFF533278),
                  radius: 24,
                  child: Text(
                    _user!.partner1Name.isNotEmpty ? _user!.partner1Name[0] : '?',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(
                  Icons.favorite,
                  color: Color(0xFFF4436C),
                ),
                const SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: const Color(0xFFF4436C),
                  radius: 24,
                  child: Text(
                    _user!.partner2Name.isNotEmpty ? _user!.partner2Name[0] : '?',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.settings),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const SettingsScreen()),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Welcome back, ${_user!.partner1Name} & ${_user!.partner2Name}!',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              progressText,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentChallengeCard() {
    if (_currentChallenge == null) {
      return Card(
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'No Active Challenge',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Generate a new challenge to start reconnecting!',
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _generateNewChallenge,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: const Text('Generate Challenge'),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      color: _getCategoryColor(_currentChallenge!.category).withOpacity(0.1),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ChallengeScreen(
                initialChallenge: _currentChallenge,
              ),
            ),
          );
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Chip(
                    label: Text(
                      _currentChallenge!.category,
                      style: TextStyle(
                        color: _getCategoryColor(_currentChallenge!.category),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    backgroundColor: _getCategoryColor(_currentChallenge!.category).withOpacity(0.2),
                  ),
                  Text(
                    '~${_currentChallenge!.timeRequired} min',
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                _currentChallenge!.title,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _currentChallenge!.description,
                style: const TextStyle(fontSize: 16),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  OutlinedButton(
                    onPressed: _generateNewChallenge,
                    child: const Text('Try Another'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ChallengeScreen(
                            initialChallenge: _currentChallenge,
                          ),
                        ),
                      );
                    },
                    child: const Text('View Details'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickStatsCard() {
    final progress = _user?.progress;
    
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quick Stats',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(
                  icon: Icons.star,
                  value: '${progress?.totalCompleted ?? 0}',
                  label: 'Completed',
                  color: const Color(0xFF533278),
                ),
                _buildStatItem(
                  icon: Icons.local_fire_department,
                  value: '${progress?.streak ?? 0}',
                  label: 'Streak',
                  color: Colors.orange,
                ),
                _buildStatItem(
                  icon: Icons.favorite,
                  value: '${progress?.sparkLevel.toStringAsFixed(1) ?? 0}%',
                  label: 'Spark',
                  color: const Color(0xFFF4436C),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {
                  setState(() {
                    _currentIndex = 2; // Switch to Progress tab
                  });
                },
                child: const Text('View Detailed Progress'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            icon,
            color: color,
            size: 28,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Colors.black54,
          ),
        ),
      ],
    );
  }

  Widget _buildCategoriesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Explore Categories',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          children: [
            _buildCategoryCard(
              title: 'Communication',
              icon: Icons.chat_bubble_outline,
              color: Colors.blue,
              category: 'Communication Boosters',
            ),
            _buildCategoryCard(
              title: 'Physical Touch',
              icon: Icons.volunteer_activism,
              color: Colors.green,
              category: 'Physical Touch & Affection',
            ),
            _buildCategoryCard(
              title: 'Date Night',
              icon: Icons.restaurant,
              color: Colors.purple,
              category: 'Creative Date Night Ideas',
            ),
            _buildCategoryCard(
              title: 'Intimacy',
              icon: Icons.favorite,
              color: Colors.red,
              category: 'Sexual Exploration',
            ),
            _buildCategoryCard(
              title: 'Emotional',
              icon: Icons.psychology,
              color: Colors.orange,
              category: 'Emotional Connection',
            ),
            _buildCategoryCard(
              title: 'Learn More',
              icon: Icons.school,
              color: Colors.teal,
              onTap: () {
                setState(() {
                  _currentIndex = 3; // Switch to Education tab
                });
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCategoryCard({
    required String title,
    required IconData icon,
    required Color color,
    String? category,
    VoidCallback? onTap,
  }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap ?? () {
          if (category != null) {
            _generateChallengeByCategory(category);
          }
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 28,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _generateChallengeByCategory(String category) async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final challenge = await apiService.generateChallenge(category: category);
      
      if (mounted) {
        setState(() {
          _currentChallenge = challenge;
          _isLoading = false;
        });
        
        // Scroll to challenge card
        if (_currentChallenge != null) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ChallengeScreen(
                initialChallenge: _currentChallenge,
              ),
            ),
          );
        }
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
        title: const Text('PlayLove Spark'),
        backgroundColor: const Color(0xFF533278),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: _buildBody(),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFFF4436C).withOpacity(0.2),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: Color(0xFFF4436C)),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.local_fire_department_outlined),
            selectedIcon: Icon(Icons.local_fire_department, color: Color(0xFFF4436C)),
            label: 'Challenges',
          ),
          NavigationDestination(
            icon: Icon(Icons.insights_outlined),
            selectedIcon: Icon(Icons.insights, color: Color(0xFFF4436C)),
            label: 'Progress',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book, color: Color(0xFFF4436C)),
            label: 'Learn',
          ),
          NavigationDestination(
            icon: Icon(Icons.shopping_bag_outlined),
            selectedIcon: Icon(Icons.shopping_bag, color: Color(0xFFF4436C)),
            label: 'Shop',
          ),
        ],
      ),
    );
  }
}