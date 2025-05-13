import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class ArticleDetailScreen extends StatefulWidget {
  final String articleId;

  const ArticleDetailScreen({
    super.key,
    required this.articleId,
  });

  @override
  State<ArticleDetailScreen> createState() => _ArticleDetailScreenState();
}

class _ArticleDetailScreenState extends State<ArticleDetailScreen> {
  bool _isLoading = true;
  dynamic _article;

  @override
  void initState() {
    super.initState();
    _loadArticle();
  }

  Future<void> _loadArticle() async {
    setState(() {
      _isLoading = true;
    });

    final apiService = Provider.of<APIService>(context, listen: false);
    
    try {
      final article = await apiService.getArticleById(widget.articleId);
      
      if (mounted) {
        setState(() {
          _article = article;
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
            content: Text('Error loading article: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _article == null
              ? _buildArticleNotFound()
              : _buildArticleContent(),
    );
  }

  Widget _buildArticleNotFound() {
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
            'Article not found',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'The article you requested could not be found',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF4436C),
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
            child: const Text('Go Back'),
          ),
        ],
      ),
    );
  }

  Widget _buildArticleContent() {
    final title = _article['title'] ?? 'Untitled Article';
    final content = _article['content'] ?? 'No content available';
    final author = _article['author'] ?? 'PlayLove Spark Team';
    final category = _article['category'] ?? 'Uncategorized';
    final imageUrl = _article['image_url'];
    final readTime = _article['read_time'] ?? 5;
    final date = _article['published_date'] != null 
        ? DateTime.parse(_article['published_date']) 
        : null;
    
    return CustomScrollView(
      slivers: [
        // App Bar
        SliverAppBar(
          expandedHeight: 200,
          pinned: true,
          flexibleSpace: FlexibleSpaceBar(
            title: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            background: Stack(
              fit: StackFit.expand,
              children: [
                // Article image or placeholder
                if (imageUrl != null)
                  Image.network(
                    imageUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: _getCategoryColor(category),
                        child: Center(
                          child: Icon(
                            _getCategoryIcon(category),
                            size: 64,
                            color: Colors.white.withOpacity(0.5),
                          ),
                        ),
                      );
                    },
                  )
                else
                  Container(
                    color: _getCategoryColor(category),
                    child: Center(
                      child: Icon(
                        _getCategoryIcon(category),
                        size: 64,
                        color: Colors.white.withOpacity(0.5),
                      ),
                    ),
                  ),
                  
                // Gradient overlay
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.black.withOpacity(0.7),
                      ],
                      stops: const [0.5, 1.0],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        
        // Article content
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Metadata row
                Row(
                  children: [
                    // Category chip
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
                    const Spacer(),
                    
                    // Read time
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
                const SizedBox(height: 16),
                
                // Title
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                
                // Author and date
                Row(
                  children: [
                    Text(
                      'By $author',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    ),
                    if (date != null) ...[
                      const SizedBox(width: 8),
                      const Text(
                        '•',
                        style: TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${date.day}/${date.month}/${date.year}',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 24),
                
                // Divider
                const Divider(),
                const SizedBox(height: 16),
                
                // Content
                Text(
                  content,
                  style: const TextStyle(
                    fontSize: 16,
                    height: 1.6,
                  ),
                ),
                const SizedBox(height: 32),
                
                // Related articles section would go here
                
                // Share button
                Align(
                  alignment: Alignment.center,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // Implement share functionality
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Share functionality coming soon!'),
                        ),
                      );
                    },
                    icon: const Icon(Icons.share),
                    label: const Text('Share Article'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF533278),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 48),
              ],
            ),
          ),
        ),
      ],
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