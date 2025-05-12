import os
from database.connection import get_db
from database import models, crud, utils

def test_database_connection():
    # Initialize the database
    utils.initialize_database()
    
    # Create a test user
    with get_db() as db:
        # Create user
        db_user = crud.create_user(
            db=db,
            partner1_name="Partner 1",
            partner2_name="Partner 2",
            relationship_status="Dating",
            relationship_duration="1-2 years",
            challenge_frequency="daily",
            preferred_categories=["intimacy", "communication"],
            excluded_categories=["adventure"]
        )
        
        print(f"Created user with ID: {db_user.id}")
        
        # Get user
        user = crud.get_user(db, db_user.id)
        print(f"Retrieved user: {user.partner1_name} and {user.partner2_name}")
        
        # Complete a challenge
        challenge = crud.complete_challenge(
            db=db,
            user_id=db_user.id,
            challenge_id="test-challenge-1",
            category="intimacy"
        )
        
        print(f"Completed challenge: {challenge.challenge_id}")
        
        # Get user progress
        progress = crud.get_user_progress(db, db_user.id)
        print(f"User progress: Streak = {progress.streak}, Spark Level = {progress.spark_level}")
        
        # Get completed challenges
        completed = crud.get_completed_challenges(db, db_user.id)
        print(f"Completed challenges: {len(completed)}")
        
        # Get badges
        badges = crud.get_user_badges(db, db_user.id)
        for badge in badges:
            print(f"Earned badge: {badge.badge_name}")
        
        # Export user data
        data = crud.export_user_data(db, db_user.id)
        print(f"Exported user data: {data}")
        
        # Clean up (optional)
        # crud.delete_user(db, db_user.id)
        # print("User deleted")

if __name__ == "__main__":
    test_database_connection()