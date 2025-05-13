import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import 'article_detail_screen.dart';

class EducationScreen extends StatefulWidget {
  const EducationScreen({super.key});

  @override
  State<EducationScreen> createState() => _EducationScreenState();
}

class _EducationScreenState extends State<EducationScreen> {
  bool _isLoading = true;
  List<dynamic> _articles = [];
  String _selectedCategory = 'All';

  @override
  void initState() {
    super.initState();
    _loadArticles();
  }

  Future<void> _loadArticles() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final articles = await apiService.getArticles();
      
      if (mounted) {
        setState(() {
          _articles = articles;
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
            content: Text('Error loading articles: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  List<dynamic> _getFilteredArticles() {
    if (_selectedCategory == 'All') {
      return _articles;
    }
    
    return _articles.where((article) => 
      article['category'] == _selectedCategory
    ).toList();
  }

  List<String> _getCategories() {
    final Set<String> categories = {'All'};
    
    for (final article in _articles) {
      if (article['category'] != null) {
        categories.add(article['category']);
      }
    }
    
    return categories.toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Learn Together'),
        backgroundColor: const Color(0xFF533278),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildContent(),
    );
  }

  Widget _buildContent() {
    return Column(
      children: [
        // Category filter
        _buildCategoryFilter(),
        
        // Articles list
        Expanded(
          child: _articles.isEmpty
              ? _buildNoArticles()
              : _buildArticlesList(),
        ),
      ],
    );
  }

  Widget _buildCategoryFilter() {
    final categories = _getCategories();
    
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: categories.map((category) {
            final isSelected = category == _selectedCategory;
            
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: ChoiceChip(
                label: Text(category),
                selected: isSelected,
                onSelected: (selected) {
                  if (selected) {
                    setState(() {
                      _selectedCategory = category;
                    });
                  }
                },
                backgroundColor: Colors.grey.shade200,
                selectedColor: const Color(0xFFF4436C).withOpacity(0.2),
                labelStyle: TextStyle(
                  color: isSelected 
                      ? const Color(0xFFF4436C) 
                      : Colors.black87,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildNoArticles() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.menu_book_outlined,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No articles found',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_selectedCategory != 'All')
            Text(
              'No articles in the "$_selectedCategory" category',
              style: const TextStyle(
                color: Colors.grey,
              ),
            )
          else
            const Text(
              'Check back later for new content',
              style: TextStyle(
                color: Colors.grey,
              ),
            ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadArticles,
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

  Widget _buildArticlesList() {
    final filteredArticles = _getFilteredArticles();
    
    if (filteredArticles.isEmpty) {
      return _buildNoArticles();
    }
    
    return RefreshIndicator(
      onRefresh: _loadArticles,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredArticles.length,
        itemBuilder: (context, index) {
          final article = filteredArticles[index];
          return _buildArticleCard(article);
        },
      ),
    );
  }

  Widget _buildArticleCard(dynamic article) {
    final category = article['category'] ?? 'Uncategorized';
    final title = article['title'] ?? 'Untitled Article';
    final summary = article['summary'] ?? 'No summary available';
    final readTime = article['read_time'] ?? 5;
    final imageUrl = article['image_url'];
    
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ArticleDetailScreen(articleId: article['id']),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Article image
            if (imageUrl != null)
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(12),
                ),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.network(
                    imageUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: Colors.grey.shade200,
                        child: const Center(
                          child: Icon(
                            Icons.image_not_supported_outlined,
                            color: Colors.grey,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              )
            else
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(12),
                ),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Container(
                    color: _getCategoryColor(category).withOpacity(0.2),
                    child: Center(
                      child: Icon(
                        _getCategoryIcon(category),
                        size: 48,
                        color: _getCategoryColor(category),
                      ),
                    ),
                  ),
                ),
              ),
            
            // Article content
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Category and read time
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Chip(
                        label: Text(
                          category,
                          style: TextStyle(
                            color: _getCategoryColor(category),
                            fontSize: 12,
                          ),
                        ),
                        backgroundColor: _getCategoryColor(category).withOpacity(0.1),
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      Row(
                        children: [
                          const Icon(
                            Icons.access_time,
                            size: 14,
                            color: Colors.grey,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '$readTime min read',
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  
                  // Title
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  
                  // Summary
                  Text(
                    summary,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.black87,
                    ),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 16),
                  
                  // Read more button
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => ArticleDetailScreen(articleId: article['id']),
                          ),
                        );
                      },
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text('Read More'),
                          SizedBox(width: 4),
                          Icon(
                            Icons.arrow_forward,
                            size: 16,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'communication':
        return Colors.blue;
      case 'physical touch':
        return Colors.green;
      case 'date night':
        return Colors.purple;
      case 'intimacy':
        return Colors.red;
      case 'emotional connection':
        return Colors.orange;
      case 'relationships':
        return const Color(0xFF533278);
      default:
        return Colors.teal;
    }
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'communication':
        return Icons.chat_bubble_outline;
      case 'physical touch':
        return Icons.volunteer_activism;
      case 'date night':
        return Icons.restaurant;
      case 'intimacy':
        return Icons.favorite;
      case 'emotional connection':
        return Icons.psychology;
      case 'relationships':
        return Icons.people_outline;
      default:
        return Icons.menu_book_outlined;
    }
  }
}