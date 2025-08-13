# frontend/app_pages/stores.py
import streamlit as st
import requests
from .data import STORES, CAKES, CUSTOM_CAKE_STORES, STORE_DETAILS
from .utils import fake_geocode, haversine_km


def _search_box(label: str):
    q = st.text_input(label, key=f"{label}_q").strip()
    return q.lower()


def main_page():
    st.header("🏬 Our Stores")
    # Filters row
    f1, f2, f3, f4 = st.columns([3,2,2,2])
    with f1:
        q = _search_box("Search stores")
    with f2:
        min_rating = st.slider("Min rating", 0.0, 5.0, 0.0, 0.1)
    with f3:
        min_reviews = st.slider("Min reviews", 0, 5000, 0, 50)
    with f4:
        near_me = st.toggle("Near me", value=False)

    items = [(sid, name) for sid, name in STORES.items() if (not q or q in name.lower() or q in sid.lower())]

    # Optional cake filter: when user selects a cake elsewhere
    cake_filter_id = st.session_state.get('selected_cake_for_store')
    if cake_filter_id:
        cake_obj = next((c for c in CAKES if c.get('id') == cake_filter_id), None)
        allowed = set(cake_obj.get('stores', [])) if cake_obj else set()
        items = [(sid, name) for sid, name in items if sid in allowed]

    if not items:
        st.info("No stores found.")
        return

    # Determine user's location from first saved address if available
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

    # Determine distances if needed
    distances = {}
    if near_me and user_latlon:
        for sid, _ in items:
            det = STORE_DETAILS.get(sid)
            if det:
                s_lat, s_lon = fake_geocode(det.get('address',''), det.get('city',''))
                distances[sid] = haversine_km(user_latlon[0], user_latlon[1], s_lat, s_lon)
        # sort items by distance
        items = sorted(items, key=lambda x: distances.get(x[0], 1e9))

    # Apply rating/reviews filters from metadata (STORE_DETAILS)
    def passes_meta_filters(sid: str) -> bool:
        det = STORE_DETAILS.get(sid, {})
        if det.get('rating', 0) < min_rating:
            return False
        if det.get('reviews', 0) < min_reviews:
            return False
        return True

    items = [(sid, name) for sid, name in items if passes_meta_filters(sid)]

    cols = st.columns(3)
    for idx, (store_id, store_name) in enumerate(items):
        with cols[idx % 3]:
            with st.container(border=True):
                st.subheader(store_name)
                details = STORE_DETAILS.get(store_id)
                if details and details.get('area'):
                    st.caption(f"{details.get('area')}")
                # Rating & reviews
                if details and details.get('rating'):
                    st.caption(f"⭐ {details['rating']} · {details.get('reviews', 0)} reviews")
                offers_custom = store_id in CUSTOM_CAKE_STORES
                st.markdown(
                    f"<small>Custom Cakes: {'✅ Available' if offers_custom else '❌ Not available'}</small>",
                    unsafe_allow_html=True,
                )
                # Address details
                details = STORE_DETAILS.get(store_id)
                if details:
                    st.caption(f"📍 {details.get('address')}")
                # Distance from user (approx)
                if user_latlon and details:
                    dist_km = distances.get(store_id)
                    if dist_km is None:
                        s_lat, s_lon = fake_geocode(details.get('address',''), details.get('city',''))
                        dist_km = haversine_km(user_latlon[0], user_latlon[1], s_lat, s_lon)
                    st.caption(f"📏 ~{dist_km:.1f} km away")
                # Count cakes available
                available_cakes = [c for c in CAKES if store_id in c.get('stores', [])]
                st.markdown(f"<small>Cakes available: <strong>{len(available_cakes)}</strong></small>", unsafe_allow_html=True)
                if st.button("🏪\nView Catalog", key=f"open_store_detail_{store_id}"):
                    st.session_state.store_id = store_id
                    # clear the cake filter once navigating into a store
                    if 'selected_cake_for_store' in st.session_state:
                        del st.session_state['selected_cake_for_store']
                    st.session_state.page = 'store_detail'
                    st.rerun()

    # Removed below-the-fold catalog; now use dedicated Store Detail page
