import streamlit as st
import importlib.util
import sys
from utils.session_state import initialize_session_state
from database.utils import initialize_database
import os

# Initialize database tables
initialize_database()

# Import our custom pages modules directly to avoid conflict with installed Django pages package
def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not find module {module_name} at {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    if spec.loader is None:
        raise ImportError(f"Could not load module {module_name}")
    spec.loader.exec_module(module)
    return module

# Import our page modules
home = import_from_path("home_page", "./pages/home.py")
challenges = import_from_path("challenges_page", "./pages/challenges.py")
progress = import_from_path("progress_page", "./pages/progress.py")
education = import_from_path("education_page", "./pages/education.py")
products = import_from_path("products_page", "./pages/products.py")
settings = import_from_path("settings_page", "./pages/settings.py")

st.set_page_config(
    page_title="PlayLove Spark",
    page_icon="💖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('css/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
# Show database connection status in development
if 'PGDATABASE' in os.environ:
    st.sidebar.success("✓ Database connected", icon="✅")

def main():
    # Initialize session state
    initialize_session_state()
    
    # App header
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("assets/logo.svg", width=80)
    with col2:
        st.title("PlayLove Spark")
        st.write("Ignite connection and intimacy in your relationship")
    
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to:",
            ["Home", "Daily Challenges", "Progress Tracker", "Learn Together", "PlayLove Products", "Settings"],
            label_visibility="collapsed"
        )
        
        # Display user stats in sidebar
        if st.session_state.user_profile["initialized"]:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Connection Streak")
            st.sidebar.markdown(f"🔥 **{st.session_state.user_progress['streak']} days**")
            
            st.sidebar.subheader("Spark Level")
            spark_level = st.session_state.user_progress["spark_level"]
            st.sidebar.progress(spark_level / 100, f"Level: {spark_level}%")
            
            st.sidebar.markdown("---")
            st.sidebar.caption("PlayLove Spark © 2023")
            st.sidebar.caption("Made with ❤️ for Canadian couples")
    
    # Page routing
    if page == "Home":
        home.show()
    elif page == "Daily Challenges":
        challenges.show()
    elif page == "Progress Tracker":
        progress.show()
    elif page == "Learn Together":
        education.show()
    elif page == "PlayLove Products":
        products.show()
    elif page == "Settings":
        settings.show()

if __name__ == "__main__":
    main()
