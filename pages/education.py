import streamlit as st
import random

def show():
    """Display the education page"""
    
    # Check if user has completed profile
    if not st.session_state.user_profile["initialized"]:
        st.info("Please complete your profile setup on the home page first.")
        if st.button("Go to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return
    
    st.header("Learn Together")
    st.write("Explore educational content to enhance your relationship.")
    
    # Get education content
    from data.education import get_all_articles, get_article_by_id
    
    # Article categories
    categories = [
        "All Topics",
        "Communication Skills",
        "Consent and Boundaries",
        "Sexual Wellness",
        "Emotional Intimacy",
        "Relationship Growth"
    ]
    
    # Sidebar for filtering
    selected_category = st.selectbox(
        "Filter by topic",
        categories
    )
    
    # Get articles filtered by category if needed
    if selected_category == "All Topics":
        articles = get_all_articles()
    else:
        articles = [a for a in get_all_articles() if a["category"] == selected_category]
    
    # Track viewed articles
    viewed_ids = st.session_state.viewed_content["education_articles"]
    
    # Featured article (random from not viewed)
    unviewed = [a for a in articles if a["id"] not in viewed_ids]
    featured = random.choice(unviewed) if unviewed else random.choice(articles)
    
    # Mark featured as viewed
    if featured["id"] not in viewed_ids:
        viewed_ids.append(featured["id"])
    
    # Display featured article
    st.subheader("Featured Article")
    
    st.markdown(f"""
    <div style='background-color: #53327815; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #533278;'>
        <h3 style='margin-top: 0; color: #F4436C;'>{featured["title"]}</h3>
        <p><em>{featured["category"]} • {featured["reading_time"]} min read</em></p>
        <hr style='border-color: #0C748930;'>
        <p>{featured["content"][:300]}...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to read full article
    if st.button("Read Full Article", key="featured"):
        st.session_state.selected_article = featured["id"]
    
    # Check if an article is selected
    if "selected_article" in st.session_state and st.session_state.selected_article:
        article = get_article_by_id(st.session_state.selected_article)
        
        if article:
            # Display full article in modal-like format
            st.markdown("---")
            st.subheader(article["title"])
            st.caption(f"{article['category']} • {article['reading_time']} min read")
            
            # Content in sections
            sections = article["content"].split("\n\n")
            for section in sections:
                st.write(section)
            
            # Related product if any
            if "related_product" in article and article["related_product"]:
                product = article["related_product"]
                
                st.markdown("---")
                st.markdown(f"""
                <div style='background-color: #F4436C15; padding: 15px; border-radius: 10px; margin-top: 20px; border: 1px solid #F4436C;'>
                    <h4 style='margin-top: 0; color: #533278;'>Related Product</h4>
                    <p><strong>{product["name"]}</strong></p>
                    <p>{product["description"]}</p>
                    <p><em>Use code <strong style="color: #F4436C;">{product["coupon"]}</strong> for 10% off!</em></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Close button
            if st.button("Close Article"):
                st.session_state.selected_article = None
                st.rerun()
    
    st.markdown("---")
    
    # Display all articles in expandable sections
    st.subheader("Browse Articles")
    
    # Simple search
    search = st.text_input("Search articles", "")
    
    # Filter by search if needed
    if search:
        filtered_articles = [
            a for a in articles 
            if search.lower() in a["title"].lower() or search.lower() in a["content"].lower()
        ]
    else:
        filtered_articles = articles
    
    # Display as cards in columns
    if not filtered_articles:
        st.info("No articles found. Try a different search term.")
    else:
        # Show articles in 2 columns
        col1, col2 = st.columns(2)
        
        for i, article in enumerate(filtered_articles):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                article_color = "#F4436C" if "Sexual" in article["category"] else "#0C7489" 
                st.markdown(f"""
                <div style='border: 1px solid {article_color}; padding: 15px; border-radius: 5px; margin-bottom: 15px; background-color: {article_color}10;'>
                    <h4 style='margin-top: 0; color: #533278;'>{article["title"]}</h4>
                    <p><em>{article["category"]} • {article["reading_time"]} min read</em></p>
                    <p>{article["content"][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Read More", key=f"article_{article['id']}"):
                    if article["id"] not in viewed_ids:
                        viewed_ids.append(article["id"])
                    st.session_state.selected_article = article["id"]
                    st.rerun()
