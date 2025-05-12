from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import json

from . import models

def create_user(db: Session, partner1_name: str, partner2_name: str, 
               relationship_status: str, relationship_duration: str,
               challenge_frequency: str, preferred_categories: List[str], 
               excluded_categories: Optional[List[str]] = None):
    """Create a new user profile"""
    if excluded_categories is None:
        excluded_categories = []
        
    # Create user
    db_user = models.User(
        partner1_name=partner1_name,
        partner2_name=partner2_name,
        relationship_status=relationship_status,
        relationship_duration=relationship_duration,
        challenge_frequency=challenge_frequency,
        preferred_categories=preferred_categories,
        excluded_categories=excluded_categories
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create user progress
    db_progress = models.UserProgress(user_id=db_user.id)
    db.add(db_progress)
    db.commit()
    
    return db_user

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, **kwargs) -> Optional[models.User]:
    """Update user profile information"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    for key, value in kwargs.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def get_user_progress(db: Session, user_id: int) -> Optional[models.UserProgress]:
    """Get a user's progress"""
    return db.query(models.UserProgress).filter(models.UserProgress.user_id == user_id).first()

def complete_challenge(db: Session, user_id: int, challenge_id: str, category: str) -> models.CompletedChallenge:
    """Mark a challenge as completed and update progress"""
    # Check if challenge already completed
    existing = db.query(models.CompletedChallenge).filter(
        models.CompletedChallenge.user_id == user_id,
        models.CompletedChallenge.challenge_id == challenge_id
    ).first()
    
    if existing:
        return existing
    
    # Add completed challenge
    today = datetime.now()
    db_completed = models.CompletedChallenge(
        user_id=user_id,
        challenge_id=challenge_id,
        category=category,
        completed_at=today
    )
    db.add(db_completed)
    
    # Update progress
    db_progress = get_user_progress(db, user_id)
    if db_progress:
        # Update total completed
        db_progress_data = {}
        db_progress_data['total_completed'] = db_progress.total_completed + 1
        
        # Update last completed date
        db_progress_data['last_completed'] = today
        
        # Update streak
        if db_progress.last_completed and db_progress.last_completed.date() == (today - timedelta(days=1)).date():
            db_progress_data['streak'] = db_progress.streak + 1
        elif db_progress.last_completed and db_progress.last_completed.date() != today.date():
            db_progress_data['streak'] = 1
            
        # Update spark level (max 100%)
        db_progress_data['spark_level'] = min(db_progress.spark_level + 5, 100)
        
        # Apply all updates
        for key, value in db_progress_data.items():
            setattr(db_progress, key, value)
    
    db.commit()
    db.refresh(db_completed)
    
    # Check for badges
    check_for_badges(db, user_id)
    
    return db_completed

def check_for_badges(db: Session, user_id: int) -> None:
    """Check and award new badges based on progress"""
    progress = get_user_progress(db, user_id)
    if not progress:
        return
    
    # Get existing badges
    existing_badges = [badge.badge_name for badge in 
                      db.query(models.UserBadge).filter(models.UserBadge.user_id == user_id).all()]
    
    # Challenge completion badges
    if progress.total_completed >= 1 and "First Spark" not in existing_badges:
        award_badge(db, user_id, "First Spark")
    if progress.total_completed >= 5 and "Flame Starter" not in existing_badges:
        award_badge(db, user_id, "Flame Starter")
    if progress.total_completed >= 10 and "Burning Bright" not in existing_badges:
        award_badge(db, user_id, "Burning Bright")
    if progress.total_completed >= 25 and "Inferno" not in existing_badges:
        award_badge(db, user_id, "Inferno")
    
    # Streak badges
    if progress.streak >= 3 and "3 Day Streak" not in existing_badges:
        award_badge(db, user_id, "3 Day Streak")
    if progress.streak >= 7 and "1 Week Connection" not in existing_badges:
        award_badge(db, user_id, "1 Week Connection")
    if progress.streak >= 14 and "2 Week Devotion" not in existing_badges:
        award_badge(db, user_id, "2 Week Devotion")
    if progress.streak >= 30 and "Monthly Passion" not in existing_badges:
        award_badge(db, user_id, "Monthly Passion")

def award_badge(db: Session, user_id: int, badge_name: str) -> models.UserBadge:
    """Award a badge to a user"""
    new_badge = models.UserBadge(
        user_id=user_id,
        badge_name=badge_name
    )
    db.add(new_badge)
    db.commit()
    return new_badge

def get_user_badges(db: Session, user_id: int) -> List[models.UserBadge]:
    """Get all badges for a user"""
    return db.query(models.UserBadge).filter(models.UserBadge.user_id == user_id).all()

def get_completed_challenges(db: Session, user_id: int) -> List[models.CompletedChallenge]:
    """Get all completed challenges for a user"""
    return db.query(models.CompletedChallenge).filter(models.CompletedChallenge.user_id == user_id).all()

