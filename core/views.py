from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count
import json
import calendar
import datetime
import random

from core.models import (
    User, UserProgress, CompletedChallenge, UserBadge, 
    ViewedArticle, ViewedProduct, CurrentChallenge
)
from core.forms import UserProfileForm
from data.challenges import get_challenge_by_id, get_challenge_by_category, get_challenges_by_category, get_random_challenge
from data.education import get_all_articles, get_article_by_id, get_articles_by_category
from data.products import get_all_products, get_product_by_id, get_products_by_category

# Helper functions
def create_user_progress(user):
    """Create progress record for a new user"""
    return UserProgress.objects.create(user=user)

def get_session_user_id(request):
    """Get the user ID from the session"""
    return request.session.get('user_id')

def get_or_create_user_from_session(request):
    """Get the user from the session, or return None"""
    user_id = get_session_user_id(request)
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Clear invalid session
            if 'user_id' in request.session:
                del request.session['user_id']
    return None

def check_for_badges(user):
    """Check and award new badges based on progress"""
    # Get existing badges
    existing_badges = list(user.badges.values_list('badge_name', flat=True))
    
    # Get user progress
    progress = user.progress
    
    # Get completed challenges count
    completed_count = user.completed_challenges.count()
    
    # Challenge completion badges
    if completed_count >= 1 and "First Spark" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="First Spark")
    if completed_count >= 5 and "Flame Starter" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="Flame Starter")
    if completed_count >= 10 and "Burning Bright" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="Burning Bright")
    if completed_count >= 25 and "Inferno" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="Inferno")
    
    # Streak badges
    if progress.streak >= 3 and "3 Day Streak" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="3 Day Streak")
    if progress.streak >= 7 and "1 Week Connection" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="1 Week Connection")
    if progress.streak >= 14 and "2 Week Devotion" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="2 Week Devotion")
    if progress.streak >= 30 and "Monthly Passion" not in existing_badges:
        UserBadge.objects.create(user=user, badge_name="Monthly Passion")

def get_calendar_data(user):
    """Get calendar data for progress visualization"""
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    # Get the calendar for the current month
    cal = calendar.monthcalendar(current_year, current_month)
    
    # Get completed challenges for this month
    completed_days = user.completed_challenges.filter(
        completed_at__year=current_year,
        completed_at__month=current_month
    ).values('completed_at__day').distinct()
    
    completed_day_numbers = [day['completed_at__day'] for day in completed_days]
    
    # Create calendar days data
    calendar_days = []
    for week in cal:
        for day in week:
            if day == 0:
                calendar_days.append({"number": 0, "active": False})
            else:
                calendar_days.append({
                    "number": day, 
                    "active": day in completed_day_numbers
                })
    
    return {
        "current_month_name": calendar.month_name[current_month],
        "current_year": current_year,
        "calendar_days": calendar_days
    }

def get_category_stats(user):
    """Get statistics on category completion percentages"""
    categories = [
        "Communication Boosters", "Physical Touch & Affection", 
        "Creative Date Night Ideas", "Sexual Exploration", "Emotional Connection"
    ]
    
    # Get completed challenges by category
    completed_by_category = {}
    for category in categories:
        # We would need to determine total challenges per category
        # For now, let's assume 20 challenges per category
        total_per_category = 20
        completed_count = user.completed_challenges.filter(category=category).count()
        percent = round((completed_count / total_per_category) * 100) if total_per_category > 0 else 0
        
        completed_by_category[category] = {
            "name": category,
            "count": completed_count,
            "total": total_per_category,
            "percent": percent
        }
    
    return list(completed_by_category.values())

