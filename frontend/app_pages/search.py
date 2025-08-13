import streamlit as st
import requests
from .data import CAKES, STORES, STORE_DETAILS
from .utils import fake_geocode, haversine_km


def main_page():
    st.title("🔎 Search")
    tabs = st.tabs(["Cakes", "Stores"])
    with tabs[0]:
        q = st.text_input("Search cakes by name", key="search_cakes").strip().lower()
        results = [c for c in CAKES if not q or q in c['name'].lower()]
        if not results:
            st.info("No cakes found")
        cols = st.columns(3)
        for i, c in enumerate(results):
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(c['name'])
                    st.caption(f"Price: ₹{int(c['price'])}")
                    if st.button("View stores", key=f"sr_cake_{c['id']}"):
                        st.session_state.highlight_cake_id = c['id']
                        st.session_state.page = 'stores'
                        st.rerun()
    with tabs[1]:
        q2 = st.text_input("Search stores by name", key="search_stores").strip().lower()
        # Filters row
        fcols = st.columns(4)
        with fcols[0]:
            min_rating = st.slider("Min rating", 3.0, 5.0, 3.5, 0.1)
        with fcols[1]:
            max_distance = st.slider("Max distance (km)", 1.0, 20.0, 8.0, 0.5)
        with fcols[2]:
            area = st.text_input("Area filter (optional)", key="area_filter").strip().lower()
        with fcols[3]:
            min_reviews = st.slider("Min reviews", 0, 5000, 200, 50)

        # Determine user's location
        API_BASE_URL = "http://127.0.0.1:8000/api"
        headers = {"Authorization": f"Token {st.session_state.get('token', '')}"}
        user_latlon = None
        try:
            addr_res = requests.get(f"{API_BASE_URL}/addresses/", headers=headers)
            addrs = addr_res.json() if addr_res.status_code == 200 else []
            if addrs:
                a = addrs[0]
                user_latlon = fake_geocode(
                    f"{a.get('flat_number','')} {a.get('building_name','')} {a.get('street','')} {a.get('area_or_colony','')} {a.get('city','')} {a.get('state','')} {a.get('pincode','')}",
                    a.get('city','')
                )
        except Exception:
            user_latlon = None

        def store_passes_filters(sid: str, name: str):
            det = STORE_DETAILS.get(sid)
            if not det:
                return False
            if q2 and (q2 not in name.lower()):
                return False
            if area and (area not in (det.get('area','').lower())):
                return False
            if det.get('rating', 0) < min_rating:
                return False
            if det.get('reviews', 0) < min_reviews:
                return False
            if user_latlon:
                s_lat, s_lon = fake_geocode(det.get('address',''), det.get('city',''))
                dist = haversine_km(user_latlon[0], user_latlon[1], s_lat, s_lon)
                if dist > max_distance:
                    return False
            return True

        results2 = [(sid, nm) for sid, nm in STORES.items() if store_passes_filters(sid, nm)]
        if not results2:
            st.info("No stores found")
        cols2 = st.columns(3)
        for i, (sid, nm) in enumerate(results2):
            with cols2[i % 3]:
                with st.container(border=True):
                    st.subheader(nm)
                    det = STORE_DETAILS.get(sid, {})
                    if det.get('area'):
                        st.caption(det['area'])
                    if det.get('rating'):
                        st.caption(f"⭐ {det['rating']} · {det.get('reviews', 0)} reviews")
                    if user_latlon:
                        s_lat, s_lon = fake_geocode(det.get('address',''), det.get('city',''))
                        dist = haversine_km(user_latlon[0], user_latlon[1], s_lat, s_lon)
                        st.caption(f"📏 ~{dist:.1f} km away")
                    if st.button("Open", key=f"sr_store_{sid}"):
                        st.session_state.store_id = sid
                        st.session_state.page = 'store_detail'
                        st.rerun()