def set_current_challenge(db: Session, user_id: int, challenge_id: str, category: str) -> models.CurrentChallenge:
    """Set the current challenge for a user"""
    # Check if user already has a current challenge
    existing = db.query(models.CurrentChallenge).filter(
        models.CurrentChallenge.user_id == user_id
    ).first()
    
    if existing:
        # Update the existing challenge
        existing_data = {}
        existing_data['challenge_id'] = challenge_id
        existing_data['category'] = category
        existing_data['generated_at'] = datetime.now()
        
        for key, value in existing_data.items():
            setattr(existing, key, value)
            
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new current challenge
    db_challenge = models.CurrentChallenge(
        user_id=user_id,
        challenge_id=challenge_id,
        category=category,
        generated_at=datetime.now()
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_current_challenge(db: Session, user_id: int) -> Optional[models.CurrentChallenge]:
    """Get the current challenge for a user"""
    return db.query(models.CurrentChallenge).filter(
        models.CurrentChallenge.user_id == user_id
    ).first()

def add_viewed_article(db: Session, user_id: int, article_id: str) -> models.ViewedArticle:
    """Add an article to user's viewed articles"""
    # Check if already viewed
    existing = db.query(models.ViewedArticle).filter(
        models.ViewedArticle.user_id == user_id,
        models.ViewedArticle.article_id == article_id
    ).first()
    
    if existing:
        return existing
    
    # Add new viewed article
    db_article = models.ViewedArticle(
        user_id=user_id,
        article_id=article_id
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_viewed_articles(db: Session, user_id: int) -> List[models.ViewedArticle]:
    """Get all viewed articles for a user"""
    return db.query(models.ViewedArticle).filter(
        models.ViewedArticle.user_id == user_id
    ).all()

def add_viewed_product(db: Session, user_id: int, product_id: str) -> models.ViewedProduct:
    """Add a product to user's viewed products"""
    # Check if already viewed
    existing = db.query(models.ViewedProduct).filter(
        models.ViewedProduct.user_id == user_id,
        models.ViewedProduct.product_id == product_id
    ).first()
    
    if existing:
        return existing
    
    # Add new viewed product
    db_product = models.ViewedProduct(
        user_id=user_id,
        product_id=product_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_viewed_products(db: Session, user_id: int) -> List[models.ViewedProduct]:
    """Get all viewed products for a user"""
    return db.query(models.ViewedProduct).filter(
        models.ViewedProduct.user_id == user_id
    ).all()

def reset_user_progress(db: Session, user_id: int) -> bool:
    """Reset all progress for a user (for testing)"""
    # Delete completed challenges
    db.query(models.CompletedChallenge).filter(
        models.CompletedChallenge.user_id == user_id
    ).delete()
    
    # Delete badges
    db.query(models.UserBadge).filter(
        models.UserBadge.user_id == user_id
    ).delete()
    
    # Delete current challenge
    db.query(models.CurrentChallenge).filter(
        models.CurrentChallenge.user_id == user_id
    ).delete()
    
    # Reset progress
    progress = get_user_progress(db, user_id)
    if progress:
        progress_data = {}
        progress_data['streak'] = 0
        progress_data['last_completed'] = None
        progress_data['spark_level'] = 10
        progress_data['total_completed'] = 0
        
        for key, value in progress_data.items():
            setattr(progress, key, value)
    
    db.commit()
    return True

def export_user_data(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """Export all user data as a dictionary"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    progress = get_user_progress(db, user_id)
    completed = get_completed_challenges(db, user_id)
    badges = get_user_badges(db, user_id)
    viewed_articles = get_viewed_articles(db, user_id)
    viewed_products = get_viewed_products(db, user_id)
    current = get_current_challenge(db, user_id)
    
    export_data = {
        "user_profile": {
            "initialized": True,
            "names": [user.partner1_name, user.partner2_name],
            "relationship_status": user.relationship_status,
            "relationship_duration": user.relationship_duration,
            "challenge_frequency": user.challenge_frequency,
            "preferred_categories": user.preferred_categories,
            "excluded_categories": user.excluded_categories
        },
        "user_progress": {
            "completed_challenges": [c.challenge_id for c in completed],
            "streak": progress.streak if progress else 0,
            "last_completed": progress.last_completed.isoformat() if progress and progress.last_completed else None,
            "spark_level": progress.spark_level if progress else 10,
            "badges": [b.badge_name for b in badges],
            "total_completed": progress.total_completed if progress else 0
        },
        "challenge_state": {
            "current_challenge": current.challenge_id if current else None,
            "current_category": current.category if current else None,
            "last_generated": current.generated_at.date().isoformat() if current else None
        },
        "viewed_content": {
            "education_articles": [a.article_id for a in viewed_articles],
            "products_viewed": [p.product_id for p in viewed_products]
        },
        "export_date": datetime.now().isoformat()
    }
    
    return export_data