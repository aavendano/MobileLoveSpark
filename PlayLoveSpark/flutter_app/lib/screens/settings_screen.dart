import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'onboarding_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isLoading = true;
  User? _user;
  
  final _formKey = GlobalKey<FormState>();
  final _partner1Controller = TextEditingController();
  final _partner2Controller = TextEditingController();
  String _challengeFrequency = 'daily';

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  @override
  void dispose() {
    _partner1Controller.dispose();
    _partner2Controller.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final user = await apiService.getUserProfile();
      
      if (mounted) {
        setState(() {
          _user = user;
          
          // Initialize form controllers
          if (user != null) {
            _partner1Controller.text = user.partner1Name;
            _partner2Controller.text = user.partner2Name;
            _challengeFrequency = user.challengeFrequency;
          }
          
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
            content: Text('Error loading user data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _updateUserProfile() async {
    if (!_formKey.currentState!.validate() || _user == null) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      // Update user model with form data
      final updatedUser = _user!.copyWith(
        partner1Name: _partner1Controller.text,
        partner2Name: _partner2Controller.text,
        challengeFrequency: _challengeFrequency,
      );
      
      // Update user profile
      final result = await apiService.updateUserProfile(updatedUser);
      
      if (mounted) {
        setState(() {
          _isLoading = false;
          if (result != null) {
            _user = result;
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Profile updated successfully'),
                backgroundColor: Colors.green,
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Failed to update profile'),
                backgroundColor: Colors.red,
              ),
            );
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error updating profile: $e'),
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
    
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const OnboardingScreen()),
      (Route<dynamic> route) => false,
    );
  }

  Future<void> _showLogoutConfirmation() async {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Confirm Logout'),
          content: const SingleChildScrollView(
            child: Text(
              'Are you sure you want to log out? You will need to set up your profile again to access your data.',
            ),
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('Cancel'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text(
                'Logout',
                style: TextStyle(color: Colors.red),
              ),
              onPressed: () {
                Navigator.of(context).pop();
                _logout();
              },
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: const Color(0xFF533278),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _user == null
              ? _buildNoUserData()
              : _buildSettingsForm(),
    );
  }

  Widget _buildNoUserData() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'Error loading user data',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Please try again later',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadUserData,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF4436C),
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsForm() {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Profile section
          const Text(
            'Profile Settings',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          
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
          const SizedBox(height: 24),
          
          // Challenge frequency
          const Text(
            'Challenge Frequency',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          
          // Daily option
          RadioListTile<String>(
            title: const Text('Daily'),
            subtitle: const Text('A new challenge every day'),
            value: 'daily',
            groupValue: _challengeFrequency,
            activeColor: const Color(0xFFF4436C),
            onChanged: (value) {
              setState(() {
                _challengeFrequency = value ?? 'daily';
              });
            },
          ),
          
          // Weekly option
          RadioListTile<String>(
            title: const Text('Weekly'),
            subtitle: const Text('One challenge per week'),
            value: 'weekly',
            groupValue: _challengeFrequency,
            activeColor: const Color(0xFFF4436C),
            onChanged: (value) {
              setState(() {
                _challengeFrequency = value ?? 'weekly';
              });
            },
          ),
          
          // Twice a week option
          RadioListTile<String>(
            title: const Text('Twice a Week'),
            subtitle: const Text('Two challenges per week'),
            value: 'biweekly',
            groupValue: _challengeFrequency,
            activeColor: const Color(0xFFF4436C),
            onChanged: (value) {
              setState(() {
                _challengeFrequency = value ?? 'biweekly';
              });
            },
          ),
          
          const SizedBox(height: 24),
          
          // Update button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _updateUserProfile,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFF4436C),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Update Profile'),
            ),
          ),
          
          const SizedBox(height: 48),
          const Divider(),
          const SizedBox(height: 16),
          
          // App info
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About PlayLove Spark'),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'PlayLove Spark',
                applicationVersion: '1.0.0',
                applicationIcon: const FlutterLogo(size: 32),
                applicationLegalese:
                    '© 2025 PlayLoveToys. All rights reserved.',
                children: [
                  const SizedBox(height: 24),
                  const Text(
                    'PlayLove Spark helps couples reignite their relationship through personalized challenges and activities.',
                  ),
                ],
              );
            },
          ),
          
          // Notifications
          ListTile(
            leading: const Icon(Icons.notifications_outlined),
            title: const Text('Notification Settings'),
            onTap: () {
              // This would navigate to notification settings
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Notification settings coming soon'),
                ),
              );
            },
          ),
          
          // Privacy Policy
          ListTile(
            leading: const Icon(Icons.privacy_tip_outlined),
            title: const Text('Privacy Policy'),
            onTap: () {
              // This would show privacy policy
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Privacy policy coming soon'),
                ),
              );
            },
          ),
          
          // Logout
          ListTile(
            leading: const Icon(
              Icons.logout,
              color: Colors.red,
            ),
            title: const Text(
              'Logout',
              style: TextStyle(color: Colors.red),
            ),
            onTap: _showLogoutConfirmation,
          ),
          
          const SizedBox(height: 24),
          const Center(
            child: Text(
              'PlayLove Spark v1.0.0',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}