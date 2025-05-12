import streamlit as st
import pandas as pd
import json
import datetime

def save_to_session(key, data):
    """Save data to session state"""
    st.session_state[key] = data

def export_progress_data():
    """Export user progress data as JSON"""
    if not st.session_state.user_profile["initialized"]:
        return None
    
    export_data = {
        "user_profile": st.session_state.user_profile,
        "user_progress": st.session_state.user_progress,
        "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Remove sensitive info if any
    if "email" in export_data["user_profile"]:
        del export_data["user_profile"]["email"]
    
    return json.dumps(export_data, indent=2)

def import_progress_data(json_data):
    """Import user progress data from JSON"""
    try:
        data = json.loads(json_data)
        
        # Validate data structure
        required_keys = ["user_profile", "user_progress", "export_date"]
        if not all(key in data for key in required_keys):
            return False, "Invalid data format: missing required keys"
        
        # Update session state
        st.session_state.user_profile = data["user_profile"]
        st.session_state.user_progress = data["user_progress"]
        
        return True, "Data imported successfully"
    except Exception as e:
        return False, f"Error importing data: {str(e)}"

def get_progress_dataframe():
    """Convert progress data to a dataframe for visualization"""
    if not st.session_state.user_profile["initialized"]:
        return pd.DataFrame()
    
    from data.challenges import ALL_CHALLENGES
    
    # Create mapping of challenge IDs to data
    challenge_map = {c["id"]: c for c in ALL_CHALLENGES}
    
    # Create dataframe of completed challenges
    completed = []
    for chall_id in st.session_state.user_progress["completed_challenges"]:
        if chall_id in challenge_map:
            challenge = challenge_map[chall_id]
            completed.append({
                "id": chall_id,
                "title": challenge["title"],
                "category": challenge["category"],
                "difficulty": challenge["difficulty"]
            })
    
    if not completed:
        return pd.DataFrame()
    
    return pd.DataFrame(completed)

def get_category_completion_stats():
    """Get statistics on category completion percentages"""
    from data.challenges import ALL_CHALLENGES
    
    # Count challenges by category
    category_counts = {}
    for challenge in ALL_CHALLENGES:
        cat = challenge["category"]
        if cat not in category_counts:
            category_counts[cat] = {"total": 0, "completed": 0}
        category_counts[cat]["total"] += 1
    
    # Count completed challenges by category
    completed_ids = st.session_state.user_progress["completed_challenges"]
    for chall_id in completed_ids:
        for challenge in ALL_CHALLENGES:
            if challenge["id"] == chall_id:
                cat = challenge["category"]
                category_counts[cat]["completed"] += 1
                break
    
    # Calculate percentages
    result = []
    for cat, counts in category_counts.items():
        percentage = (counts["completed"] / counts["total"]) * 100 if counts["total"] > 0 else 0
        result.append({
            "category": cat,
            "percentage": percentage,
            "completed": counts["completed"],
            "total": counts["total"]
        })
    
    return result
