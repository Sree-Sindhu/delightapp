import streamlit as st
import base64
import datetime

st.set_page_config(page_title="DelightAPI", page_icon="🎂", layout="wide")

# Set background image
def set_bg():
    with open("background.jpg", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .nav-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px 40px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            position: sticky;
            top: 0;
            z-index: 999;
        }}
        .nav-title {{
            font-size: 28px;
            color: #6c3483;
            font-weight: bold;
            font-family: 'Georgia', serif;
        }}
        .nav-buttons button {{
            margin-left: 20px;
            background-color: #ff6f91;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            transition: background 0.2s ease-in-out;
        }}
        .nav-buttons button:hover {{
            background-color: #ff3c6f;
        }}
        .cake-img {{
            border-radius: 12px;
            width: 180px;
            height: 180px;
            object-fit: cover;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.2);
            transition: transform 0.2s ease-in-out;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        .cake-img:hover {{
            transform: scale(1.05);
        }}
        .cake-title {{
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            color: #6c3483;
            margin-top: 5px;
        }}
        </style>
    """, unsafe_allow_html=True)

set_bg()

# Navigation State
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Top Navigation Bar (without Home button)
st.markdown(f"""
    <div class="nav-container">
        <div class="nav-title">🎂 DelightAPI</div>
        <div class="nav-buttons">
            <form action="#">
                <button name="custom" formaction="?custom">Customize</button>
                <button name="track" formaction="?track">Track Order</button>
                <button name="support" formaction="?support">Support</button>
            </form>
        </div>
    </div>
""", unsafe_allow_html=True)

# Routing
query_params = st.query_params
if 'custom' in query_params:
    st.session_state.page = 'Customize'
elif 'track' in query_params:
    st.session_state.page = 'Track'
elif 'support' in query_params:
    st.session_state.page = 'Support'
else:
    st.session_state.page = 'Home'

# Pages
def home_page():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#ff6f91;'>Craft your dream cake from scratch 🎨✨</h2>", unsafe_allow_html=True)
    st.markdown("---")

    cake_data = [
        ("hazelnutcake.jpeg", "Hazelnut Cake"),
        ("chocolate_cake.jpeg", "Chocolate Cake"),
        ("fruit_cake.jpeg", "Fruit Cake"),
        ("custom_cake.jpeg", "Custom Cake"),
        ("italianforest.jpeg", "Italian Forest"),
        ("blackforest.jpeg", "Black Forest"),
        ("icecream.jpeg", "Ice Cream Cake"),
        ("redvelvet.jpeg", "Red Velvet"),
        ("black_current.jpeg", "Black Current Cake"),
    ]

    for i in range(0, len(cake_data), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(cake_data):
                img, name = cake_data[i + j]
                with cols[j]:
                    cake_link = name.replace(" ", "_")
                    st.markdown(f"""
                        <a href="/pages/1_Store_Listings?cake={cake_link}" target="_self">
                            <img src="data:image/jpeg;base64,{base64.b64encode(open('images/' + img, 'rb').read()).decode()}" class="cake-img">
                        </a>
                        <div class="cake-title">{name}</div>
                    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎁 Flash Sale Countdown")
    end_time = datetime.datetime(2025, 7, 25, 23, 59, 59)
    remaining = end_time - datetime.datetime.now()
    d, s = remaining.days, remaining.seconds
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    st.markdown(f"⏳ Ends in: `{d}d {h}h {m}m {s}s`")
    st.write("- 🍫 10% off Chocolate Cakes")
    st.write("- 🎂 Free delivery on ₹500+")

def customize_page():
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎨 Customize Your Cake")

    st.markdown("#### Choose Flavor")
    flavors = ["Hazelnut Cake", "Chocolate Cake", "Fruit Cake", "Italian Forest", "Black Forest", "Ice Cream Cake", "Red Velvet", "Black Current Cake"]
    selected_flavor = st.selectbox("Flavor", flavors)

    st.markdown("#### Cake Size")
    size = st.radio("Choose size", ["Half kg", "1 kg", "1.5 kg", "2 kg", "3 kg"])

    st.markdown("#### Theme Color")
    color = st.color_picker("Select theme color")

    st.markdown("#### Message on Cake")
    message = st.text_input("Type a short message (e.g. Happy Birthday!)")

    st.markdown("#### Delivery Date")
    date = st.date_input("Select a delivery date", min_value=datetime.date.today())

    if st.button("Submit Custom Cake"):
        st.success(f"🎉 Your {selected_flavor} cake order has been submitted!")

    st.markdown("---")
    st.subheader("💡 Have a Custom Cake Idea?")
    note = st.text_area("Describe your unique idea (design, theme, etc.):")
    if st.button("Submit Idea"):
        if note.strip():
            st.success("✅ Your custom cake idea has been received!")
        else:
            st.error("⚠️ Please enter something.")

def track_page():
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📦 Track Your Order")
    order_id = st.text_input("Enter your Order ID:")
    if st.button("Track"):
        if order_id:
            st.info(f"Tracking order #{order_id}... Feature coming soon!")
        else:
            st.warning("Please enter a valid Order ID.")

def support_page():
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📞 Contact Support")
    st.write("For assistance, reach us at:")
    st.markdown("- 📧 support@delightapi.com")
    st.markdown("- 📱 +91-9876543210")
    st.map({"lat": [17.385044], "lon": [78.486671]})

# Page Renderer
if st.session_state.page == 'Home':
    home_page()
elif st.session_state.page == 'Customize':
    customize_page()
elif st.session_state.page == 'Track':
    track_page()
elif st.session_state.page == 'Support':
    support_page()

# Footer
st.markdown("---")
st.markdown("<center><small>© 2025 DelightAPI</small></center>", unsafe_allow_html=True)