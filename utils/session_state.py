import streamlit as st
import datetime
import random
from database.connection import get_db
from database import models, crud, utils
from typing import Optional, List

def initialize_session_state():
    """Initialize all session state variables if they don't exist"""
    
    # User ID for database integration
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    # User profile
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "initialized": False,
            "names": ["", ""],
            "challenge_frequency": "daily",
            "preferred_categories": [],
            "excluded_categories": [],
            "relationship_status": "",
            "relationship_duration": ""
        }
    
    # User progress
    if "user_progress" not in st.session_state:
        st.session_state.user_progress = {
            "completed_challenges": [],
            "streak": 0,
            "last_completed": None,
            "spark_level": 10,  # Starting at 10%
            "badges": [],
            "total_completed": 0
        }
    
    # Challenge state
    if "challenge_state" not in st.session_state:
        st.session_state.challenge_state = {
            "current_challenge": None,
            "current_category": None,
            "last_generated": None
        }
    
    # Viewed content
    if "viewed_content" not in st.session_state:
        st.session_state.viewed_content = {
            "education_articles": [],
            "products_viewed": []
        }
    
    # Try to load user from database (if user_id exists)
    if st.session_state.user_id:
        load_user_from_database(st.session_state.user_id)

def create_user_profile(partner1_name: str, partner2_name: str, 
                      relationship_status: str, relationship_duration: str,
                      challenge_frequency: str, preferred_categories: List[str], 
                      excluded_categories: Optional[List[str]] = None):
    """Create a new user profile in the database"""
    with get_db() as db:
        # Create user in database
        db_user = crud.create_user(
            db=db,
            partner1_name=partner1_name,
            partner2_name=partner2_name,
            relationship_status=relationship_status,
            relationship_duration=relationship_duration,
            challenge_frequency=challenge_frequency,
            preferred_categories=preferred_categories,
            excluded_categories=excluded_categories or []
        )
        
        # Save user ID
        st.session_state.user_id = db_user.id
        
        # Update session state with user data
        user_data = utils.db_to_session_data(db_user, db)
        update_session_from_db(user_data)
        
        return db_user.id

def load_user_from_database(user_id: int) -> bool:
    """Load user data from database into session state"""
    with get_db() as db:
        # Get user from database
        db_user = crud.get_user(db, user_id)
        if not db_user:
            return False
        
        # Export user data and update session state
        user_data = utils.db_to_session_data(db_user, db)
        update_session_from_db(user_data)
        
        return True

def update_session_from_db(user_data):
    """Update session state with data from database"""
    if not user_data:
        return
    
    # Update user profile
    st.session_state.user_profile = user_data["user_profile"]
    
    # Update user progress
    st.session_state.user_progress = user_data["user_progress"]
    
    # Update challenge state
    st.session_state.challenge_state = user_data["challenge_state"]
    
    # Update viewed content
    st.session_state.viewed_content = user_data["viewed_content"]

def save_session_to_db():
    """Save current session state to database"""
    if not st.session_state.user_id or not st.session_state.user_profile["initialized"]:
        return
    
    with get_db() as db:
        # Get user
        db_user = crud.get_user(db, st.session_state.user_id)
        if not db_user:
            return
        
        # Update user data
        crud.update_user(
            db=db,
            user_id=st.session_state.user_id,
            partner1_name=st.session_state.user_profile["names"][0],
            partner2_name=st.session_state.user_profile["names"][1],
            relationship_status=st.session_state.user_profile["relationship_status"],
            relationship_duration=st.session_state.user_profile["relationship_duration"],
            challenge_frequency=st.session_state.user_profile["challenge_frequency"],
            preferred_categories=st.session_state.user_profile["preferred_categories"],
            excluded_categories=st.session_state.user_profile["excluded_categories"]
        )
        
        # Update current challenge if needed
        if st.session_state.challenge_state["current_challenge"]:
            challenge_id = st.session_state.challenge_state["current_challenge"]
            if isinstance(challenge_id, dict):
                challenge_id = challenge_id.get("id", "")
            category = st.session_state.challenge_state["current_category"] or ""
            
            crud.set_current_challenge(
                db=db,
                user_id=st.session_state.user_id,
                challenge_id=challenge_id,
                category=category
            )

