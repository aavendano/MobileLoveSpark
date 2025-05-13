from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'progress', views.UserProgressViewSet)
router.register(r'completed-challenges', views.CompletedChallengeViewSet)
router.register(r'badges', views.UserBadgeViewSet)
router.register(r'viewed-articles', views.ViewedArticleViewSet)
router.register(r'viewed-products', views.ViewedProductViewSet)
router.register(r'current-challenges', views.CurrentChallengeViewSet)

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Custom API routes
    path('users-with-progress/', views.UserWithProgressView.as_view(), name='users-with-progress'),
    path('users-with-progress/<int:pk>/', views.UserWithProgressView.as_view(), name='user-with-progress-detail'),
    path('users-with-full-data/<int:pk>/', views.UserWithFullDataView.as_view(), name='user-with-full-data'),
    
    # Challenge related endpoints
    path('challenges/', views.get_challenges, name='challenges-list'),
    path('challenges/<str:challenge_id>/', views.get_challenge, name='challenge-detail'),
    path('complete-challenge/', views.complete_challenge_api, name='complete-challenge'),
    path('generate-challenge/', views.generate_challenge_api, name='generate-challenge'),
    
    # Education related endpoints
    path('articles/', views.get_articles, name='articles-list'),
    path('articles/<str:article_id>/', views.get_article, name='article-detail'),
    
    # Product related endpoints
    path('products/', views.get_products, name='products-list'),
    path('products/<str:product_id>/', views.get_product, name='product-detail'),
    
    # API Auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]