def generate_challenge_for_user(user, category=None, challenge_id=None):
    """
    Generate a new challenge for a user.
    Uses a hybrid approach combining static challenges with AI-generated ones.
    """
    from utils.challenge_provider import get_hybrid_challenge, schedule_batch_generation
    
    # Get completed challenge IDs
    completed_ids = list(user.completed_challenges.values_list('challenge_id', flat=True))
    
    # Prepare user profile data for the challenge generator
    user_profile = {
        'partner1_name': user.partner1_name,
        'partner2_name': user.partner2_name,
        'relationship_status': user.relationship_status,
        'relationship_duration': user.relationship_duration,
        'preferred_categories': user.preferred_categories,
        'excluded_categories': user.excluded_categories,
        'streak': getattr(user.progress, 'streak', 0),
        'total_completed': getattr(user.progress, 'total_completed', 0)
    }
    
    # Smart category selection if none specified
    if not category and not challenge_id:
        # Get user preferences
        preferred_categories = user.preferred_categories
        excluded_categories = user.excluded_categories
        
        # Default categories if none specified
        all_categories = [
            "Communication Boosters", "Physical Touch & Affection", 
            "Creative Date Night Ideas", "Sexual Exploration", "Emotional Connection"
        ]
        
        # Remove excluded categories
        available_categories = [c for c in all_categories if c not in excluded_categories]
        
        # Filter to preferred categories if specified, otherwise use all available
        if preferred_categories:
            available_categories = [c for c in preferred_categories if c in available_categories]
        
        if not available_categories:
            # Fallback if no categories are available
            available_categories = all_categories
            
        # Calculate category weights based on completion history
        category_weights = {}
        
        # Count completed challenges per category
        completed_by_category = {}
        for cat in available_categories:
            count = user.completed_challenges.filter(category=cat).count()
            completed_by_category[cat] = count
        
        # If there's completion history, use it to calculate weights
        if sum(completed_by_category.values()) > 0:
            # Invert counts to prioritize less-used categories
            total_completions = sum(completed_by_category.values())
            for cat in available_categories:
                # Calculate inverse weight (less completed = higher weight)
                inverse_weight = 1 - (completed_by_category.get(cat, 0) / total_completions) if total_completions > 0 else 1
                # Add some randomness but keep the weighting
                category_weights[cat] = inverse_weight + random.random() * 0.2
        else:
            # If no history, use equal weights with slight randomness
            for cat in available_categories:
                category_weights[cat] = 1 + random.random() * 0.2
                
        # Select category based on weights
        cats = list(category_weights.keys())
        weights = list(category_weights.values())
        
        if cats:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w/total_weight for w in weights]
            
            try:
                # Use weighted random choice to select category
                category = random.choices(cats, weights=normalized_weights, k=1)[0]
            except ValueError:
                # Fallback to simple random if weighting fails
                category = random.choice(cats)
    
    # Get a challenge using our hybrid generator
    challenge = get_hybrid_challenge(user_profile, completed_ids, category, challenge_id)
    
    # Schedule background generation of challenges to pre-fill cache
    # This is a non-blocking operation
    try:
        schedule_batch_generation(user_profile)
    except Exception as e:
        # Log error but don't disrupt the user experience
        print(f"Error scheduling batch generation: {str(e)}")
    
    # Update or create current challenge
    if challenge:
        try:
            current = CurrentChallenge.objects.get(user=user)
            current.challenge_id = challenge['id']
            current.category = challenge['category']
            current.generated_at = timezone.now()
            current.save()
        except CurrentChallenge.DoesNotExist:
            CurrentChallenge.objects.create(
                user=user,
                challenge_id=challenge['id'],
                category=challenge['category']
            )
    
    return challenge

