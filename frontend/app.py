import streamlit as st
import base64
import requests
import os
from pages import home # <<< NEW: Import the home_page function from home.py

BASE_URL = "http://127.0.0.1:8000/api/auth"

# --- Page Configuration ---
# This must be the very first Streamlit command
st.set_page_config(page_title="DelightAPI - Access", layout="wide")

# --- Function to load and encode image ---
def get_base64_image(image_path):
    """Loads an image from the given path and returns its base64 encoded string."""
    if not os.path.exists(image_path):
        st.warning(f"Image not found: {image_path}")
        return ""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# --- Load image (ensure this is called before its use in st.markdown) ---
# Make sure 'register_login.webp' exists in the same directory as app.py
img_base64 = get_base64_image("register_login.webp")

# --- Custom CSS to force light mode and hide settings ---
# Using f-string to inject img_base64 directly into the CSS
st.markdown(f"""
    <style>
    /* Force the entire HTML document to use light color scheme */
    html {{
        color-scheme: light !important;
    }}

    /* Ensure the body and main Streamlit app container adhere to light background */
    body {{
        background-color: #ffffff !important; /* Fallback white background */
    }}
    .stApp {{
        background-color: #ffffff !important; /* Fallback white background for the app */
        background-image: url("data:image/webp;base64,{img_base64}"); /* Corrected background image URL */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* Hide the entire toolbar which typically contains the hamburger menu and other default Streamlit header elements */
    div[data-testid="stToolbar"] {{
        display: none !important;
        visibility: hidden !important; /* Adding visibility hidden as an extra measure */
        height: 0 !important; /* Collapse space */
    }}

    /* Hide the three-dots menu button itself (redundant if stToolbar is hidden, but good for robustness) */
    button[data-testid="baseButton-header"] {{
        display: none !important;
    }}

    /* Hide the entire settings dialog if it pops up, using its data-testid */
    div[data-testid="stConfigDialog"] {{
        display: none !important;
        visibility: hidden !important; /* Adding visibility hidden as an extra measure */
        height: 0 !important; /* Collapse space */
    }}
    
    /* Ensure the main content block has a light, translucent background */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.85); /* Light translucent background */
        padding: 3rem 2rem;
        border-radius: 1rem;
        max-width: 600px;
        margin: 5rem auto;
        box-shadow: 0 0 25px rgba(0,0,0,0.1);
    }}
    .form-title {{
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: #8e44ad; /* A shade of purple */
        margin-bottom: 1.5rem;
    }}
    button[kind="primary"] {{
        background-color: #e63946; /* Red */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 1rem;
        width: 100%;
        border: none;
        font-size: 1rem;
    }}
    button[kind="primary"]:hover {{
        background-color: #c62828; /* Darker red on hover */
    }}
    a {{
        color: #007bff; /* Blue */
        text-decoration: none;
        font-size: 0.9rem;
    }}
    a:hover {{
        text-decoration: underline;
    }}
    </style>
    <head>
        <meta name="color-scheme" content="light">
    </head>
""", unsafe_allow_html=True)

# --- Session State for Page Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "login" # Default to login page

# --- Page Switchers ---
def switch_to_register():
    st.session_state.page = "register"

def switch_to_login():
    st.session_state.page = "login"

def switch_to_home(): # <<< NEW: Function to switch to home page
    st.session_state.page = "home"

# --- Main Application Logic ---
# If logged in, show the home page; otherwise, show login/register
if st.session_state.get("logged_in"): # <<< MODIFIED: Check if 'logged_in' is True
    # Display the home page content
    home(st.session_state.get('email', 'User')) # Pass user email to home page

    # Add a logout button on the home page
    if st.button("Logout"):
        try:
            headers = {'Authorization': f'Token {st.session_state.token}'}
            requests.post(f"{BASE_URL}/logout/", headers=headers)
        except Exception as e:
            st.warning(f"Could not log out from backend: {e}")

        # Clear session state and redirect to login
        del st.session_state["token"]
        del st.session_state["logged_in"]
        del st.session_state["email"]
        st.session_state.page = "login"
        st.rerun()

else: # Not logged in, show login/register forms
    with st.container():
        st.markdown('<div class="form-title">🍰 DelightAPI</div>', unsafe_allow_html=True)

        if st.session_state.page == "login":
            with st.form("login_form"):
                st.subheader("Sign In")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                login_submit = st.form_submit_button("Sign In")

                if login_submit:
                    if not email.strip() or not password.strip():
                        st.error("🚫 Please enter both email and password.")
                    else:
                        data = {
                            "username": email.split('@')[0],
                            "password": password
                        }

                        try:
                            res = requests.post(f"{BASE_URL}/login/", json=data)
                            if res.status_code == 200:
                                token = res.json().get("token")
                                st.success("✅ Login successful!")
                                st.session_state["token"] = token
                                st.session_state["logged_in"] = True
                                st.session_state["email"] = email
                                st.session_state.page = "home" # <<< NEW: Switch to home page on successful login
                                st.rerun()
                            else:
                                st.error(f"❌ Invalid credentials. {res.json().get('error', '')}")
                        except requests.exceptions.ConnectionError:
                            st.error("⚠️ Could not connect to backend. Please ensure the Django server is running.")
                        except Exception as e:
                            st.error(f"⚠️ An unexpected error occurred: {e}")

            st.button("New user? Sign Up", on_click=switch_to_register)

        elif st.session_state.page == "register":
            with st.form("register_form"):
                st.subheader("Sign Up")
                full_name = st.text_input("Full Name")
                mobile = st.text_input("Mobile Number")
                address = st.text_area("Address")
                email = st.text_input("Email")
                gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
                location = st.selectbox("Select Location", ["Hyderabad", "Bangalore", "Mumbai"])
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                register_submit = st.form_submit_button("Register")

                if register_submit:
                    if not all([full_name.strip(), mobile.strip(), address.strip(), email.strip(), password.strip(), confirm_password.strip()]):
                        st.error("🚫 Please fill in all the required fields.")
                    elif password != confirm_password:
                        st.error("🔐 Passwords do not match.")
                    else:
                        username = email.split('@')[0]
                        data = {
                            "username": username,
                            "email": email,
                            "password": password,
                            "first_name": full_name.split()[0],
                            "last_name": " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "",
                            "phone_number": mobile,
                            "gender": gender[0],
                            "address": address
                        }

                        try:
                            res = requests.post(f"{BASE_URL}/register/", json=data)
                            if res.status_code == 200 or res.status_code == 201:
                                st.success("🎉 Registered successfully! Please log in.")
                                st.session_state.page = "login"
                                st.rerun()
                            else:
                                st.error(f"❌ Registration failed: {res.json().get('error', 'Unknown error')}")
                        except requests.exceptions.ConnectionError:
                            st.error("⚠️ Could not connect to backend. Please ensure the Django server is running.")
                        except Exception as e:
                            st.error(f"⚠️ An unexpected error occurred: {e}")

            st.button("Already have an account? Sign In", on_click=switch_to_login)

    st.markdown('</div>', unsafe_allow_html=True)
