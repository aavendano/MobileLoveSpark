from django.urls import path
from core import views

urlpatterns = [
    # Home and profile
    path('', views.home, name='home'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Challenges
    path('challenges/', views.challenges_view, name='challenges'),
    path('complete-challenge/', views.complete_challenge, name='complete_challenge'),
    path('generate-challenge/', views.generate_challenge, name='generate_challenge'),
    
    # Progress tracking
    path('progress/', views.progress_view, name='progress'),
    
    # Education
    path('education/', views.education_view, name='education'),
    path('education/article/<str:article_id>/', views.article_detail, name='article_detail'),
    
    # Products
    path('products/', views.products_view, name='products'),
    path('products/detail/<str:product_id>/', views.product_detail, name='product_detail'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('reset-progress/', views.reset_progress, name='reset_progress'),
    path('export-data/', views.export_data, name='export_data'),
]