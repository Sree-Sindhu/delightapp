import base64
import datetime
import os
import requests
import streamlit as st
from app_pages import customize, track, support, profile, cart, dashboard, map_demo, stores, cakes_catalog, cake_detail
from app_pages.data import STORES, CAKES
from app_pages import search, store_detail, login


def home_page():
    """Landing/home content: cake gallery + flash sale countdown (store-aware)."""
    # Image files reside in frontend/images; build absolute paths robustly
    images_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'images'))
    # Hide the 'Custom Cake' from the home gallery list (button remains elsewhere)
    filtered_cakes = [cake for cake in CAKES if cake.get('name') != 'Custom Cake']
    
    # Get top 7 best selling cakes (you can adjust this number between 5-9)
    best_selling_cakes = filtered_cakes[:7]  # Taking first 7 as "best selling"
    
    st.markdown("<h2 style='text-align: center; color: var(--text); margin-bottom: 20px; text-shadow: 0 2px 4px rgba(0,0,0,0.1);'>🌟 Best Selling Cakes</h2>", unsafe_allow_html=True)
    # Grid layout for best selling cakes (3 columns)
    for i in range(0, len(best_selling_cakes), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(best_selling_cakes):
                cake = best_selling_cakes[i + j]
                with col:
                    with st.container():
                        # Load image properly from file
                        img_path = os.path.join(images_dir, cake.get('image', ''))
                        img_src = ""
                        if os.path.exists(img_path):
                            try:
                                with open(img_path, 'rb') as f:
                                    encoded = base64.b64encode(f.read()).decode()
                                img_src = f"data:image/jpeg;base64,{encoded}"
                            except Exception:
                                img_src = ""
                        
                        # Fallback to placeholder if image not found
                        if not img_src:
                            img_src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2Y4ZjlmYSIvPgo8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE4IiBmaWxsPSIjNmM3NTdkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+8J+NsCBDYWtlPC90ZXh0Pgo8L3N2Zz4="
                        
                        st.markdown(f"""
                            <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.3); border: 1px solid rgba(255,255,255,0.4); border-radius: 15px; margin-bottom: 20px; backdrop-filter: blur(8px); box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                                <img src="{img_src}" alt="{cake.get('name', 'Cake')}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.2);">
                                <h4 style="margin: 12px 0 8px 0; color: #2c3e50; font-weight: 600;">{cake.get('name', 'Unknown')}</h4>
                                <p style="color: #34495e; margin: 5px 0; font-weight: 500;">₹{cake.get('price', 0)}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("📋\nView Details", key=f"view_home_{cake.get('id','')}_{i}_{j}"):
                            st.session_state.selected_cake_id = cake.get('id')
                            st.session_state.page = 'cake_detail'
                            st.rerun()
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='flash-sale'>", unsafe_allow_html=True)
    st.markdown("<h3>🎁 Flash Sale</h3>", unsafe_allow_html=True)
    # Countdown to a future date (example: 3 days from now)
    now = datetime.datetime.now()
    target = now + datetime.timedelta(days=3, hours=5, minutes=30)
    diff = target - now
    d, h, m, s = diff.days, diff.seconds // 3600, (diff.seconds % 3600) // 60, diff.seconds % 60
    st.markdown(f"<p style='margin:0 0 6px 0;'>⏳ Ends in: <code>{d}d {h}h {m}m {s}s</code></p>", unsafe_allow_html=True)
    st.markdown("<ul style='list-style:disc'>", unsafe_allow_html=True)
    st.markdown("<li>🎉 <strong>10% off</strong> Chocolate Cakes</li>", unsafe_allow_html=True)
    st.markdown("<li>🎂 Free delivery on <strong>₹500+</strong></li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div><hr style='opacity:0.4'>", unsafe_allow_html=True)
    st.markdown("<center><small style='opacity:0.7;'>© 2025 DelightAPI</small></center>", unsafe_allow_html=True)


def main_page():
    # Ensure a default page is set
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    # Force LIGHT theme globally (hidden from UI)
    st.session_state.ui_theme = 'light'
    # Default store selection
    if 'store_id' not in st.session_state:
        st.session_state.store_id = 'bangalore'
    
    # Display background styling
    background_img_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'bakery-background.jpg')
    if os.path.exists(background_img_path):
        with open(background_img_path, 'rb') as f:
            bg_data = base64.b64encode(f.read()).decode()
        bg_style = f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)),
                        url(data:image/jpeg;base64,{bg_data});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .content-translucent {{
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }}
        .flash-sale {{
            background: rgba(255, 165, 0, 0.3);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 165, 0, 0.5);
            border-radius: 15px;
            padding: 20px;
            margin: 25px 0;
            box-shadow: 0 4px 15px rgba(255, 165, 0, 0.2);
        }}
        
        /* Top Navigation Styling */
        .main-nav {{
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            padding: 8px 0;
            margin-bottom: 20px;
        }}
        .nav-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .nav-button {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 8px 12px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.8);
            min-width: 90px;
            min-height: 70px;
            text-decoration: none;
            color: #2c3e50;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s ease;
            cursor: pointer;
            backdrop-filter: blur(5px);
        }}
        .nav-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            background: rgba(255, 255, 255, 0.9);
        }}
        .nav-button.active {{
            background: rgba(74, 144, 226, 0.2);
            border-color: rgba(74, 144, 226, 0.4);
            color: #1f4e79;
        }}
        .nav-icon {{
            font-size: 20px;
            margin-bottom: 4px;
        }}
        
        /* Bottom Navigation Styling */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            padding: 8px 0 max(8px, env(safe-area-inset-bottom));
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
        }}
        .bottom-nav-container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            max-width: 400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .bottom-nav-button {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 6px 10px;
            border-radius: 10px;
            background: transparent;
            text-decoration: none;
            color: #666;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s ease;
            cursor: pointer;
            position: relative;
            min-width: 60px;
        }}
        .bottom-nav-button:hover {{
            background: rgba(74, 144, 226, 0.1);
            color: #1f4e79;
        }}
        .bottom-nav-button.active {{
            background: rgba(74, 144, 226, 0.2);
            color: #1f4e79;
        }}
        .bottom-nav-icon {{
            font-size: 18px;
            margin-bottom: 2px;
        }}
        .nav-badge {{
            position: absolute;
            top: -2px;
            right: 8px;
            background: #ff4444;
            color: white;
            border-radius: 10px;
            padding: 1px 6px;
            font-size: 10px;
            font-weight: bold;
            min-width: 16px;
            text-align: center;
        }}
        
        /* Add padding to content so bottom nav doesn't overlap */
        .main-content {{
            padding-bottom: 80px;
        }}
        
        /* Hide default Streamlit elements */
        .stDeployButton {{
            display: none;
        }}
        .stDecoration {{
            display: none;
        }}
        </style>
        """
        st.markdown(bg_style, unsafe_allow_html=True)
    
    # Top Navigation
    top_nav_items = [
        ("🏠", "Home", 'home'),
        ("🏬", "Store", 'stores'),
        ("🍰", "Cakes", 'cakes_catalog'),
        ("🛍️", "Cart", 'cart'),
        ("🎨", "Customize", 'customize'),
        ("🎯", "Dashboard", 'dashboard'),
        ("📍", "Map", 'map_demo'),
        ("📞", "Support", 'support'),
        ("👤", "Profile", 'profile'),
        ("🚚", "Track", 'track'),
        ("🔍", "Search", 'search'),
    ]
    
    st.markdown("<div class='main-nav'>", unsafe_allow_html=True)
    st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
    
    nav_cols = st.columns(len(top_nav_items))
    for idx, (icon, label, page_key) in enumerate(top_nav_items):
        with nav_cols[idx]:
            is_active = st.session_state.get('page') == page_key
            button_class = "nav-button active" if is_active else "nav-button"
            
            # Create invisible button for functionality
            if st.button(f"{icon}\n{label}", key=f"nav_{page_key}", 
                        help=f"Go to {label}"):
                st.session_state.page = page_key
                st.rerun()
                
            # Display styled button
            st.markdown(f"""
                <div class="{button_class}">
                    <div class="nav-icon">{icon}</div>
                    <div>{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Main content wrapper
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    # Page content
    current_page = st.session_state.get('page', 'home')
    
    if current_page == 'home':
        home_page()
    elif current_page == 'stores':
        stores.stores_page()
    elif current_page == 'cakes_catalog':
        cakes_catalog.cakes_catalog_page()
    elif current_page == 'cart':
        cart.cart_page()
    elif current_page == 'customize':
        customize.customize_page()
    elif current_page == 'dashboard':
        dashboard.dashboard_page()
    elif current_page == 'map_demo':
        map_demo.map_demo_page()
    elif current_page == 'support':
        support.support_page()
    elif current_page == 'profile':
        profile.profile_page()
    elif current_page == 'track':
        track.track_page()
    elif current_page == 'search':
        search.search_page()
    elif current_page == 'store_detail':
        store_detail.store_detail_page()
    elif current_page == 'cake_detail':
        cake_detail.cake_detail_page()
    elif current_page == 'login':
        login.login_page()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bottom Navigation - Always visible
    bottom_nav_items = [
        ("🏠", "Home", 'home'),
        ("🔍", "Search", 'search'),
        ("🛒", "Cart", 'cart', 3),  # Number indicates badge count
    ]
    
    st.markdown("<div class='bottom-nav'>", unsafe_allow_html=True)
    st.markdown("<div class='bottom-nav-container'>", unsafe_allow_html=True)
    
    for item in bottom_nav_items:
        icon, label, page_key = item[:3]
        badge_count = item[3] if len(item) > 3 else None
        
        is_active = st.session_state.get('page') == page_key
        button_class = "bottom-nav-button active" if is_active else "bottom-nav-button"
        
        badge_html = f'<span class="nav-badge">{badge_count}</span>' if badge_count else ''
        
        # Create the button HTML (visual only)
        st.markdown(f"""
            <div class="{button_class}" onclick="window.parent.postMessage({{type: 'streamlit:setPageState', page: '{page_key}'}}, '*')">
                <div class="bottom-nav-icon">{icon}</div>
                <div>{label}</div>
                {badge_html}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Handle bottom nav clicks with invisible buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("", key="bottom_home", help="Home"):
            st.session_state.page = 'home'
            st.rerun()
    with col2:
        if st.button("", key="bottom_search", help="Search"):
            st.session_state.page = 'search'
            st.rerun()
    with col3:
        if st.button("", key="bottom_cart", help="Cart"):
            st.session_state.page = 'cart'
            st.rerun()


if __name__ == "__main__":
    main_page()
