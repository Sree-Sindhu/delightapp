import streamlit as st
import requests
import pandas as pd
import json

'''# Define the base URL for your backend API
API_BASE_URL = "http://127.0.0.1:8000/api"

def dashboard_page():
    """
    Renders the dashboard page content for a logged-in user.
    """
    # Load Font Awesome for icons
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        """,
        unsafe_allow_html=True
    )

    # Check if user is logged in
    if not st.session_state.get("logged_in"):
        st.error("You must be logged in to view the dashboard.")
        return

    # --- Fetch Data from Backend (Placeholder for real data) ---
    headers = {"Authorization": f"Token {st.session_state.get('token')}"}
    
    # Initialize placeholder data
    user_profile_data = {}
    orders_data = []
    sales_analytics_data = {}
    
    try:
        # Fetch user profile data
        user_profile_res = requests.get(f"{API_BASE_URL}/auth/profile/", headers=headers)
        if user_profile_res.status_code == 200:
            user_profile_data = user_profile_res.json()
        
        # Fetch recent orders
        orders_res = requests.get(f"{API_BASE_URL}/orders/", headers=headers)
        if orders_res.status_code == 200:
            orders_data = orders_res.json()

        # Fetch analytics data (assuming admin access)
        sales_analytics_res = requests.get(f"{API_BASE_URL}/analytics/sales/", headers=headers)
        if sales_analytics_res.status_code == 200:
            sales_analytics_data = sales_analytics_res.json()
        
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend server. Please check if the server is running.")
        return
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return

    st.markdown("<h1 class='dashboard-header'>Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subheader'>Welcome back! Here's your account overview.</p>", unsafe_allow_html=True)

    # --- Main Dashboard Layout ---
    main_col, right_col = st.columns([2, 1])

    with main_col:
        # --- Metric Cards Section ---
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon' style='background: #f8f0f7; color: #d63384;'>
                        <i class="fas fa-boxes"></i>
                    </div>
                    <div>
                        <div class='metric-title'>Total Orders</div>
                        <div class='metric-value'>{len(orders_data)}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with metric_cols[1]:
            active_orders = [o for o in orders_data if o.get('status') in ['pending', 'confirmed', 'out_for_delivery']]
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon' style='background: #fff6e5; color: #f59e0b;'>
                        <i class="fas fa-shipping-fast"></i>
                    </div>
                    <div>
                        <div class='metric-title'>Active Orders</div>
                        <div class='metric-value'>{len(active_orders)}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with metric_cols[2]:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-icon' style='background: #eaf8f0; color: #10b981;'>
                        <i class="fas fa-sack-dollar"></i>
                    </div>
                    <div>
                        <div class='metric-title'>Total Sales (Admin)</div>
                        <div class='metric-value'>₹{sales_analytics_data.get('total_sales', 0):,.0f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with metric_cols[3]:
            st.markdown("""
                <div class='metric-card'>
                    <div class='metric-icon' style='background: #eef2ff; color: #4f46e5;'>
                        <i class="fas fa-star"></i>
                    </div>
                    <div>
                        <div class='metric-title'>Reward Points</div>
                        <div class='metric-value'>450</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # --- Recent Orders Section ---
        st.markdown("""
            <div class='section-container'>
                <div class='section-header'>
                    <span>Recent Orders</span>
                    <a href="#" class="view-all">View All</a>
                </div>
        """, unsafe_allow_html=True)
        
        if orders_data:
            for order in orders_data[:2]:
                order_items_text = ", ".join([item['cake_name'] for item in order.get('items', [])])
                status_class = 'status-in-transit' if order.get('status') == 'out_for_delivery' else 'status-preparing'
                
                # Use a try-except block to handle potential key errors from nested data
                try:
                    price_sum = sum(item['quantity'] for item in order.get('items', [])) * 100
                except (KeyError, TypeError):
                    price_sum = 0

                st.markdown(f"""
                    <div class='order-item-list'>
                        <div class='order-item-details'>
                            <span style='font-weight: 600;'>#ORD-{order.get('id')}</span>
                            <span>{order_items_text}</span>
                            <span>{order.get('created_at').split('T')[0]}</span>
                        </div>
                        <span class='order-price'>₹{price_sum}</span>
                        <span class='status-tag {status_class}'>{order.get('status', 'unknown').upper()}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent orders found.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(f"""
            <div class='profile-card'>
                <div class='profile-avatar'>
                    <i class="fas fa-user"></i>
                </div>
                <div class='profile-name'>{st.session_state.get('username')}</div>
                <div class='profile-email'>{user_profile_data.get('phone_number', 'N/A')}</div>
                <div class='rating-stars'>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star-half-alt"></i> 4.8 avg rating
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='section-container'>
                <div class='section-header'>
                    <span>Quick Actions</span>
                </div>
                <div class='action-item'>
                    <i class="fas fa-box"></i> My Orders
                </div>
                <div class='action-item'>
                    <i class="fas fa-heart"></i> Favorites
                </div>
                <div class='action-item'>
                    <i class="fas fa-bell"></i> Notifications
                </div>
                <div class='action-item'>
                    <i class="fas fa-user-lock"></i> Privacy Settings
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='loyalty-card'>
                <div class='loyalty-title'>Loyalty Rewards</div>
                <p>You have 450 points!</p>
                <div class='progress-bar-container'>
                    <div class='progress-bar' style='width: 75%;'></div>
                </div>
                <p>Progress to next reward</p>
                <div class='redeem-btn'>
                    <button>Redeem Points</button>
                </div>
            </div>
        """, unsafe_allow_html=True)'''


