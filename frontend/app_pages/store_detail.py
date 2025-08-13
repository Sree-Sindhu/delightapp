# frontend/app_pages/store_detail.py
import base64
import os
import streamlit as st
import requests
from .data import STORES, CAKES, CAKE_SIZES
from .api_helpers import get_or_create_cake_id


def _cakes_for_store(store_id: str):
    mapped = [c for c in CAKES if store_id in c.get('stores', [])]
    if mapped:
        return mapped
    # Fallback: show popular cakes if store has no explicit mapping
    # Choose a stable subset (first 9) to keep UI predictable
    return CAKES[:9]


def _img_src(filename: str):
    images_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'images'))
    p = os.path.join(images_dir, filename)
    if os.path.exists(p):
        with open(p, 'rb') as f:
            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
    return None


def main_page():
    sid = st.session_state.get('store_id')
    if not sid or sid not in STORES:
        st.warning("No store selected.")
        st.session_state.page = 'stores'
        st.rerun()
        return

    st.title(f"🏬 {STORES[sid]}")

    cakes = _cakes_for_store(sid)
    if not any(sid in c.get('stores', []) for c in cakes):
        st.info("Showing popular picks while this store updates its menu.")

    q = st.text_input("Search cakes in this store").strip().lower()
    if q:
        cakes = [c for c in cakes if q in c['name'].lower() or q in c['id'].lower()]

    cols = st.columns(3)
    for i, c in enumerate(cakes):
        with cols[i % 3]:
            with st.container(border=True):
                src = _img_src(c.get('image',''))
                if src:
                    st.image(src, caption=c['name'])
                st.subheader(c['name'])
                size = st.selectbox(
                    "Size",
                    options=CAKE_SIZES['options'],
                    key=f"size_{sid}_{c['id']}"
                )
                price = int(c['price'] * CAKE_SIZES['multipliers'][size])
                st.caption(f"Price: ₹{price}")
                qty_key = f"qty_{sid}_{c['id']}"
                if qty_key not in st.session_state:
                    st.session_state[qty_key] = 1
                ccols = st.columns([1,1,2])
                with ccols[0]:
                    if st.button("➖", key=f"minus_{sid}_{c['id']}"):
                        st.session_state[qty_key] = max(1, st.session_state[qty_key]-1)
                with ccols[1]:
                    if st.button("➕", key=f"plus_{sid}_{c['id']}"):
                        st.session_state[qty_key] += 1
                with ccols[2]:
                    st.write(f"Quantity: {st.session_state[qty_key]}")
                bcols = st.columns([1,2,1])
                add_clicked = False
                with bcols[1]:
                    add_clicked = st.button("Add to Cart", key=f"add_{sid}_{c['id']}")
                if add_clicked:
                    API_BASE_URL = "http://127.0.0.1:8000/api"
                    headers = {"Authorization": f"Token {st.session_state.get('token', '')}"}
                    payload = {
            # resolve backend cake id by name (create if missing)
            "cake": get_or_create_cake_id(c['name'], price, size=size) or c['id'],
                        "quantity": st.session_state[qty_key],
                        "customization": f"store:{sid}|size:{size}"
                    }
                    try:
                        if not payload.get("cake") or isinstance(payload.get("cake"), str):
                            st.error("Could not resolve cake on backend. Please login and try again.")
                            return
                        resp = requests.post(f"{API_BASE_URL}/cart/", headers=headers, json=payload)
                        if resp.status_code in (200, 201):
                            # Set a flag to show success message and buttons
                            st.session_state[f'cart_success_{sid}_{c["id"]}'] = True
                            st.rerun()
                        else:
                            try:
                                err = resp.json()
                            except Exception:
                                err = resp.text
                            st.error(f"Failed to add to cart ({resp.status_code}). {err}")
                    except Exception as e:
                        st.error(f"Error: {e}")

                # Show success message and buttons if cart addition was successful
                success_key = f'cart_success_{sid}_{c["id"]}'
                if st.session_state.get(success_key, False):
                    st.success("Added to cart! ✅")
                    btnc = st.columns(3)
                    with btnc[0]:
                        if st.button("🛒 Go to Cart", key=f"go_cart_{sid}_{c['id']}", type="primary"):
                            # Clear the success flag and go to cart
                            del st.session_state[success_key]
                            st.session_state.page = 'cart'
                            st.rerun()
                    with btnc[1]:
                        if st.button("🛍️ Continue Shopping", key=f"continue_{sid}_{c['id']}"):
                            # Clear the success flag and stay on page
                            del st.session_state[success_key]
                            st.rerun()
                    with btnc[2]:
                        st.caption("Item added successfully!")