import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000/api"


def _headers():
    return {"Authorization": f"Token {st.session_state.get('token', '')}"}


def get_or_create_cake_id(name: str, price: float, size: str = "1 kg", flavor: str = "classic"):
    """Resolve a Cake PK by exact name from backend. If missing, do NOT auto-create here.
    Returns integer id or None if not found.
    """
    try:
        res = requests.get(f"{API_BASE_URL}/cakes/", headers=_headers())
        if res.status_code == 200:
            for c in res.json():
                if c.get('name') == name:
                    return c.get('id')
    except Exception as e:
        st.error(f"Error resolving cake: {e}")
        return None
    # Not found; advise seeding backend data
    st.error("Cake not found on backend. Please seed demo data: manage.py seed_demo")
    return None


def ensure_custom_cake_id(name: str, price: float, size: str, flavor: str):
    """Resolve a 'Custom Cake' on the backend without creating new records.
    Returns the id of an existing cake whose name matches (case-insensitive).
    If not found, returns None and shows a hint to seed one.
    """
    try:
        res = requests.get(f"{API_BASE_URL}/cakes/", headers=_headers())
        if res.status_code == 200:
            for c in res.json():
                nm = str(c.get('name',''))
                if nm.lower() == name.lower():
                    return c.get('id')
        st.error("No 'Custom Cake' exists on backend. Please create one in admin or seed demo data.")
        return None
    except Exception as e:
        st.error(f"Error resolving custom cake: {e}")
        return None