def main_page():
    st.title("📊 Dashboard")
    st.markdown("---")

    API_BASE_URL = "http://127.0.0.1:8000/api"
    headers = {"Authorization": f"Token {st.session_state.get('token', '')}"}

    # Analytics Section
    st.subheader("🌟 Your Sweet Analytics")
    
    # Create metrics columns
    metrics_cols = st.columns(4)
    
    # Mock analytics data (replace with real API calls)
    total_orders = 24
    total_spent = 12450
    favorite_cake = "Chocolate Truffle"
    loyalty_points = 340
    
    with metrics_cols[0]:
        st.metric(
            label="🛒 Total Orders", 
            value=str(total_orders),
            delta="2 this month"
        )
    
    with metrics_cols[1]:
        st.metric(
            label="💰 Total Spent", 
            value=f"₹{total_spent:,}",
            delta="₹850 this month"
        )
    
    with metrics_cols[2]:
        st.metric(
            label="🎂 Favorite Cake", 
            value=favorite_cake
        )
    
    with metrics_cols[3]:
        st.metric(
            label="⭐ Loyalty Points", 
            value=str(loyalty_points),
            delta="45 earned recently"
        )

    # Top Selling Cakes Chart
    st.markdown("### 📈 Your Cake Preferences")
    
    # Create sample data for user's cake ordering history
    cake_data = {
        'Cake': ['Chocolate Truffle', 'Red Velvet', 'Black Forest', 'Vanilla', 'Strawberry', 'Butterscotch'],
        'Orders': [8, 6, 4, 3, 2, 1]
    }
    
    import pandas as pd
    df = pd.DataFrame(cake_data)
    
    # Display as bar chart
    st.bar_chart(df.set_index('Cake')['Orders'])
    
    # Monthly spending trend
    st.markdown("### 💸 Monthly Spending Trend")
    
    spending_data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Amount': [800, 1200, 950, 1100, 1350, 850]
    }
    
    df_spending = pd.DataFrame(spending_data)
    st.line_chart(df_spending.set_index('Month')['Amount'])
    
    # Quick insights
    st.markdown("### 💡 Quick Insights")
    
    insights_cols = st.columns(2)
    
    with insights_cols[0]:
        st.info("🎯 You order most cakes on weekends! Perfect for celebrations.")
        st.success("🏆 You're in the top 15% of our loyal customers!")
    
    with insights_cols[1]:
        st.warning("📅 It's been 12 days since your last order. Missing something sweet?")
        st.info("🎁 You're 160 points away from a free cake!")

    st.markdown("---")

    # Fetch orders from backend
    try:
        res = requests.get(f"{API_BASE_URL}/orders/", headers=headers)
        orders = res.json() if res.status_code == 200 else []
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        orders = []

    if not orders:
        st.info("No orders found.")
        return

    st.subheader("Your Orders")

    # Filters: Active vs Past
    filt = st.segmented_control("Filter", options=["Active", "Past", "All"], default="Active")
    def is_active(o):
        return o.get('status') in ['pending','confirmed','out_for_delivery']
    if filt == 'Active':
        orders = [o for o in orders if is_active(o)]
    elif filt == 'Past':
        orders = [o for o in orders if not is_active(o)]

    for order in orders:
        order_id = order.get('id')
        status = order.get('status', '').capitalize()
        created = order.get('created_at', '').split('T')[0]
        eta = order.get('estimated_delivery_time', None)
        agent = order.get('agent', None)
        items = order.get('items', [])
        price_sum = order.get('total_amount')
        # If items or totals are missing, fetch the single order detail
        if (not items) or (not price_sum or price_sum <= 0):
            try:
                dres = requests.get(f"{API_BASE_URL}/orders/{order_id}/", headers=headers)
                if dres.status_code == 200:
                    d = dres.json()
                    items = d.get('items', items)
                    price_sum = d.get('total_amount', price_sum)
            except Exception:
                pass
        if not price_sum or price_sum <= 0:
            try:
                price_sum = sum((i.get('quantity',1) * (i.get('unit_price') or 0)) for i in items)
                if not price_sum or price_sum <= 0:
                    price_sum = sum(i.get('quantity',1) for i in items) * 100
            except Exception:
                price_sum = 0
        st.markdown(f"""
            <div style='border:1px solid #eee; border-radius:12px; padding:18px; margin-bottom:18px; box-shadow:0 2px 8px rgba(0,0,0,0.07); background:#fff;'>
                <div style='font-size:18px; font-weight:bold;'>Order #{order_id} <span style='color:#ff3c6f;'>{status}</span></div>
                <div style='margin-top:8px;'>Placed on: {created}</div>
                <div style='margin-top:8px;'>ETA: {eta if eta else 'N/A'}</div>
                <div style='margin-top:8px;'>Items: {', '.join([i.get('cake_name','Cake') for i in items])}</div>
                <div style='margin-top:8px;'>Total: ₹{price_sum}</div>
                <div style='margin-top:8px;'>Agent: {agent if agent else 'Not assigned'}</div>
            </div>
        """, unsafe_allow_html=True)
        cols = st.columns([1,1,1,1])
        with cols[0]:
            if status.lower() in ('pending','confirmed'):
                if st.button(f"Cancel #{order_id}", key=f"cancel_{order_id}"):
                    try:
                        cancel_res = requests.delete(f"{API_BASE_URL}/orders/{order_id}/cancel/", headers=headers)
                        if cancel_res.status_code == 200:
                            st.success("Order cancelled.")
                            st.rerun()
                        else:
                            st.error(cancel_res.json().get('detail','Failed to cancel'))
                    except Exception as e:
                        st.error(f"Error: {e}")
        with cols[1]:
            if st.button(f"Reorder #{order_id}", key=f"reorder_{order_id}"):
                try:
                    rr = requests.post(f"{API_BASE_URL}/orders/{order_id}/reorder/", headers=headers)
                    if rr.status_code == 200:
                        st.success("Items added to cart.")
                    else:
                        st.error("Could not add items to cart.")
                except Exception as e:
                    st.error(f"Error: {e}")
        with cols[2]:
            if status.lower() == 'out_for_delivery':
                if st.button(f"Track #{order_id}", key=f"track_{order_id}"):
                    st.session_state['track_order_id'] = order_id
                    st.session_state.page = 'map_demo'
                    st.rerun()
        with cols[3]:
            pass
