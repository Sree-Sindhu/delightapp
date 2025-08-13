# frontend/app_pages/customize.py
import streamlit as st
import requests
from .data import STORES, CUSTOM_CAKE_STORES
from .api_helpers import ensure_custom_cake_id

def main_page():
    st.header("🎨 Customize Your Cake")
    
    st.info("Note: Custom cake orders are available only at select locations.")

    # Require login
    token = st.session_state.get('token', '')
    if not token:
        st.warning("Please log in to place a custom cake order.")
        return

    # Let user select a store that offers custom cakes
    available_stores = {store_id: STORES[store_id] for store_id in CUSTOM_CAKE_STORES}
    
    if not available_stores:
        st.error("Sorry, no stores are currently offering custom cake orders.")
        return

    selected_store = st.selectbox(
        "First, select a store for pickup/delivery:",
        options=list(available_stores.keys()),
        format_func=lambda store_id: available_stores[store_id]
    )

    st.markdown(f"You are ordering from: **{available_stores[selected_store]}**")
    
    with st.form("custom_cake_form"):
        st.subheader("Cake Options")
        
        cake_flavor = st.selectbox("Base Flavor", ["Vanilla", "Chocolate", "Red Velvet", "Lemon"])
        cake_size = st.select_slider("Size (servings)", options=[6, 8, 12, 16, 24], value=8)
        
        st.subheader("Frosting & Filling")
        frosting_type = st.selectbox("Frosting", ["Buttercream", "Cream Cheese", "Fondant", "Ganache"])
        filling_type = st.selectbox("Filling (optional)", ["None", "Strawberry Jam", "Chocolate Mousse", "Caramel"])
        
        st.subheader("Personalization")
        message = st.text_input("Message on cake (max 40 characters)", max_chars=40)
        
        st.subheader("Dietary Needs")
        is_gluten_free = st.checkbox("Gluten-Free")
        is_vegan = st.checkbox("Vegan")
        
        notes = st.text_area("Additional notes or special requests")

        # Live price preview
        # Base price by servings, with minor add-ons for dietary options
        base_price = 699 + max(0, (cake_size - 8)) * 50
        addons = 0
        if is_gluten_free:
            addons += 60
        if is_vegan:
            addons += 90
        est_price = base_price + addons
        st.info(f"Estimated price: ₹{est_price}")
        submitted = st.form_submit_button("Add to Cart")

    if submitted:
            API_BASE_URL = "http://127.0.0.1:8000/api"
            headers = {"Authorization": f"Token {token}"}
            # Use a fixed product name for custom cakes and derive size label
            size_label = f"{cake_size} servings"
            custom_name = "Custom Cake"
            # Price heuristic (same as preview)
            base_price = 699 + max(0, (cake_size - 8)) * 50
            addons = (60 if is_gluten_free else 0) + (90 if is_vegan else 0)
            final_price = base_price + addons
            cake_id = ensure_custom_cake_id(custom_name, final_price, size_label, cake_flavor)
            if cake_id:
                customization = "|".join([
                    f"store:{selected_store}",
                    f"size:{size_label}",
                    f"frosting:{frosting_type}",
                    f"filling:{filling_type}",
                    f"message:{message or '-'}",
                    f"gluten_free:{is_gluten_free}",
                    f"vegan:{is_vegan}",
                ])
                try:
                    resp = requests.post(f"{API_BASE_URL}/cart/", headers=headers, json={
                        "cake": cake_id,
                        "quantity": 1,
                        "customization": customization
                    })
                    if resp.status_code in (200, 201):
                        st.success("Custom cake added to cart!")
                        st.balloons()
                        go_cols = st.columns(2)
                        with go_cols[0]:
                            if st.button("🛒\nGo to Cart"):
                                st.session_state.page = 'cart'
                                st.rerun()
                        with go_cols[1]:
                            if st.button("🛍️\nContinue Browsing"):
                                st.session_state.page = 'home'
                                st.rerun()
                    else:
                        st.error("Failed to add to cart. Please login and try again.")
                except Exception as e:
                    st.error(f"Error adding to cart: {e}")
            else:
                st.error("Unable to create custom cake item.")

