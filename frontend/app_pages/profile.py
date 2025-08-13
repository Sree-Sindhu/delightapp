import streamlit as st
import requests


API_BASE_URL = "http://127.0.0.1:8000/api"


def main_page():
    st.title("👤 Profile & Addresses")
    st.caption("Update your details like in delivery apps")
    st.markdown("---")
    # floating chips are rendered globally in home wrapper

    headers = {"Authorization": f"Token {st.session_state.get('token', '')}"}

    # Fetch profile
    profile_data = {}
    try:
        res = requests.get(f"{API_BASE_URL}/auth/profile/", headers=headers)
        if res.status_code == 200:
            profile_data = res.json() or {}
    except Exception:
        pass

    # Profile card
    with st.container(border=True):
        st.subheader("User Details")
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone number", profile_data.get('phone_number', ''))
            gender = st.selectbox("Gender", ['-','M','F','O'], index=['-','M','F','O'].index(profile_data.get('gender','-')))
            first_name = st.text_input("First name", profile_data.get('first_name', st.session_state.get('username','')))
        with col2:
            last_name = st.text_input("Last name", profile_data.get('last_name', ''))
            st.text_input("Email (unique)", st.session_state.get('email', ''), disabled=True)

    if st.button("Save profile"):
        try:
            payload = {"phone_number": phone, "gender": gender, "first_name": first_name, "last_name": last_name}
            upd = requests.put(f"{API_BASE_URL}/auth/profile/", headers=headers, json=payload)
            if upd.status_code in (200, 202):
                st.success("Profile updated")
                # Reflect the changed name locally
                st.session_state['username'] = first_name or st.session_state.get('username')
            else:
                st.error("Failed to update profile")
        except Exception as e:
            st.error(f"Error: {e}")

    # Password change
    with st.expander("🔐 Change Password"):
        cp1, cp2 = st.columns(2)
        with cp1:
            current_pw = st.text_input("Current password", type="password")
        with cp2:
            new_pw = st.text_input("New password", type="password")
        if st.button("Update password"):
            try:
                pr = requests.put(f"{API_BASE_URL}/auth/change-password/", headers=headers, json={
                    "current_password": current_pw,
                    "new_password": new_pw,
                })
                if pr.status_code == 200:
                    st.success("Password updated")
                else:
                    msg = pr.json().get('error') if pr.headers.get('content-type','').startswith('application/json') else 'Failed to update password'
                    st.error(msg or 'Failed to update password')
            except Exception as e:
                st.error(f"Error: {e}")

    # Account actions
    st.markdown("---")
    st.subheader("Account")
    a1, a2 = st.columns(2)
    with a1:
        if st.button("🔓 Logout"):
            try:
                requests.post(f"{API_BASE_URL}/auth/logout/", headers=headers)
            except Exception:
                pass
            # Clear local session regardless of API outcome
            for k in ['token', 'username', 'email']:
                if k in st.session_state:
                    del st.session_state[k]
            st.success("Logged out")
            st.session_state.logged_in = False
            st.session_state.page = 'login'
            st.rerun()
    with a2:
        with st.expander("⚠️ Delete account (irreversible)"):
            confirm = st.checkbox("I understand this will permanently delete my account")
            if st.button("🗑️ Delete my account", type="primary", disabled=not confirm):
                try:
                    dr = requests.delete(f"{API_BASE_URL}/auth/delete-account/", headers=headers)
                    if dr.status_code in (200, 204):
                        st.success("Account deleted")
                        for k in list(st.session_state.keys()):
                            if k in ['token', 'username', 'email', 'page']:
                                del st.session_state[k]
                        st.session_state.page = 'home'
                        st.rerun()
                    else:
                        st.error("Failed to delete account")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    # Addresses
    st.subheader("Delivery Addresses")
    addresses = []
    try:
        addr_res = requests.get(f"{API_BASE_URL}/addresses/", headers=headers)
        if addr_res.status_code == 200:
            addresses = addr_res.json() or []
    except Exception:
        pass

    # List addresses
    if addresses:
        for a in addresses:
            with st.container(border=True):
                st.write(f"{a.get('flat_number','')} {a.get('building_name','')}")
                st.write(f"{a.get('street','')}, {a.get('area_or_colony','')}")
                st.write(f"{a.get('city','')}, {a.get('state','')} - {a.get('pincode','')}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Delete", key=f"del_addr_{a['id']}"):
                        try:
                            d = requests.delete(f"{API_BASE_URL}/addresses/{a['id']}/", headers=headers)
                            if d.status_code == 204:
                                st.success("Address deleted")
                                st.rerun()
                            else:
                                st.error("Failed to delete address")
                        except Exception as e:
                            st.error(f"Error: {e}")
                with c2:
                    pass
    else:
        st.info("No addresses. Add one below.")

    # Add new address
    with st.expander("➕ Add Address", expanded=True):
        a1, a2 = st.columns(2)
        with a1:
            flat = st.text_input("Flat/House No.")
            build = st.text_input("Building/Apartment")
            street = st.text_input("Street")
            area = st.text_input("Area/Colony")
            city = st.text_input("City")
        with a2:
            state = st.text_input("State")
            pincode = st.text_input("Pincode")
            landmark = st.text_input("Landmark (optional)")
        if st.button("Save address"):
            payload = {
                "flat_number": flat,
                "building_name": build,
                "street": street,
                "area_or_colony": area,
                "city": city,
                "state": state,
                "pincode": pincode,
                "landmark": landmark,
            }
            try:
                cr = requests.post(f"{API_BASE_URL}/addresses/", headers=headers, json=payload)
                if cr.status_code in (200, 201):
                    st.success("Address added")
                    st.rerun()
                else:
                    st.error("Failed to add address")
            except Exception as e:
                st.error(f"Error: {e}")
