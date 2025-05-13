import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../models/user.dart';
import '../models/user_progress.dart';
import '../services/api_service.dart';

class ProgressScreen extends StatefulWidget {
  const ProgressScreen({super.key});

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen> with SingleTickerProviderStateMixin {
  bool _isLoading = true;
  User? _user;
  UserProgress? _progress;
  List<dynamic>? _completedChallenges;
  List<dynamic>? _badges;
  Map<String, int>? _categoryStats;
  
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final user = await apiService.getUserProfile();
      final progress = await apiService.getUserProgress();
      
      if (mounted) {
        setState(() {
          _user = user;
          _progress = progress;
          
          // TODO: Fetch completed challenges and badges once implemented
          _completedChallenges = [];
          _badges = [];
          
          // Calculate category stats
          _calculateCategoryStats();
          
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
            content: Text('Error loading progress: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _calculateCategoryStats() {
    // If completed challenges aren't available, create dummy data
    // This would be replaced with actual category counts from the API
    _categoryStats = {
      'Communication Boosters': 0,
      'Physical Touch & Affection': 0,
      'Creative Date Night Ideas': 0,
      'Sexual Exploration': 0,
      'Emotional Connection': 0,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Progress Tracker'),
        backgroundColor: const Color(0xFF533278),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFFF4436C),
          tabs: const [
            Tab(text: 'Summary'),
            Tab(text: 'Stats'),
            Tab(text: 'Badges'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _progress == null
              ? _buildNoProgress()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildSummaryTab(),
                    _buildStatsTab(),
                    _buildBadgesTab(),
                  ],
                ),
    );
  }

  Widget _buildNoProgress() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.sentiment_neutral,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No progress data available',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height:
            8,
          ),
          const Text(
            'Complete some challenges to start tracking your progress!',
            style: TextStyle(
              color: Colors.grey,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadData,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF4436C),
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
            child: const Text('Refresh'),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryTab() {
    final progress = _progress!;
    
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Streak and Spark Level
            Card(
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
                        Expanded(
                          child: _buildStatBox(
                            icon: Icons.local_fire_department,
                            iconColor: Colors.orange,
                            value: '${progress.streak}',
                            label: 'Day Streak',
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildStatBox(
                            icon: Icons.favorite,
                            iconColor: const Color(0xFFF4436C),
                            value: '${progress.sparkLevel.toStringAsFixed(1)}%',
                            label: 'Spark Level',
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Last Challenge Completed',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      progress.lastCompleted != null
                          ? DateFormat('MMMM d, y').format(progress.lastCompleted!)
                          : 'No challenges completed yet',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Recent Challenges
            const Text(
              'Recent Challenges',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            if (_completedChallenges == null || _completedChallenges!.isEmpty)
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(
                  child: Text(
                    'No challenges completed yet',
                    style: TextStyle(
                      color: Colors.grey,
                    ),
                  ),
                ),
              )
            else
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _completedChallenges!.length > 5 
                      ? 5 
                      : _completedChallenges!.length,
                  separatorBuilder: (context, index) => const Divider(),
                  itemBuilder: (context, index) {
                    final challenge = _completedChallenges![index];
                    return ListTile(
                      title: Text(
                        challenge['title'] ?? 'Challenge ${index + 1}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        challenge['category'] ?? '',
                      ),
                      trailing: Text(
                        challenge['completed_at'] != null
                            ? DateFormat('MMM d').format(
                                DateTime.parse(challenge['completed_at']),
                              )
                            : '',
                        style: const TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                    );
                  },
                ),
              ),
            const SizedBox(height: 24),
            
            // Total Challenges
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF533278).withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.check_circle_outline,
                        color: Color(0xFF533278),
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Total Challenges Completed',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${progress.totalCompleted}',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF533278),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Category Distribution
            const Text(
              'Challenge Categories',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      height: 200,
                      child: _buildCategoryChart(),
                    ),
                    const SizedBox(height: 16),
                    const Center(
                      child: Text(
                        'Challenges completed by category',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Activity Calendar
            const Text(
              'Activity Calendar',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    // This would be replaced with an actual calendar visualization
                    Container(
                      height: 200,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade200,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Center(
                        child: Text(
                          'Calendar Visualization\n(Coming Soon)',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.grey,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Track your consistency over time',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Streak History
            const Text(
              'Streak History',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Card(
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
                        _buildStreakStatItem(
                          label: 'Current',
                          value: '${_progress?.streak ?? 0}',
                        ),
                        const SizedBox(width: 16),
                        _buildStreakStatItem(
                          label: 'Best',
                          value: '14',  // This would come from the API
                        ),
                        const SizedBox(width: 16),
                        _buildStreakStatItem(
                          label: 'Average',
                          value: '5',  // This would come from the API
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBadgesTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: _badges == null || _badges!.isEmpty
          ? _buildNoBadges()
          : GridView.builder(
              padding: const EdgeInsets.all(16.0),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.8,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: _badges!.length,
              itemBuilder: (context, index) {
                final badge = _badges![index];
                return _buildBadgeCard(badge);
              },
            ),
    );
  }

  Widget _buildNoBadges() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.emoji_events_outlined,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No badges earned yet',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 32.0),
            child: Text(
              'Complete challenges to earn badges and track your relationship journey!',
              style: TextStyle(
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBadgeCard(dynamic badge) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF533278).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.emoji_events,
                color: Color(0xFFF4436C),
                size: 36,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              badge['badge_name'] ?? 'Badge',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              badge['earned_at'] != null
                  ? DateFormat('MMM d, y').format(
                      DateTime.parse(badge['earned_at']),
                    )
                  : '',
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatBox({
    required IconData icon,
    required Color iconColor,
    required String value,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: iconColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                color: iconColor,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  color: iconColor,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: iconColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStreakStatItem({
    required String label,
    required String value,
  }) {
    return Expanded(
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF533278),
            ),
          ),
          Text(
            label,
            style: const TextStyle(
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChart() {
    if (_categoryStats == null || _categoryStats!.isEmpty) {
      return const Center(
        child: Text(
          'No category data available',
          style: TextStyle(
            color: Colors.grey,
          ),
        ),
      );
    }

    // Convert to sections for pie chart
    final sections = _categoryStats!.entries.map((entry) {
      final color = _getCategoryColor(entry.key);
      return PieChartSectionData(
        value: entry.value.toDouble(),
        title: entry.value > 0 ? '${entry.value}' : '',
        radius: 50,
        titleStyle: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
        color: color,
      );
    }).toList();

    // If all values are 0, show a placeholder
    final bool allZero = sections.every((section) => section.value == 0);
    
    if (allZero) {
      // Create a placeholder chart
      sections.clear();
      
      // Add a placeholder section
      sections.add(PieChartSectionData(
        value: 1,
        title: '',
        radius: 50,
        color: Colors.grey.shade300,
      ));
    }

    return Column(
      children: [
        SizedBox(
          height: 150,
          child: PieChart(
            PieChartData(
              sections: sections,
              centerSpaceRadius: 40,
              sectionsSpace: 2,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          alignment: WrapAlignment.center,
          children: _categoryStats!.entries.map((entry) {
            final color = _getCategoryColor(entry.key);
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 12,
                  height: 12,
                  color: color,
                ),
                const SizedBox(width: 4),
                Text(
                  _getCategoryShortName(entry.key),
                  style: const TextStyle(
                    fontSize: 12,
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ],
    );
  }

  String _getCategoryShortName(String category) {
    switch (category) {
      case 'Communication Boosters':
        return 'Communication';
      case 'Physical Touch & Affection':
        return 'Physical Touch';
      case 'Creative Date Night Ideas':
        return 'Date Night';
      case 'Sexual Exploration':
        return 'Intimacy';
      case 'Emotional Connection':
        return 'Emotional';
      default:
        return category;
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
}