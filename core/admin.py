from django.contrib import admin
from core.models import (
    User, UserProgress, CompletedChallenge, UserBadge, 
    ViewedArticle, ViewedProduct, CurrentChallenge
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner1_name', 'partner2_name', 'relationship_status', 'challenge_frequency')
    search_fields = ('partner1_name', 'partner2_name')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'streak', 'spark_level', 'total_completed', 'last_completed')
    search_fields = ('user__partner1_name', 'user__partner2_name')

@admin.register(CompletedChallenge)
class CompletedChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge_id', 'category', 'completed_at')
    list_filter = ('category', 'completed_at')
    search_fields = ('user__partner1_name', 'user__partner2_name', 'challenge_id')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_name', 'earned_at')
    list_filter = ('badge_name', 'earned_at')
    search_fields = ('user__partner1_name', 'user__partner2_name', 'badge_name')

@admin.register(ViewedArticle)
class ViewedArticleAdmin(admin.ModelAdmin):
    list_display = ('user', 'article_id', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__partner1_name', 'user__partner2_name', 'article_id')

@admin.register(ViewedProduct)
class ViewedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_id', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__partner1_name', 'user__partner2_name', 'product_id')

@admin.register(CurrentChallenge)
class CurrentChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge_id', 'category', 'generated_at')
    list_filter = ('category', 'generated_at')
    search_fields = ('user__partner1_name', 'user__partner2_name', 'challenge_id')