# Unused Streamlit Files

This directory contains files from the original Streamlit implementation of PlayLove Spark. These files are no longer used in the current Django implementation but are kept here for reference purposes.

## Content

- `app.py` - Main Streamlit application entry point
- `fix_rerun.py` - Utility script to update deprecated Streamlit experimental_rerun() calls to rerun()
- `pages/` - Directory containing Streamlit page implementations:
  - `challenges.py` - Challenge management UI
  - `education.py` - Educational content UI
  - `home.py` - Home/dashboard UI
  - `products.py` - Products showcase UI
  - `progress.py` - Progress tracking UI
  - `settings.py` - User settings UI
- `utils/` - Utility modules for Streamlit:
  - `data_manager.py` - Data export/import functionality
  - `session_state.py` - Streamlit session state management
  - `visualization.py` - Streamlit charts and visualizations
- `css/` - Streamlit custom styling:
  - `custom.css` - Custom CSS for Streamlit UI

## Migration Notes

The PlayLove Spark application was migrated from Streamlit to Django for better scalability, authentication features, and traditional web application structure. The current implementation preserves the functionality while using Django templates, views, and database models.