import streamlit as st
from utils.session_state import complete_challenge, generate_new_challenge

def show():
    """Display the challenges page"""
    
    # Check if user has completed profile
    if not st.session_state.user_profile["initialized"]:
        st.info("Please complete your profile setup on the home page first.")
        if st.button("Go to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return
    
    st.header("Explore Challenges")
    st.write("Discover new ways to connect with your partner through our curated challenges.")
    
    # Challenge categories
    categories = [
        "Communication Boosters",
        "Physical Touch & Affection",
        "Creative Date Night Ideas", 
        "Sexual Exploration",
        "Emotional Connection"
    ]
    
    # Filter out excluded categories
    excluded = st.session_state.user_profile["excluded_categories"]
    available_categories = [c for c in categories if c not in excluded]
    
    # Category selection
    selected_category = st.selectbox(
        "Select a category",
        available_categories
    )
    
    st.markdown("---")
    
    # Category descriptions
    category_info = {
        "Communication Boosters": {
            "description": "Enhance your verbal and non-verbal communication skills to build understanding and connection.",
            "icon": "💬",
            "color": "#0C748915"
        },
        "Physical Touch & Affection": {
            "description": "Explore the power of physical connection through non-sexual touch and affection.",
            "icon": "🤝",
            "color": "#F4436C15"
        },
        "Creative Date Night Ideas": {
            "description": "Break out of your routine with fresh, exciting ways to spend quality time together.",
            "icon": "🌙",
            "color": "#53327815"
        },
        "Sexual Exploration": {
            "description": "Discover new dimensions of physical intimacy and pleasure with your partner.",
            "icon": "❤️",
            "color": "#F4436C20"
        },
        "Emotional Connection": {
            "description": "Deepen your emotional bond through vulnerability, trust, and authentic expression.",
            "icon": "🫂",
            "color": "#0C748920"
        }
    }
    
    # Display category info
    info = category_info[selected_category]
    # Determine border color based on category
    border_color = "#F4436C" if "Touch" in selected_category or "Sexual" in selected_category else "#533278"
    
    st.markdown(f"""
    <div style='background-color: {info["color"]}; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid {border_color};'>
        <h2 style='margin-top: 0; color: {border_color};'>{info["icon"]} {selected_category}</h2>
        <p>{info["description"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get challenges for this category
    from data.challenges import get_challenges_by_category
    challenges = get_challenges_by_category(selected_category)
    
    # Get completed challenge IDs
    completed_ids = st.session_state.user_progress["completed_challenges"]
    
    # Display current challenge if available and in this category
    current = st.session_state.challenge_state["current_challenge"]
    if current and st.session_state.challenge_state["current_category"] == selected_category:
        st.subheader("Today's Challenge")
        
        # Challenge card
        is_completed = current["id"] in completed_ids
        status_color = "#0C7489" if is_completed else "#F4436C" 
        status_text = "✅ Completed" if is_completed else "⏳ Pending"
        
        st.markdown(f"""
        <div style='border-left: 5px solid {status_color}; padding: 15px; background-color: {info["color"]}; margin-bottom: 20px; border-radius: 5px; border: 1px solid {status_color};'>
            <h3 style='margin-top: 0; color: #533278;'>{current["title"]}</h3>
            <p>{current["description"]}</p>
            <p style='color: {status_color}; font-weight: bold;'>{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not is_completed:
            if st.button("Mark as Completed", key="complete_current"):
                complete_challenge(current["id"], selected_category)
                st.success("Challenge completed! Your connection grows stronger.")
                st.balloons()
                st.rerun()
    
    # Display all challenges in this category
    st.subheader(f"All {selected_category} Challenges")
    
    # Filter button
    show_completed = st.checkbox("Show completed challenges", value=True)
    
    # Show challenges in expandable sections
    for challenge in challenges:
        is_completed = challenge["id"] in completed_ids
        
        # Skip if we're not showing completed
        if is_completed and not show_completed:
            continue
        
        status_color = "#0C7489" if is_completed else "#533278"
        status_icon = "✅" if is_completed else "🔒"
        
        with st.expander(f"{status_icon} {challenge['title']}"):
            st.write(challenge["description"])
            
            if "difficulty" in challenge:
                st.caption(f"Difficulty: {challenge['difficulty']}")
            
            if not is_completed:
                if st.button("Mark as Completed", key=f"complete_{challenge['id']}"):
                    complete_challenge(challenge["id"], selected_category)
                    st.success("Challenge completed! Your connection grows stronger.")
                    st.balloons()
                    st.rerun()
    
    st.markdown("---")
    
    # Generate a random challenge from this category
    st.subheader("Generate Random Challenge")
    st.write("Not sure where to start? Let us suggest a challenge for you.")
    
    if st.button("Surprise Me!"):
        challenge = generate_new_challenge(selected_category)
        if challenge:
            st.session_state.challenge_state["current_challenge"] = challenge
            st.session_state.challenge_state["current_category"] = selected_category
            st.success("New challenge generated!")
            st.rerun()
        else:
            st.error("No more challenges available in this category. Try another one!")
