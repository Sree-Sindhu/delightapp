# frontend/app.py
import streamlit as st
import base64
import os
from app_pages import login, register, home

# --- Session State for Page Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "auto"
active_theme = st.session_state.ui_theme

# --- Page Configuration and Styling ---
st.set_page_config(page_title="DelightAPI", layout="wide")

def get_base64_image(image_path: str) -> str:
    """Return base64 string for an image path or empty string if missing."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return ""

def resolve_login_image() -> str:
    """Find a login background image inside the local images folder.
    Preference order: login.jpeg, login.jpg, login.png, first file containing 'login' in name, else ''.
    Returns absolute file path or '' if not found.
    """
    # app.py lives in frontend/, images folder is frontend/images
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    if not os.path.isdir(images_dir):
        st.warning("'images' folder not found next to app.py")
        return ''
    candidates = [
        os.path.join(images_dir, "login.jpeg"),
        os.path.join(images_dir, "login.jpg"),
        os.path.join(images_dir, "login.png"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    # fallback: any file with 'login' in name
    for fname in os.listdir(images_dir):
        if 'login' in fname.lower():
            fpath = os.path.join(images_dir, fname)
            if os.path.isfile(fpath):
                return fpath
    return ''

image_file_path = resolve_login_image()
img_base64 = get_base64_image(image_file_path) if image_file_path else ""
if not img_base64:
    st.warning("Login background image not found. Place 'login.jpeg' (or .jpg/.png) in the images folder.")

st.markdown(f"""
    <style>
    .stApp {{
        {f'background-image: url("data:image/jpeg;base64,{img_base64}");' if img_base64 else 'background: linear-gradient(135deg,#000080,#ff3c6f);'}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 100vh;
        position: relative;
    }}
    .stApp:before {{ /* subtle dark overlay for readability */
        content: '';
        position: absolute; inset:0;
        background: rgba(0,0,0,0.15);
        pointer-events:none;
    }}
    body.theme-dark .stApp:before {{
        background: rgba(0,0,0,0.35);
    }}
    /* Make the main block full-width with comfortable padding */
    .block-container {{
        max-width: 100% !important;
        padding: 2rem 3.5rem 4rem 3.5rem;
        margin: 0 auto;
        background: rgba(255,255,255,0.78);
        backdrop-filter: blur(6px) saturate(135%);
        -webkit-backdrop-filter: blur(6px) saturate(135%);
        border-radius: 0;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.55), 0 10px 40px -12px rgba(0,0,0,0.45);
        position: relative;
        z-index: 1;
        transition: background .35s ease; 
    }}
    body.theme-dark .block-container {{
        background: rgba(18,20,26,0.70);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06), 0 14px 48px -14px rgba(0,0,0,0.75);
    }}
    /* Optional utility wrapper for centering small forms if needed */
    .narrow-form {{
        max-width: 760px;
        margin: 0 auto 3rem auto;
        padding: 2.2rem 2.4rem 2.6rem;
        background: #ffffffee;
        border: 1px solid #ececec;
        box-shadow: 0 4px 18px -6px rgba(0,0,0,0.12);
        border-radius: 18px;
    }}
    .form-title {{
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #8e44ad;
        margin: 0 0 1.25rem 0;
        letter-spacing: .5px;
    }}
    .landing-hero h2 {{
        font-size: 2.4rem;
        margin-bottom: .4rem;
        line-height: 1.15;
        background: linear-gradient(90deg,#ff3c6f,#000080);
        -webkit-background-clip: text;
        color: transparent;
    }}
    .landing-hero p {{
        font-size: 1.05rem;
        opacity: .85;
        margin-bottom: 2rem;
    }}
    .landing-actions .stButton > button {{
        background: linear-gradient(90deg,#000080,#ff3c6f);
        color:#fff;
        font-weight:600;
        border:none;
        padding: .9rem 1.4rem;
        border-radius: 10px;
        font-size:1rem;
        transition: all .18s ease;
        width:100%;
        box-shadow:0 4px 12px -3px rgba(0,0,0,0.25);
    }}
    .landing-actions .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow:0 8px 20px -5px rgba(0,0,0,0.35);
        background: linear-gradient(90deg,#ff3c6f,#000080);
    }}
    .two-col-auth {{
        display: grid;
        grid-template-columns: repeat(auto-fit,minmax(320px,1fr));
        gap: 2.2rem;
        align-items: start;
        margin-top: 1.2rem;
    }}
    .feature-grid {{
        display:grid;
        gap:1.2rem;
        grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
        margin: 2.2rem 0 1rem;
    }}
    .feature-card {{
        background:rgba(255,255,255,0.85);
        border:1px solid #ececec;
        padding:1rem .9rem 1.15rem;
        border-radius:16px;
        box-shadow:0 4px 16px -6px rgba(0,0,0,0.15);
        transition:.18s;
        backdrop-filter:blur(4px) saturate(140%);
    }}
    body.theme-dark .feature-card {{
        background:rgba(28,32,40,0.72);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 6px 20px -8px rgba(0,0,0,0.85);
    }}
    .feature-card:hover {{
        transform:translateY(-4px);
        box-shadow:0 6px 18px -5px rgba(0,0,0,0.18);
        border-color:#ff3c6f55;
    }}
    body.theme-dark .feature-card:hover {{
        border-color:#ff3c6f99;
        box-shadow:0 10px 26px -8px rgba(0,0,0,0.9);
    }}
    </style>
     <script>
     (function() {{
         try {{
            const b = (window.parent && window.parent.document && window.parent.document.body) || document.body;
            b.classList.remove('theme-dark','theme-light');
            const mode = '{active_theme}';
            if (mode === 'dark') {{ b.classList.add('theme-dark'); }}
            else if (mode === 'light') {{ b.classList.add('theme-light'); }}
            else {{
                const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                b.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
            }}
         }} catch(e) {{ console.warn('theme script', e); }}
     }})();
     </script>
""", unsafe_allow_html=True)

# --- Navigation Logic ---
if st.session_state.logged_in:
    home.main_page()
else:
    st.markdown('<div class="form-title">🍰 Welcome to DelightAPI!</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="landing-hero">
            <h2>Fresh, Customized Cakes Delivered Fast</h2>
            <p>Create, personalize, track and enjoy – all in one seamless experience.</p>
        </div>
    """, unsafe_allow_html=True)

    # Feature highlight grid (optional visual richness)
    st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">🎨 Custom Designs<br><small>Personalize messages & styles.</small></div>
            <div class="feature-card">🚚 Live Tracking<br><small>Know where your cake is.</small></div>
            <div class="feature-card">🛒 Smart Cart<br><small>Update items in real time.</small></div>
            <div class="feature-card">⭐ Reviews<br><small>Trusted by dessert lovers.</small></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='landing-actions'></div>", unsafe_allow_html=True)
    auth_cols = st.columns(2)
    with auth_cols[0]:
        if st.button("Login", key="landing_login"):
            st.session_state.page = "login"
            st.rerun()
    with auth_cols[1]:
        if st.button("Register", key="landing_register"):
            st.session_state.page = "register"
            st.rerun()

    if st.session_state.page == "login":
        login.login_page()
    elif st.session_state.page == "register":
        register.register_page()
