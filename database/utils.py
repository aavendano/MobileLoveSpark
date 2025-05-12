from sqlalchemy.orm import Session
import json
import logging
from typing import Optional, Dict, Any, List
import sqlalchemy.exc

from . import models, crud
from database.connection import Base, engine, get_db

def initialize_database():
    """Create database tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except sqlalchemy.exc.OperationalError as e:
        logging.error(f"Could not connect to database: {e}")
        logging.info("Application will continue with session-only storage")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        logging.info("Application will continue with session-only storage")

def session_to_db_data(session_state):
    """Convert Streamlit session state data to database format"""
    if not session_state.user_profile["initialized"]:
        return None
    
    user_data = {
        "partner1_name": session_state.user_profile["names"][0],
        "partner2_name": session_state.user_profile["names"][1],
        "relationship_status": session_state.user_profile["relationship_status"],
        "relationship_duration": session_state.user_profile["relationship_duration"],
        "challenge_frequency": session_state.user_profile["challenge_frequency"],
        "preferred_categories": session_state.user_profile["preferred_categories"],
        "excluded_categories": session_state.user_profile["excluded_categories"]
    }
    
    progress_data = {
        "completed_challenges": session_state.user_progress["completed_challenges"],
        "streak": session_state.user_progress["streak"],
        "last_completed": session_state.user_progress["last_completed"],
        "spark_level": session_state.user_progress["spark_level"],
        "badges": session_state.user_progress["badges"],
        "total_completed": session_state.user_progress["total_completed"]
    }
    
    challenge_data = {
        "current_challenge": session_state.challenge_state["current_challenge"],
        "current_category": session_state.challenge_state["current_category"],
        "last_generated": session_state.challenge_state["last_generated"]
    }
    
    viewed_content = {
        "education_articles": session_state.viewed_content["education_articles"],
        "products_viewed": session_state.viewed_content["products_viewed"]
    }
    
    return {
        "user_data": user_data,
        "progress_data": progress_data,
        "challenge_data": challenge_data,
        "viewed_content": viewed_content
    }

def db_to_session_data(db_user, db: Optional[Session] = None):
    """Convert database data to Streamlit session state format"""
    if not db_user:
        return None
    
    # If no db session provided, create one
    if db is None:
        with get_db() as session:
            return crud.export_user_data(session, db_user.id)
    else:
        # Use provided session
        return crud.export_user_data(db, db_user.id)