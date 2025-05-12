import streamlit as st
import datetime
from utils.session_state import generate_new_challenge

def show():
    """Display the home page"""
    
    # Check if user has completed profile
    if not st.session_state.user_profile["initialized"]:
        show_welcome_screen()
        return
    
    # Get names
    partner1, partner2 = st.session_state.user_profile["names"]
    
    # Show today's challenge if available
    st.header("Your Connection Journey")
    
    # Stats cards in 3 columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Spark Level", f"{st.session_state.user_progress['spark_level']}%")
    with col2:
        st.metric("Current Streak", f"{st.session_state.user_progress['streak']} days")
    with col3:
        st.metric("Challenges Completed", st.session_state.user_progress["total_completed"])
    
    st.markdown("---")
    
    # Daily challenge section
    st.subheader("Today's Challenge")
    
    # Check if we need to generate a new challenge
    if (st.session_state.challenge_state["current_challenge"] is None or 
        st.session_state.challenge_state["last_generated"] != datetime.date.today()):
        generate_new_challenge()
    
    # Display current challenge
    challenge = st.session_state.challenge_state["current_challenge"]
    category = st.session_state.challenge_state["current_category"]
    
    if challenge:
        st.write(f"**Category:** {category}")
        
        st.markdown(f"""
        <div style='background-color: #53327815; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #533278;'>
            <h3 style='margin-top: 0; color: #F4436C;'>{challenge['title']}</h3>
            <p>{challenge['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if challenge is completed
        is_completed = challenge["id"] in st.session_state.user_progress["completed_challenges"]
        
        if is_completed:
            st.success("✅ You've completed this challenge!")
            
            if st.button("Generate New Challenge"):
                new_challenge = generate_new_challenge()
                st.rerun()
        else:
            if st.button("Mark as Completed"):
                from utils.session_state import complete_challenge
                complete_challenge(challenge["id"], category)
                st.success("Challenge completed! Your connection grows stronger.")
                st.balloons()
                st.rerun()
    else:
        st.info("No challenge available. Try generating a new one.")
        if st.button("Generate Challenge"):
            generate_new_challenge()
            st.rerun()
    
    st.markdown("---")
    
    # Quick navigation cards
    st.subheader("Quick Access")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background-color: #F4436C20; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #F4436C;'>
            <h4 style='color: #533278;'>Browse Challenges</h4>
            <p>Explore challenges by category and find new ways to connect</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Challenges"):
            st.session_state.page = "Daily Challenges"
            st.rerun()
            
    with col2:
        st.markdown("""
        <div style='background-color: #0C748920; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #0C7489;'>
            <h4 style='color: #533278;'>Track Your Progress</h4>
            <p>View your connection stats and earned badges</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Progress"):
            st.session_state.page = "Progress Tracker"
            st.rerun()

def show_welcome_screen():
    """Show the welcome screen for new users"""
    st.header("Welcome to PlayLove Spark! 💖")
    
    st.write("""
    PlayLove Spark helps couples strengthen their connection through fun, 
    engaging challenges and activities. Get ready to ignite the spark in your relationship!
    """)
    
    st.info("To get started, please set up your profile.")
    
    with st.form("setup_profile"):
        st.subheader("Let's set up your profile")
        
        partner1 = st.text_input("Your name")
        partner2 = st.text_input("Your partner's name")
        
        st.subheader("Relationship Information")
        status = st.selectbox(
            "Relationship status",
            ["Dating", "Engaged", "Married", "Long-term partners", "Other"]
        )
        
        duration = st.selectbox(
            "How long have you been together?",
            ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years"]
        )
        
        st.subheader("Challenge Preferences")
        frequency = st.radio(
            "How often would you like to receive challenges?",
            ["Daily", "Every other day", "Weekly"],
            horizontal=True
        )
        
        st.subheader("Challenge Categories")
        st.write("Select the categories you're interested in:")
        
        col1, col2 = st.columns(2)
        with col1:
            comm = st.checkbox("Communication Boosters", value=True)
            touch = st.checkbox("Physical Touch & Affection", value=True)
            date = st.checkbox("Creative Date Night Ideas", value=True)
        
        with col2:
            sex = st.checkbox("Sexual Exploration", value=True)
            emotion = st.checkbox("Emotional Connection", value=True)
        
        # Collect preferred categories
        preferred_categories = []
        if comm:
            preferred_categories.append("Communication Boosters")
        if touch:
            preferred_categories.append("Physical Touch & Affection")
        if date:
            preferred_categories.append("Creative Date Night Ideas")
        if sex:
            preferred_categories.append("Sexual Exploration")
        if emotion:
            preferred_categories.append("Emotional Connection")
        
        # Submit button
        submitted = st.form_submit_button("Start My Journey")
        
        if submitted:
            if not partner1 or not partner2:
                st.error("Please provide both names to continue.")
            elif not preferred_categories:
                st.error("Please select at least one challenge category.")
            else:
                # Save to session state
                st.session_state.user_profile["initialized"] = True
                st.session_state.user_profile["names"] = [partner1, partner2]
                st.session_state.user_profile["relationship_status"] = status
                st.session_state.user_profile["relationship_duration"] = duration
                st.session_state.user_profile["challenge_frequency"] = frequency.lower()
                st.session_state.user_profile["preferred_categories"] = preferred_categories
                
                # Generate first challenge
                generate_new_challenge()
                
                st.success("Profile created successfully! Your journey begins now.")
                st.balloons()
                st.rerun()
    
    st.markdown("---")
    
    # Brief app description
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("What is PlayLove Spark?")
        st.write("""
        PlayLove Spark is designed to enhance intimacy and connection in your relationship through:
        
        * Daily or weekly challenges to bring you closer
        * Progress tracking to visualize your connection growth
        * Educational content about communication and intimacy
        * Tools to spark meaningful conversations
        * Fun activities to explore together
        
        Join thousands of Canadian couples who have strengthened their relationships with PlayLove Spark!
        """)
    
    with col2:
        st.markdown("""
        <div style='background-color: #F4436C15; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #F4436C;'>
            <h4 style='color: #533278;'>PlayLoveToys Values</h4>
            <ul style='text-align: left;'>
                <li>Empowering</li>
                <li>Sex-Positive</li>
                <li>Inclusive</li>
                <li>Educational</li>
                <li>Respectful</li>
                <li>Authentic</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
