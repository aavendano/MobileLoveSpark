import streamlit as st
import pandas as pd
from utils.visualization import create_spark_meter, create_category_completion_chart, create_streak_calendar, display_badges
from utils.data_manager import get_category_completion_stats

def show():
    """Display the progress tracking page"""
    
    # Check if user has completed profile
    if not st.session_state.user_profile["initialized"]:
        st.info("Please complete your profile setup on the home page first.")
        if st.button("Go to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return
    
    st.header("Your Connection Journey")
    st.write("Track your progress and see how your relationship is growing.")
    
    # Get partner names
    partner1, partner2 = st.session_state.user_profile["names"]
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Challenges Completed", st.session_state.user_progress["total_completed"])
    with col2:
        st.metric("Current Streak", f"{st.session_state.user_progress['streak']} days")
    with col3:
        st.metric("Spark Level", f"{st.session_state.user_progress['spark_level']}%")
    
    st.markdown("---")
    
    # Spark meter visualization
    st.subheader("Spark Meter")
    st.write("Watch your connection grow as you complete more challenges!")
    
    spark_level = st.session_state.user_progress["spark_level"]
    spark_fig = create_spark_meter(spark_level)
    st.plotly_chart(spark_fig, use_container_width=True)
    
    # Provide context based on level
    if spark_level < 30:
        st.info("You're just getting started! Complete more challenges to build your connection.")
    elif spark_level < 60:
        st.info("You're making great progress! Keep the momentum going.")
    elif spark_level < 90:
        st.success("Your connection is strong! You're building a resilient relationship.")
    else:
        st.success("Incredible connection! You've reached the highest levels of intimacy.")
    
    st.markdown("---")
    
    # Activity calendar
    st.subheader("Activity Calendar")
    st.write("Your recent challenge completion activity:")
    
    # Convert streak to calendar data if there's a streak
    streak_days = None
    if st.session_state.user_progress["streak"] > 0:
        import datetime
        streak = st.session_state.user_progress["streak"]
        today = datetime.date.today()
        streak_days = [today - datetime.timedelta(days=i) for i in range(streak)]
    
    calendar_fig = create_streak_calendar(streak_days)
    st.plotly_chart(calendar_fig, use_container_width=True)
    
    # Category completion
    st.subheader("Category Progress")
    st.write("See which areas you've been focusing on:")
    
    category_stats = get_category_completion_stats()
    if category_stats:
        cat_fig = create_category_completion_chart(category_stats)
        if cat_fig:
            st.plotly_chart(cat_fig, use_container_width=True)
        
        # Category recommendations
        least_completed = min(category_stats, key=lambda x: x["percentage"])
        if least_completed["percentage"] < 30:
            st.info(f"💡 Tip: Try exploring more challenges in the '{least_completed['category']}' category to balance your connection.")
    else:
        st.info("Complete challenges to see your category progress!")
    
    st.markdown("---")
    
    # Badges section
    st.subheader("Your Badges")
    st.write("Achievements you've unlocked on your journey:")
    
    badges = st.session_state.user_progress["badges"]
    display_badges(badges)
    
    # Help text for badges
    with st.expander("How to earn badges"):
        st.markdown("""
        **Challenge completion badges:**
        - **First Spark**: Complete your first challenge
        - **Flame Starter**: Complete 5 challenges
        - **Burning Bright**: Complete 10 challenges
        - **Inferno**: Complete 25 challenges
        
        **Streak badges:**
        - **3 Day Streak**: Complete challenges for 3 days in a row
        - **1 Week Connection**: Maintain a 7-day streak
        - **2 Week Devotion**: Maintain a 14-day streak
        - **Monthly Passion**: Maintain a 30-day streak
        """)
    
    st.markdown("---")
    
    # Reset progress button (for testing)
    with st.expander("Developer Options"):
        if st.button("Reset Progress (for testing)"):
            from utils.session_state import reset_progress
            reset_progress()
            st.success("Progress has been reset.")
            st.rerun()