def prepare_context_for_user(request, user=None):
    """Prepare the common context for templates"""
    user = user or get_or_create_user_from_session(request)
    context = {}
    
    if user:
        # Get user profile data
        context['user_profile'] = {
            'initialized': True,
            'partner1_name': user.partner1_name,
            'partner2_name': user.partner2_name,
            'relationship_status': user.relationship_status,
            'relationship_duration': user.relationship_duration,
            'challenge_frequency': user.challenge_frequency,
            'preferred_categories': user.preferred_categories,
            'excluded_categories': user.excluded_categories
        }
        
        # Get user progress
        try:
            progress = user.progress
            
            # Prepare badges for display
            badges = list(user.badges.values_list('badge_name', flat=True))
            
            # Prepare progress data
            context['user_progress'] = {
                'streak': progress.streak,
                'spark_level': progress.spark_level,
                'total_completed': progress.total_completed,
                'badges': badges,
                'last_completed': progress.last_completed
            }
        except UserProgress.DoesNotExist:
            # Create progress if it doesn't exist
            progress = create_user_progress(user)
            context['user_progress'] = {
                'streak': 0,
                'spark_level': 10,
                'total_completed': 0,
                'badges': [],
                'last_completed': None
            }
        
        # Get current challenge
        try:
            current = CurrentChallenge.objects.get(user=user)
            challenge = get_challenge_by_id(current.challenge_id)
            
            if challenge:
                # Add extra metadata for template display
                challenge['generated_at'] = current.generated_at
                
                # Add personalized names to challenge description
                description = challenge.get('description', '')
                if '{partner1}' in description:
                    description = description.replace('{partner1}', user.partner1_name)
                if '{partner2}' in description:
                    description = description.replace('{partner2}', user.partner2_name)
                challenge['description'] = description
                
                # Add difficulty display
                difficulty = challenge.get('difficulty', 'medium')
                if difficulty.lower() == 'easy':
                    challenge['difficulty_display'] = 'Easy'
                    challenge['difficulty_class'] = 'text-success'
                elif difficulty.lower() == 'medium':
                    challenge['difficulty_display'] = 'Medium'
                    challenge['difficulty_class'] = 'text-primary'
                elif difficulty.lower() == 'hard':
                    challenge['difficulty_display'] = 'Challenging'
                    challenge['difficulty_class'] = 'text-danger'
                else:
                    challenge['difficulty_display'] = 'Medium'
                    challenge['difficulty_class'] = 'text-primary'
            
            context['current_challenge'] = challenge
        except CurrentChallenge.DoesNotExist:
            context['current_challenge'] = None
        
        # Get completed challenges
        completed = user.completed_challenges.order_by('-completed_at')[:5]
        context['completed_challenges'] = completed
        
        # Get viewed articles and products
        context['viewed_articles'] = list(user.viewed_articles.values_list('article_id', flat=True))
        context['viewed_products'] = list(user.viewed_products.values_list('product_id', flat=True))
    else:
        # No user in session, show registration form
        context['user_profile'] = {'initialized': False}
        context['form'] = UserProfileForm()
    
    return context

# View functions
def home(request):
    # Check if this is a form submission for profile creation
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create initial progress record
            create_user_progress(user)
            
            # Generate initial challenge
            generate_challenge_for_user(user)
            
            # Store user ID in session
            request.session['user_id'] = user.id
            
            messages.success(request, 'Your profile has been created successfully!')
            return redirect('home')
        else:
            # Form has errors, display them
            user = None
            context = prepare_context_for_user(request, user)
            context['form'] = form  # Use the form with validation errors
            return render(request, 'home.html', context)
    
    # Normal page load
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    # If no user is found, provide a fresh form
    if not user:
        context['form'] = UserProfileForm()
    
    return render(request, 'home.html', context)

def setup_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create initial progress record
            create_user_progress(user)
            
            # Generate initial challenge
            generate_challenge_for_user(user)
            
            # Store user ID in session
            request.session['user_id'] = user.id
            
            messages.success(request, 'Your profile has been created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form.')
    else:
        form = UserProfileForm()
    
    context = {
        'form': form,
        'user_profile': {'initialized': False}
    }
    return render(request, 'home.html', context)

def update_profile(request):
    user = get_or_create_user_from_session(request)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('settings')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form.')
    else:
        form = UserProfileForm(instance=user)
    
    context = prepare_context_for_user(request, user)
    context['form'] = form
    
    return render(request, 'settings.html', context)

