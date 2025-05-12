"""
Challenge provider utility that combines static challenges with AI-generated ones.
Uses a hybrid approach to minimize AI API calls while providing varied challenges.
"""

import os
import random
from typing import Dict, List, Optional, Any

from data.challenges import get_challenge_by_id, get_challenge_by_category, get_random_challenge
from utils.ai_generator import generate_ai_challenge, should_use_ai, batch_generate_challenges

# Flag to enable/disable AI generation (for testing or if API key unavailable)
from utils.ai_generator import AI_AVAILABLE
AI_ENABLED = AI_AVAILABLE

def get_hybrid_challenge(user_profile: Dict[str, Any], completed_challenges: List[str],
                        category: Optional[str] = None, challenge_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a challenge using the hybrid approach:
    1. If specific challenge ID requested, return that challenge
    2. If AI should be used (based on criteria), generate AI challenge
    3. Otherwise, use pre-defined challenges
    
    This minimizes API calls while still providing personalized content.
    """
    # If a specific challenge ID was requested
    if challenge_id:
        # Check if it's an AI challenge ID (starts with 'ai_')
        if challenge_id.startswith('ai_') and AI_ENABLED:
            # Force regenerate this AI challenge (passing category for consistency)
            cat = category or (challenge_id.split('_')[1] if len(challenge_id.split('_')) > 1 else None)
            return generate_ai_challenge(user_profile, cat)
        else:
            # Get pre-defined challenge by ID
            challenge = get_challenge_by_id(challenge_id)
            if challenge:
                return challenge
    
    # Get all available challenge IDs for the category
    available_challenges = []
    if category:
        # Get all challenges in this category
        all_category_challenges = get_challenge_by_category(category, None, return_all=True) or []
        available_challenges = [c.get('id', '') for c in all_category_challenges if isinstance(c, dict)]
    
    # Determine if we should use AI
    if AI_ENABLED and should_use_ai(user_profile, completed_challenges, available_challenges, category):
        # Use AI to generate a challenge
        return generate_ai_challenge(user_profile, category)
    
    # Otherwise, get a pre-defined challenge
    if category:
        challenge = get_challenge_by_category(category, completed_challenges)
    else:
        challenge = get_random_challenge(completed_challenges)
    
    # If we couldn't get a pre-defined challenge and AI is enabled, use AI as fallback
    if not challenge and AI_ENABLED:
        return generate_ai_challenge(user_profile, category)
    
    # Final fallback - ensure we always return a dictionary
    if not challenge:
        # Create a default challenge if everything else fails
        return {
            "id": "default_challenge",
            "title": "Connection Time",
            "description": "Spend 15 minutes today sharing three things you appreciate about each other.",
            "category": category or "Communication Boosters",
            "difficulty": "easy"
        }
        
    return challenge

def schedule_batch_generation(user_profile: Dict[str, Any], count: int = 5):
    """
    Schedule background generation of challenges to pre-fill the cache.
    This should be called during app initialization or as a periodic task.
    """
    if AI_ENABLED:
        try:
            # This would ideally be run as a background task
            # For simplicity, we're running it directly, but in production
            # this should be a celery task or similar async job
            batch_generate_challenges(user_profile, count)
        except Exception as e:
            # Log the error but don't disrupt the application
            print(f"Error scheduling batch challenge generation: {str(e)}")