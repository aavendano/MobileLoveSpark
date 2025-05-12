from django.db import models
from django.utils import timezone
import json

class User(models.Model):
    """User profile information"""
    partner1_name = models.CharField(max_length=100)
    partner2_name = models.CharField(max_length=100)
    relationship_status = models.CharField(max_length=50)
    relationship_duration = models.CharField(max_length=50)
    challenge_frequency = models.CharField(max_length=20, default="daily")
    preferred_categories = models.JSONField(default=list)
    excluded_categories = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.partner1_name} & {self.partner2_name}"

class UserProgress(models.Model):
    """User progress tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    streak = models.IntegerField(default=0)
    last_completed = models.DateTimeField(null=True, blank=True)
    spark_level = models.FloatField(default=10.0)
    total_completed = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user} - Level: {self.spark_level}"

class CompletedChallenge(models.Model):
    """Challenges completed by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_challenges')
    challenge_id = models.CharField(max_length=50)  # From the static challenge data
    category = models.CharField(max_length=100)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'challenge_id']
    
    def __str__(self):
        return f"{self.user} - {self.challenge_id}"

class UserBadge(models.Model):
    """Badges earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_name = models.CharField(max_length=100)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge_name']
    
    def __str__(self):
        return f"{self.user} - {self.badge_name}"

class ViewedArticle(models.Model):
    """Articles viewed by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_articles')
    article_id = models.CharField(max_length=50)  # From the static article data
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'article_id']
    
    def __str__(self):
        return f"{self.user} - {self.article_id}"

class ViewedProduct(models.Model):
    """Products viewed by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_products')
    product_id = models.CharField(max_length=50)  # From the static product data
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product_id']
    
    def __str__(self):
        return f"{self.user} - {self.product_id}"

class CurrentChallenge(models.Model):
    """Currently active challenge for a user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='current_challenge')
    challenge_id = models.CharField(max_length=50)  # From the static challenge data
    category = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.challenge_id}"