import streamlit as st
import random

def show():
    """Display the product integration page"""
    
    # Check if user has completed profile
    if not st.session_state.user_profile["initialized"]:
        st.info("Please complete your profile setup on the home page first.")
        if st.button("Go to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return
    
    st.header("PlayLove Products")
    st.write("Discover products that can enhance your connection. Special offers for app users!")
    
    # Disclaimer
    st.info(
        "PlayLove Spark is designed to enhance your relationship through activities and education. "
        "These product suggestions are optional and designed to complement your journey."
    )
    
    # Get product data
    from data.products import get_all_products, get_product_by_id
    
    # Product categories
    categories = [
        "All Products",
        "Couples Toys",
        "Massage & Sensual",
        "Communication Games",
        "Wellness Products"
    ]
    
    # Filter by category
    selected_category = st.selectbox(
        "Browse by category",
        categories
    )
    
    # Get products filtered by category if needed
    if selected_category == "All Products":
        products = get_all_products()
    else:
        products = [p for p in get_all_products() if p["category"] == selected_category]
    
    # Track viewed products
    viewed_ids = st.session_state.viewed_content["products_viewed"]
    
    # Featured product (random from not viewed)
    unviewed = [p for p in products if p["id"] not in viewed_ids]
    featured = random.choice(unviewed) if unviewed else random.choice(products)
    
    # Mark featured as viewed
    if featured["id"] not in viewed_ids:
        viewed_ids.append(featured["id"])
    
    # Display featured product
    st.subheader("Featured Product")
    
    # Get a random challenge related to this product if available
    related_challenge = None
    if "related_challenges" in featured and featured["related_challenges"]:
        related_challenge = random.choice(featured["related_challenges"])
    
    st.markdown(f"""
    <div style='background-color: #F4436C15; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #F4436C;'>
        <h3 style='margin-top: 0; color: #533278;'>{featured["name"]}</h3>
        <p><em>{featured["category"]}</em></p>
        <hr style='border-color: #0C748930;'>
        <p>{featured["description"]}</p>
        <p><strong>Price:</strong> {featured["price"]}</p>
        <p><strong>App User Special:</strong> Use code <code style='background-color: #533278; color: white; padding: 2px 5px; border-radius: 3px;'>{featured["coupon"]}</code> for 10% off!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show related challenge if available
    if related_challenge:
        st.markdown(f"""
        <div style='background-color: #0C748915; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #0C7489;'>
            <h4 style='margin-top: 0; color: #533278;'>Try This Challenge with {featured["name"]}</h4>
            <p>{related_challenge}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Visit product button
    if st.button("Visit Product Page", key="featured"):
        st.session_state.selected_product = featured["id"]
    
    # Check if a product is selected
    if "selected_product" in st.session_state and st.session_state.selected_product:
        product = get_product_by_id(st.session_state.selected_product)
        
        if product:
            # Display full product details in modal-like format
            st.markdown("---")
            st.subheader(product["name"])
            st.caption(product["category"])
            
            # Product details
            st.write(product["description"])
            st.write(f"**Price:** {product['price']}")
            st.write(f"**App User Special:** Use code `{product['coupon']}` for 10% off!")
            
            # Benefits
            if "benefits" in product and product["benefits"]:
                st.subheader("Benefits")
                for benefit in product["benefits"]:
                    st.markdown(f"✅ {benefit}")
            
            # Related challenges
            if "related_challenges" in product and product["related_challenges"]:
                st.subheader("Suggested Challenges")
                for challenge in product["related_challenges"]:
                    st.markdown(f"""
                    <div style='background-color: #F0F0F0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        {challenge}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Close button
            if st.button("Close Details"):
                st.session_state.selected_product = None
                st.rerun()
    
    st.markdown("---")
    
    # Display all products in a grid
    st.subheader("Browse Products")
    
    # Simple search
    search = st.text_input("Search products", "")
    
    # Filter by search if needed
    if search:
        filtered_products = [
            p for p in products 
            if search.lower() in p["name"].lower() or search.lower() in p["description"].lower()
        ]
    else:
        filtered_products = products
    
    # Display as cards in columns
    if not filtered_products:
        st.info("No products found. Try a different search term.")
    else:
        # Show products in 3 columns
        cols = st.columns(3)
        
        for i, product in enumerate(filtered_products):
            col = cols[i % 3]
            
            with col:
                # Set color based on category
                product_color = "#F4436C" if "Couples" in product["category"] or "Sensual" in product["category"] else "#0C7489"
                
                st.markdown(f"""
                <div style='border: 1px solid {product_color}; padding: 15px; border-radius: 5px; margin-bottom: 15px; height: 200px; overflow: hidden; background-color: {product_color}10;'>
                    <h4 style='margin-top: 0; color: #533278;'>{product["name"]}</h4>
                    <p><em>{product["category"]}</em></p>
                    <p>{product["description"][:80]}...</p>
                    <p><strong style="color: {product_color};">{product["price"]}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Details", key=f"product_{product['id']}"):
                    if product["id"] not in viewed_ids:
                        viewed_ids.append(product["id"])
                    st.session_state.selected_product = product["id"]
                    st.rerun()
