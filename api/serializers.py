from rest_framework import serializers
from core.models import (
    User, UserProgress, CompletedChallenge, 
    UserBadge, ViewedArticle, ViewedProduct, CurrentChallenge
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'partner1_name', 'partner2_name', 
            'relationship_status', 'relationship_duration', 
            'challenge_frequency', 'preferred_categories', 
            'excluded_categories', 'created_at', 'last_login'
        ]

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'streak', 'last_completed', 'spark_level', 'total_completed']

class CompletedChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedChallenge
        fields = ['id', 'user', 'challenge_id', 'category', 'completed_at']

class UserBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'badge_name', 'earned_at']

class ViewedArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewedArticle
        fields = ['id', 'user', 'article_id', 'viewed_at']

class ViewedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewedProduct
        fields = ['id', 'user', 'product_id', 'viewed_at']

class CurrentChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentChallenge
        fields = ['id', 'user', 'challenge_id', 'category', 'generated_at']

# Nested serializers for comprehensive data retrieval
class UserWithProgressSerializer(serializers.ModelSerializer):
    progress = UserProgressSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'partner1_name', 'partner2_name', 
            'relationship_status', 'relationship_duration', 
            'challenge_frequency', 'preferred_categories', 
            'excluded_categories', 'created_at', 'last_login',
            'progress'
        ]

class UserWithFullDataSerializer(serializers.ModelSerializer):
    progress = UserProgressSerializer(read_only=True)
    completed_challenges = CompletedChallengeSerializer(many=True, read_only=True)
    badges = UserBadgeSerializer(many=True, read_only=True)
    viewed_articles = ViewedArticleSerializer(many=True, read_only=True)
    viewed_products = ViewedProductSerializer(many=True, read_only=True)
    current_challenge = CurrentChallengeSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'partner1_name', 'partner2_name', 
            'relationship_status', 'relationship_duration', 
            'challenge_frequency', 'preferred_categories', 
            'excluded_categories', 'created_at', 'last_login',
            'progress', 'completed_challenges', 'badges', 
            'viewed_articles', 'viewed_products', 'current_challenge'
        ]