def complete_challenge(challenge_id, category):
    """Mark a challenge as completed and update progress"""
    today = datetime.date.today()
    
    # Add to completed challenges list (memory)
    if challenge_id not in st.session_state.user_progress["completed_challenges"]:
        st.session_state.user_progress["completed_challenges"].append(challenge_id)
        st.session_state.user_progress["total_completed"] += 1
    
    # Update last completed date
    st.session_state.user_progress["last_completed"] = today.isoformat()
    
    # Update streak
    if st.session_state.user_progress["last_completed"] == (today - datetime.timedelta(days=1)).isoformat():
        st.session_state.user_progress["streak"] += 1
    elif st.session_state.user_progress["last_completed"] != today.isoformat():
        st.session_state.user_progress["streak"] = 1
    
    # Update spark level (max 100%)
    new_spark = min(st.session_state.user_progress["spark_level"] + 5, 100)
    st.session_state.user_progress["spark_level"] = new_spark
    
    # Check for badges (memory)
    check_for_new_badges()
    
    # Generate new challenge (memory)
    generate_new_challenge()
    
    # If user is in database, update database
    if st.session_state.user_id:
        with get_db() as db:
            # Mark challenge as completed in database
            crud.complete_challenge(
                db=db, 
                user_id=st.session_state.user_id, 
                challenge_id=challenge_id, 
                category=category
            )
            
            # Update current challenge in database
            current_challenge = st.session_state.challenge_state["current_challenge"]
            if isinstance(current_challenge, dict):
                current_id = current_challenge.get("id", "")
            else:
                current_id = current_challenge
                
            current_category = st.session_state.challenge_state["current_category"] or ""
            
            crud.set_current_challenge(
                db=db,
                user_id=st.session_state.user_id,
                challenge_id=current_id,
                category=current_category
            )

def check_for_new_badges():
    """Check and award new badges based on progress"""
    badges = st.session_state.user_progress["badges"]
    total = st.session_state.user_progress["total_completed"]
    streak = st.session_state.user_progress["streak"]
    
    # Challenge completion badges
    if total >= 1 and "First Spark" not in badges:
        badges.append("First Spark")
    if total >= 5 and "Flame Starter" not in badges:
        badges.append("Flame Starter")
    if total >= 10 and "Burning Bright" not in badges:
        badges.append("Burning Bright")
    if total >= 25 and "Inferno" not in badges:
        badges.append("Inferno")
    
    # Streak badges
    if streak >= 3 and "3 Day Streak" not in badges:
        badges.append("3 Day Streak")
    if streak >= 7 and "1 Week Connection" not in badges:
        badges.append("1 Week Connection")
    if streak >= 14 and "2 Week Devotion" not in badges:
        badges.append("2 Week Devotion")
    if streak >= 30 and "Monthly Passion" not in badges:
        badges.append("Monthly Passion")

def generate_new_challenge(category=None):
    """Generate a new challenge for the user"""
    from data.challenges import get_challenge_by_category
    
    # If no specific category, use user preferences or random
    if category is None:
        if st.session_state.user_profile["preferred_categories"]:
            # Filter out excluded categories
            available_cats = [c for c in st.session_state.user_profile["preferred_categories"]
                             if c not in st.session_state.user_profile["excluded_categories"]]
            if available_cats:
                category = random.choice(available_cats)
            else:
                category = "Communication Boosters"  # Default
        else:
            categories = ["Communication Boosters", "Physical Touch & Affection", 
                         "Creative Date Night Ideas", "Sexual Exploration", "Emotional Connection"]
            excluded = st.session_state.user_profile["excluded_categories"]
            available_cats = [c for c in categories if c not in excluded]
            category = random.choice(available_cats)
    
    # Get a challenge that hasn't been completed
    completed_ids = st.session_state.user_progress["completed_challenges"]
    challenge = get_challenge_by_category(category, completed_ids)
    
    # Update challenge state
    st.session_state.challenge_state["current_challenge"] = challenge
    st.session_state.challenge_state["current_category"] = category
    st.session_state.challenge_state["last_generated"] = datetime.date.today().isoformat()
    
    # If user is in database, update database
    if st.session_state.user_id:
        with get_db() as db:
            challenge_id = challenge["id"] if isinstance(challenge, dict) else challenge
            crud.set_current_challenge(
                db=db,
                user_id=st.session_state.user_id,
                challenge_id=challenge_id,
                category=category
            )
    
    return challenge

def add_viewed_article(article_id):
    """Add an article to viewed articles"""
    if article_id not in st.session_state.viewed_content["education_articles"]:
        st.session_state.viewed_content["education_articles"].append(article_id)
    
    # If user is in database, update database
    if st.session_state.user_id:
        with get_db() as db:
            crud.add_viewed_article(
                db=db,
                user_id=st.session_state.user_id,
                article_id=article_id
            )

def add_viewed_product(product_id):
    """Add a product to viewed products"""
    if product_id not in st.session_state.viewed_content["products_viewed"]:
        st.session_state.viewed_content["products_viewed"].append(product_id)
    
    # If user is in database, update database
    if st.session_state.user_id:
        with get_db() as db:
            crud.add_viewed_product(
                db=db,
                user_id=st.session_state.user_id,
                product_id=product_id
            )

def reset_progress():
    """Reset all progress (for testing)"""
    # Reset memory state
    st.session_state.user_progress = {
        "completed_challenges": [],
        "streak": 0,
        "last_completed": None,
        "spark_level": 10,
        "badges": [],
        "total_completed": 0
    }
    st.session_state.challenge_state = {
        "current_challenge": None,
        "current_category": None,
        "last_generated": None
    }
    st.session_state.viewed_content = {
        "education_articles": [],
        "products_viewed": []
    }
    
    # If user is in database, reset database
    if st.session_state.user_id:
        with get_db() as db:
            crud.reset_user_progress(db, st.session_state.user_id)
