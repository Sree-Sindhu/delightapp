# frontend/pages/cart.py
import streamlit as st
import requests
from .data import CAKES, CAKE_SIZES

def main_page():
    st.title("🛒 Your Cart")
    st.markdown("---")
    # floating chips are rendered globally in home wrapper

    API_BASE_URL = "http://127.0.0.1:8000/api"
    headers = {"Authorization": f"Token {st.session_state.get('token', '')}"}

    # Fetch cart items from backend
    try:
        res = requests.get(f"{API_BASE_URL}/cart/", headers=headers)
        if res.status_code == 200:
            cart_items = res.json()
        else:
            st.error("Failed to fetch cart items.")
            cart_items = []
    except Exception as e:
        st.error(f"Error fetching cart: {e}")
        cart_items = []

    # Fetch addresses for delivery selection
    try:
        addr_res = requests.get(f"{API_BASE_URL}/addresses/", headers=headers)
        addresses = addr_res.json() if addr_res.status_code == 200 else []
    except Exception:
        addresses = []

    if not cart_items:
        st.info("Your cart is empty.")
        return

    st.subheader("Cart Items")
    total_price = 0
    def _base_price_by_name(name: str) -> int:
        for c in CAKES:
            if c.get('name') == name:
                return int(c.get('price', 0))
        return 0

    def _price_with_size(base_price: int, customization: str | None) -> int:
        if not customization:
            return int(base_price)
        # customization like "store:<id>|size:<size>"
        size_val = None
        parts = [p.strip() for p in customization.split('|')]
        for p in parts:
            if p.startswith('size:'):
                size_val = p.split(':', 1)[1].strip()
                break
        if size_val and size_val in CAKE_SIZES.get('multipliers', {}):
            mult = CAKE_SIZES['multipliers'][size_val]
            return int(round(base_price * mult))
        return int(base_price)

    for item in cart_items:
        cake_name = item.get('cake_name', 'Cake')
        quantity = int(item.get('quantity', 1))
        customization = item.get('customization')
        # Prefer backend-provided pricing if available
        price_each = item.get('unit_price') or item.get('cake_price') or item.get('price')
        if isinstance(price_each, str):
            try:
                price_each = float(price_each)
            except Exception:
                price_each = None
        if price_each is not None:
            price = int(round(float(price_each)))
        else:
            # Fallbacks: if it's a custom cake, compute using simple heuristic by servings
            if cake_name.lower().startswith('custom') and customization:
                servings = None
                try:
                    parts = [p.strip() for p in customization.split('|')]
                    for p in parts:
                        if p.startswith('size:'):
                            size_label = p.split(':', 1)[1].strip()  # e.g., "8 servings"
                            if size_label.endswith('servings'):
                                servings = int(size_label.split()[0])
                            break
                except Exception:
                    servings = None
                if servings is None:
                    servings = 8
                price = int(699 + max(0, (servings - 8)) * 50)
            else:
                base = _base_price_by_name(cake_name)
                price = _price_with_size(base, customization)
        item_id = item.get('id')
        total_price += quantity * price
        col1, col2, col3, col4 = st.columns([3,2,2,2])
        with col1:
            st.write(f"**{cake_name}**")
            if customization:
                st.caption(customization)
        with col2:
            new_qty = st.number_input("Qty", min_value=1, value=quantity, key=f"qty_{item_id}")
            if new_qty != quantity:
                if st.button("🔄\nUpdate", key=f"update_{item_id}"):
                    try:
                        update_res = requests.put(f"{API_BASE_URL}/cart/{item_id}/", headers=headers, json={"quantity": new_qty})
                        if update_res.status_code == 200:
                            st.success("Quantity updated!")
                            st.rerun()
                        else:
                            st.error("Failed to update quantity.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with col3:
            st.write(f"₹{price * quantity}")
        with col4:
            if st.button("🗑️\nRemove", key=f"remove_{item_id}"):
                try:
                    del_res = requests.delete(f"{API_BASE_URL}/cart/{item_id}/", headers=headers)
                    if del_res.status_code == 204:
                        st.success("Item removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove item.")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.subheader(f"Total: ₹{total_price}")

    # Address selection
    st.markdown("### Delivery Address")
    if addresses:
        addr_options = [f"{a['flat_number']} {a['building_name']}, {a['street']}, {a['city']} ({a['pincode']})" for a in addresses]
        selected_addr = st.selectbox("Choose delivery address", addr_options)
        selected_addr_id = addresses[addr_options.index(selected_addr)]['id']
    else:
        st.warning("No address found. Please add one in your profile.")
        selected_addr_id = None

    # Checkout
    if st.button("💳\nProceed to Checkout"):
        if not selected_addr_id:
            st.error("Please select a delivery address.")
        else:
            # Place order
            try:
                order_payload = {"address": selected_addr_id}
                order_res = requests.post(f"{API_BASE_URL}/orders/", headers=headers, json=order_payload)
                if order_res.status_code in [200, 201]:
                    data = order_res.json() if order_res.content else {}
                    order_id = data.get('id')
                    st.success("Order placed! Redirecting to live tracking…")
                    # Clear any cached cart data by removing session state
                    if 'cart_items' in st.session_state:
                        del st.session_state['cart_items']
                    if order_id:
                        st.session_state['track_order_id'] = order_id
                        st.session_state.page = 'map_demo'
                    else:
                        st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    try:
                        error_detail = order_res.json().get('detail', 'Unknown error')
                    except:
                        error_detail = order_res.text or f"HTTP {order_res.status_code}"
                    st.error(f"Failed to place order: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to place order: Cannot connect to server. Please ensure Django backend is running on http://127.0.0.1:8000")
            except Exception as e:
                st.error(f"Error placing order: {e}")
