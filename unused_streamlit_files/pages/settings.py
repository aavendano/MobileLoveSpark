import streamlit as st
import json
from utils.data_manager import export_progress_data, import_progress_data

def show():
    """Display the settings page"""
    
    st.header("Settings & Preferences")
    st.markdown("<p style='color: #533278;'>Customize your PlayLove Spark experience.</p>", unsafe_allow_html=True)
    
    # Check if profile is initialized
    if not st.session_state.user_profile["initialized"]:
        st.info("Please complete your profile setup on the home page first.")
        if st.button("Go to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return
    
    # Profile information
    with st.expander("Profile Information", expanded=True):
        # Get current profile data
        profile = st.session_state.user_profile
        
        st.subheader("Update Your Profile")
        
        # Partner names
        col1, col2 = st.columns(2)
        with col1:
            partner1 = st.text_input("Your name", profile["names"][0])
        with col2:
            partner2 = st.text_input("Your partner's name", profile["names"][1])
        
        # Relationship info
        status = st.selectbox(
            "Relationship status",
            ["Dating", "Engaged", "Married", "Long-term partners", "Other"],
            index=["Dating", "Engaged", "Married", "Long-term partners", "Other"].index(profile["relationship_status"]) if profile["relationship_status"] in ["Dating", "Engaged", "Married", "Long-term partners", "Other"] else 0
        )
        
        duration = st.selectbox(
            "How long have you been together?",
            ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years"],
            index=["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years"].index(profile["relationship_duration"]) if profile["relationship_duration"] in ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years"] else 0
        )
        
        # Save button
        if st.button("Save Profile Changes"):
            st.session_state.user_profile["names"] = [partner1, partner2]
            st.session_state.user_profile["relationship_status"] = status
            st.session_state.user_profile["relationship_duration"] = duration
            st.success("Profile updated successfully!")
    
    # Challenge preferences
    with st.expander("Challenge Preferences", expanded=True):
        st.subheader("Challenge Settings")
        
        # Challenge frequency
        frequency = st.radio(
            "How often would you like to receive challenges?",
            ["Daily", "Every other day", "Weekly"],
            index=["daily", "every other day", "weekly"].index(profile["challenge_frequency"].lower()) if profile["challenge_frequency"].lower() in ["daily", "every other day", "weekly"] else 0,
            horizontal=True
        )
        
        # Categories
        st.write("Select the categories you're interested in:")
        
        all_categories = ["Communication Boosters", "Physical Touch & Affection", "Creative Date Night Ideas", "Sexual Exploration", "Emotional Connection"]
        
        # Create columns for checkboxes
        col1, col2 = st.columns(2)
        
        selected_categories = []
        with col1:
            if st.checkbox("Communication Boosters", value="Communication Boosters" in profile["preferred_categories"]):
                selected_categories.append("Communication Boosters")
            
            if st.checkbox("Physical Touch & Affection", value="Physical Touch & Affection" in profile["preferred_categories"]):
                selected_categories.append("Physical Touch & Affection")
            
            if st.checkbox("Creative Date Night Ideas", value="Creative Date Night Ideas" in profile["preferred_categories"]):
                selected_categories.append("Creative Date Night Ideas")
        
        with col2:
            if st.checkbox("Sexual Exploration", value="Sexual Exploration" in profile["preferred_categories"]):
                selected_categories.append("Sexual Exploration")
            
            if st.checkbox("Emotional Connection", value="Emotional Connection" in profile["preferred_categories"]):
                selected_categories.append("Emotional Connection")
        
        # Excluded categories
        st.write("Are there any categories you'd like to exclude completely?")
        excluded_categories = []
        
        for category in all_categories:
            if category in selected_categories:
                continue  # Skip if it's selected above
            
            if st.checkbox(f"Exclude {category}", value=category in profile["excluded_categories"]):
                excluded_categories.append(category)
        
        # Save button
        if st.button("Save Challenge Preferences"):
            if not selected_categories:
                st.error("Please select at least one challenge category.")
            else:
                st.session_state.user_profile["challenge_frequency"] = frequency.lower()
                st.session_state.user_profile["preferred_categories"] = selected_categories
                st.session_state.user_profile["excluded_categories"] = excluded_categories
                st.success("Challenge preferences updated successfully!")
    
    # Notifications (mockup)
    with st.expander("Notifications", expanded=False):
        st.subheader("Notification Settings")
        st.write("Customize when and how you receive notifications.")
        
        st.checkbox("Challenge reminders", value=True)
        st.checkbox("Achievement notifications", value=True)
        st.checkbox("Weekly progress summary", value=True)
        
        st.caption("Note: Notification settings are not fully implemented in this prototype.")
    
    # Privacy settings
    with st.expander("Privacy", expanded=False):
        st.subheader("Privacy Settings")
        st.write("Control your data and privacy preferences.")
        
        st.checkbox("Allow anonymous usage data collection to improve the app", value=False)
        st.checkbox("Receive occasional emails about relationship resources", value=False)
        
        st.write("Your data is stored locally in this prototype. No information is transmitted externally.")
    
    # Data management
    with st.expander("Data Management", expanded=False):
        st.subheader("Export/Import Data")
        st.write("Export your progress for backup or transfer to another device.")
        
        # Export data
        if st.button("Export My Data"):
            exported_data = export_progress_data()
            if exported_data:
                st.download_button(
                    "Download JSON Data",
                    exported_data,
                    file_name="playlove_spark_data.json",
                    mime="application/json"
                )
            else:
                st.error("No data to export. Please complete setup first.")
        
        # Import data
        st.write("Import your previously exported data:")
        uploaded_file = st.file_uploader("Upload JSON data file", type=["json"])
        
        if uploaded_file is not None:
            # Read the file
            data = uploaded_file.getvalue().decode("utf-8")
            
            # Import the data
            success, message = import_progress_data(data)
            
            if success:
                st.success(message)
                st.button("Refresh to See Changes", on_click=st.rerun)
            else:
                st.error(message)
    
    # About
    with st.expander("About PlayLove Spark", expanded=False):
        st.subheader("About")
        st.write("""
        PlayLove Spark is designed to enhance intimacy and connection in relationships through 
        engaging challenges, progress tracking, and educational content.
        
        **Version:** 1.0.0 (Prototype)
        
        **Created by:** PlayLoveToys
        
        **Target Audience:** Canadian couples aged 25-55 interested in sexual wellness, 
        open communication, and enhancing their relationships.
        
        **Brand Values:**
        - Empowering
        - Sex-Positive
        - Inclusive
        - Educational
        - Engaging
        - Respectful
        - Authentic
        - Discreet
        """)
