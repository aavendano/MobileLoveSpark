from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import (
    User, UserProgress, CompletedChallenge, 
    UserBadge, ViewedArticle, ViewedProduct, CurrentChallenge
)

from .serializers import (
    UserSerializer, UserProgressSerializer, CompletedChallengeSerializer,
    UserBadgeSerializer, ViewedArticleSerializer, ViewedProductSerializer,
    CurrentChallengeSerializer, UserWithProgressSerializer, UserWithFullDataSerializer
)

from data.challenges import get_challenge_by_id, get_challenge_by_category, get_random_challenge
from data.education import get_all_articles, get_article_by_id
from data.products import get_all_products, get_product_by_id

# Model ViewSets for basic CRUD operations
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProgressViewSet(viewsets.ModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer

class CompletedChallengeViewSet(viewsets.ModelViewSet):
    queryset = CompletedChallenge.objects.all()
    serializer_class = CompletedChallengeSerializer

class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.all()
    serializer_class = UserBadgeSerializer

class ViewedArticleViewSet(viewsets.ModelViewSet):
    queryset = ViewedArticle.objects.all()
    serializer_class = ViewedArticleSerializer

class ViewedProductViewSet(viewsets.ModelViewSet):
    queryset = ViewedProduct.objects.all()
    serializer_class = ViewedProductSerializer

class CurrentChallengeViewSet(viewsets.ModelViewSet):
    queryset = CurrentChallenge.objects.all()
    serializer_class = CurrentChallengeSerializer

# Custom API Views for specific application logic
class UserWithProgressView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                user = User.objects.get(pk=pk)
                serializer = UserWithProgressSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.all()
            serializer = UserWithProgressSerializer(users, many=True)
            return Response(serializer.data)

class UserWithFullDataView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                user = User.objects.get(pk=pk)
                serializer = UserWithFullDataSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Please provide a user ID"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_challenges(request):
    """Get challenges from the database"""
    category = request.query_params.get('category', None)
    exclude_ids = request.query_params.getlist('exclude_ids', None)
    
    if category:
        challenge = get_challenge_by_category(category, exclude_ids)
    else:
        challenge = get_random_challenge(exclude_ids)
        
    return Response(challenge)

@api_view(['GET'])
def get_challenge(request, challenge_id):
    """Get a specific challenge by ID"""
    challenge = get_challenge_by_id(challenge_id)
    if challenge:
        return Response(challenge)
    return Response({"error": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def complete_challenge_api(request):
    """Mark a challenge as completed and update progress"""
    user_id = request.data.get('user_id')
    challenge_id = request.data.get('challenge_id')
    category = request.data.get('category')
    
    if not all([user_id, challenge_id, category]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(pk=user_id)
        
        # Create the completed challenge
        completed, created = CompletedChallenge.objects.get_or_create(
            user=user, 
            challenge_id=challenge_id,
            defaults={"category": category}
        )
        
        if not created:
            return Response({"message": "Challenge already completed"})
            
        # Update user progress
        progress, _ = UserProgress.objects.get_or_create(user=user)
        progress.total_completed += 1
        
        # Logic for streak and spark level updates
        # ... (to be implemented based on core.views logic)
        
        progress.save()
        
        # Return the updated progress
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)
        
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_articles(request):
    """Get educational articles"""
    articles = get_all_articles()
    return Response(articles)

@api_view(['GET'])
def get_article(request, article_id):
    """Get a specific article by ID"""
    article = get_article_by_id(article_id)
    if article:
        return Response(article)
    return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_products(request):
    """Get products"""
    products = get_all_products()
    return Response(products)

@api_view(['GET'])
def get_product(request, product_id):
    """Get a specific product by ID"""
    product = get_product_by_id(product_id)
    if product:
        return Response(product)
    return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def generate_challenge_api(request):
    """Generate a new challenge for a user"""
    user_id = request.data.get('user_id')
    category = request.data.get('category', None)
    
    if not user_id:
        return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(pk=user_id)
        
        # Get completed challenge IDs to exclude
        completed_ids = CompletedChallenge.objects.filter(user=user).values_list('challenge_id', flat=True)
        
        # Get a challenge
        if category:
            challenge = get_challenge_by_category(category, exclude_ids=completed_ids)
        else:
            # If no category specified, try to use preferred categories
            preferred = user.preferred_categories
            excluded = user.excluded_categories
            
            if preferred:
                # Get a random preferred category
                import random
                category = random.choice(preferred)
                challenge = get_challenge_by_category(category, exclude_ids=completed_ids)
            else:
                # Get a random challenge, avoiding excluded categories
                challenge = get_random_challenge(exclude_ids=completed_ids)
                
                # Make sure it's not in excluded categories
                attempts = 0
                while challenge.get('category') in excluded and attempts < 10:
                    challenge = get_random_challenge(exclude_ids=completed_ids)
                    attempts += 1
                    
        # Save as current challenge
        current, _ = CurrentChallenge.objects.update_or_create(
            user=user,
            defaults={
                "challenge_id": challenge.get('id'),
                "category": challenge.get('category')
            }
        )
        
        return Response(challenge)
        
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)