import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000/api/auth"

def login_page():
    if not st.session_state.get("show_reset_form"):
        with st.form("login_form"):
            st.subheader("Sign In")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In")

            if login_submit:
                if not email.strip() or not password.strip():
                    st.error("🚫 Please enter both email and password.")
                else:
                    data = {"username": email.split('@')[0], "password": password}
                    try:
                        res = requests.post(f"{BASE_URL}/login/", json=data)
                        if res.status_code == 200:
                            token = res.json().get("token")
                            st.session_state["token"] = token
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = email.split('@')[0]
                            st.session_state["email"] = email
                            # Ensure we land on Home after login, regardless of current shell
                            st.session_state["page"] = "home"
                            st.success("✅ Login successful! Redirecting to home...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials.")
                    except Exception as e:
                        st.error(f"⚠️ Could not connect to backend: {e}")
        
        st.button("Forgot Password?", on_click=lambda: st.session_state.update(show_reset_form=True), key="forgot_password_btn")
    else:
        # Password reset form
        st.subheader("Reset Password")
        with st.form("reset_password_form"):
            phone_number = st.text_input("Enter your phone number")
            new_password = st.text_input("Enter new password", type="password")
            reset_submit = st.form_submit_button("Reset Password")
            
            if reset_submit:
                if not phone_number or not new_password:
                    st.error("Please fill all fields.")
                else:
                    # TODO: Call your backend API for password reset
                    # This API endpoint needs to be created on the backend
                    st.success("Password reset request sent. Check your phone.")
                    st.session_state.show_reset_form = False
                    st.rerun()
        
        st.button("Back to Login", on_click=lambda: st.session_state.update(show_reset_form=False))