def challenges_view(request):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if user and user.partner1_name:
        # Add challenge categories
        context['categories'] = [
            "Communication Boosters", "Physical Touch & Affection", 
            "Creative Date Night Ideas", "Sexual Exploration", "Emotional Connection"
        ]
        
        # Get all completed challenges
        completed_challenges = user.completed_challenges.order_by('-completed_at')
        
        # Enhance with full challenge details
        enhanced_challenges = []
        for completed in completed_challenges:
            challenge_data = get_challenge_by_id(completed.challenge_id)
            if challenge_data:
                # Combine DB record with challenge details
                challenge_data.update({
                    'id': completed.id,
                    'completed_at': completed.completed_at
                })
                enhanced_challenges.append(challenge_data)
            else:
                # Fallback if challenge details not found
                enhanced_challenges.append({
                    'id': completed.id,
                    'challenge_id': completed.challenge_id,
                    'category': completed.category,
                    'title': 'Challenge',
                    'description': 'Details not available',
                    'difficulty': 'Unknown',
                    'completed_at': completed.completed_at
                })
        
        context['completed_challenges'] = enhanced_challenges
    
    return render(request, 'challenges.html', context)

@require_POST
def complete_challenge(request):
    user = get_or_create_user_from_session(request)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    challenge_id = request.POST.get('challenge_id')
    category = request.POST.get('category')
    
    if not challenge_id or not category:
        messages.error(request, 'Invalid request. Challenge ID and category are required.')
        return redirect('challenges')
    
    # Check if challenge already completed
    if not CompletedChallenge.objects.filter(user=user, challenge_id=challenge_id).exists():
        # Mark challenge as completed
        CompletedChallenge.objects.create(
            user=user,
            challenge_id=challenge_id,
            category=category
        )
        
        # Update progress
        progress = user.progress
        progress.total_completed += 1
        
        # Update last completed date
        today = timezone.now()
        
        # Update streak
        if progress.last_completed:
            yesterday = (today - datetime.timedelta(days=1)).date()
            if progress.last_completed.date() == yesterday:
                progress.streak += 1
            elif progress.last_completed.date() != today.date():
                progress.streak = 1
        else:
            progress.streak = 1
            
        progress.last_completed = today
        
        # Update spark level (max 100%)
        progress.spark_level = min(progress.spark_level + 5, 100)
        progress.save()
        
        # Check for badges
        check_for_badges(user)
        
        # Generate new challenge
        generate_challenge_for_user(user)
        
        messages.success(request, 'Challenge completed! Your progress has been updated.')
    else:
        messages.info(request, 'You have already completed this challenge.')
    
    return redirect('challenges')

@require_POST
def generate_challenge(request):
    user = get_or_create_user_from_session(request)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    category = request.POST.get('category')
    challenge_id = request.POST.get('challenge_id')
    
    challenge = generate_challenge_for_user(user, category, challenge_id)
    
    if challenge:
        messages.success(request, 'New challenge generated!')
    else:
        messages.warning(request, 'Could not generate a new challenge. You may have completed all available challenges in this category.')
    
    # Redirect back to referring page
    referer = request.META.get('HTTP_REFERER')
    if referer and 'challenges' in referer:
        return redirect('challenges')
    else:
        return redirect('home')

def progress_view(request):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if user and user.partner1_name:
        # Add calendar data
        calendar_data = get_calendar_data(user)
        context.update(calendar_data)
        
        # Add category stats
        context['category_stats'] = get_category_stats(user)
    
    return render(request, 'progress.html', context)

def education_view(request):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if user and user.partner1_name:
        # Get all articles
        articles = get_all_articles()
        context['articles'] = articles
        
        # Get categories and articles by category
        categories = set(article['category'] for article in articles)
        articles_by_category = {}
        
        for category in categories:
            articles_by_category[category] = get_articles_by_category(category)
        
        context['categories'] = categories
        context['articles_by_category'] = articles_by_category
    
    return render(request, 'education.html', context)

def article_detail(request, article_id):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    # Get article
    article = get_article_by_id(article_id)
    if not article:
        messages.error(request, 'Article not found.')
        return redirect('education')
    
    context['article'] = article
    
    # Mark as viewed
    if not ViewedArticle.objects.filter(user=user, article_id=article_id).exists():
        ViewedArticle.objects.create(user=user, article_id=article_id)
    
    # Get related articles in same category
    related_articles = get_articles_by_category(article['category'])
    context['related_articles'] = [a for a in related_articles if a['id'] != article_id][:4]
    
    # Get related challenges
    related_challenges = get_challenges_by_category(article['category'])[:3]
    context['related_challenges'] = related_challenges
    
    return render(request, 'article_detail.html', context)

