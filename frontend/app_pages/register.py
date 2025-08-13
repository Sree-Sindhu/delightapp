# frontend/pages/register.py
import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000/api/auth"

def register_page():
    with st.form("register_form"):
        st.subheader("Sign Up")
        full_name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email")
        gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])

        st.markdown("### 🏠 Address Details")
        flat_no = st.text_input("Flat / Apartment No.")
        building = st.text_input("Building / House Name")
        street = st.text_input("Street")
        area = st.text_input("Area or Colony")
        landmark = st.text_input("Landmark (Optional)")
        city = st.text_input("City")
        state = st.text_input("State")
        pincode = st.text_input("Pincode")
        # Defaulting lat/lon for now. These could be fetched via a Geo-API later.
        lat, lon = 0.0, 0.0

        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        register_submit = st.form_submit_button("Register")

        if register_submit:
            if password != confirm_password:
                st.error("🔐 Passwords do not match.")
            elif not all([full_name, mobile, email, flat_no, building, street, area, city, state, pincode, password]):
                st.error("🚫 Please fill in all the required fields.")
            else:
                # --- Construct the nested JSON payload for the backend ---
                username = email.split('@')[0]
                data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "first_name": full_name.split()[0],
                    "last_name": " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "",
                    "phone_number": mobile,
                    "gender": gender[0] if gender != "Prefer not to say" else "-",
                    "address": {
                        "flat_number": flat_no,
                        "building_name": building,
                        "street": street,
                        "area_or_colony": area,
                        "landmark": landmark,
                        "city": city,
                        "state": state,
                        "pincode": pincode,
                        "latitude": lat,
                        "longitude": lon,
                    }
                }

                try:
                    res = requests.post(f"{BASE_URL}/register/", json=data)
                    if res.status_code == 200 or res.status_code == 201:
                        st.success("🎉 Registration successful! Welcome to DelightAPI!")
                        # Auto login the user and redirect to home
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.session_state["email"] = email
                        st.session_state["page"] = "home"
                        st.rerun()
                    else:
                        st.error(f"❌ Registration failed: {res.json().get('error', res.text)}")
                except Exception as e:
                    st.error(f"⚠️ Could not connect to backend: {e}")