def products_view(request):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if user and user.partner1_name:
        # Get all products
        products = get_all_products()
        
        # Add star ratings for display
        for product in products:
            if 'rating' in product:
                rating = product['rating']
                product['rating_stars'] = range(int(rating))
                product['rating_empty_stars'] = range(5 - int(rating))
        
        context['products'] = products
        
        # Get categories and products by category
        categories = set(product['category'] for product in products)
        products_by_category = {}
        
        for category in categories:
            category_products = get_products_by_category(category)
            
            # Add star ratings
            for product in category_products:
                if 'rating' in product:
                    rating = product['rating']
                    product['rating_stars'] = range(int(rating))
                    product['rating_empty_stars'] = range(5 - int(rating))
            
            products_by_category[category] = category_products
        
        context['categories'] = categories
        context['products_by_category'] = products_by_category
    
    return render(request, 'products.html', context)

def product_detail(request, product_id):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    # Get product
    product = get_product_by_id(product_id)
    if not product:
        messages.error(request, 'Product not found.')
        return redirect('products')
    
    # Add star ratings
    if 'rating' in product:
        rating = product['rating']
        product['rating_stars'] = range(int(rating))
        product['rating_empty_stars'] = range(5 - int(rating))
    
    context['product'] = product
    
    # Mark as viewed
    if not ViewedProduct.objects.filter(user=user, product_id=product_id).exists():
        ViewedProduct.objects.create(user=user, product_id=product_id)
    
    # Get related products in same category
    related_products = get_products_by_category(product['category'])
    
    # Add star ratings to related products
    for related in related_products:
        if 'rating' in related:
            rating = related['rating']
            related['rating_stars'] = range(int(rating))
            related['rating_empty_stars'] = range(5 - int(rating))
    
    context['related_products'] = [p for p in related_products if p['id'] != product_id][:4]
    
    return render(request, 'product_detail.html', context)

def settings_view(request):
    user = get_or_create_user_from_session(request)
    context = prepare_context_for_user(request, user)
    
    if user and user.partner1_name:
        form = UserProfileForm(instance=user)
        context['form'] = form
    
    return render(request, 'settings.html', context)

@require_POST
def reset_progress(request):
    user = get_or_create_user_from_session(request)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    # Delete completed challenges
    user.completed_challenges.all().delete()
    
    # Delete badges
    user.badges.all().delete()
    
    # Delete current challenge
    CurrentChallenge.objects.filter(user=user).delete()
    
    # Reset progress
    progress = user.progress
    progress.streak = 0
    progress.last_completed = None
    progress.spark_level = 10
    progress.total_completed = 0
    progress.save()
    
    # Generate new challenge
    generate_challenge_for_user(user)
    
    messages.success(request, 'Your progress has been reset successfully.')
    return redirect('settings')

def export_data(request):
    user = get_or_create_user_from_session(request)
    
    if not user:
        messages.error(request, 'No user profile found. Please create one first.')
        return redirect('home')
    
    # Prepare export data
    export_data = {
        "user_profile": {
            "partner1_name": user.partner1_name,
            "partner2_name": user.partner2_name,
            "relationship_status": user.relationship_status,
            "relationship_duration": user.relationship_duration,
            "challenge_frequency": user.challenge_frequency,
            "preferred_categories": user.preferred_categories,
            "excluded_categories": user.excluded_categories
        },
        "progress": {
            "streak": user.progress.streak,
            "total_completed": user.progress.total_completed,
            "spark_level": user.progress.spark_level
        },
        "completed_challenges": [
            {
                "challenge_id": cc.challenge_id,
                "category": cc.category,
                "completed_at": cc.completed_at.isoformat()
            } for cc in user.completed_challenges.all()
        ],
        "badges": [
            {
                "badge_name": badge.badge_name,
                "earned_at": badge.earned_at.isoformat()
            } for badge in user.badges.all()
        ],
        "export_date": timezone.now().isoformat()
    }
    
    # Create JSON response
    response = HttpResponse(json.dumps(export_data, indent=4), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="playlove_spark_data_{user.id}.json"'
    
    return response