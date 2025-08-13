import streamlit as st
import requests
from typing import List, Dict


def _status_stepper(current: str, history: List[Dict]):
    steps = [
        ("pending", "Order placed"),
        ("confirmed", "Preparing"),
        ("out_for_delivery", "On the way"),
        ("delivered", "Delivered"),
    ]
    # Map timestamps from history
    ts_map = {h.get('status'): h.get('timestamp') for h in history or []}
    st.markdown(
        """
        <style>
        .stepper{display:flex;gap:14px;margin:10px 0 4px;align-items:center;}
        .step{display:flex;flex-direction:column;align-items:center;flex:1;}
        .dot{width:14px;height:14px;border-radius:50%;background:#e4e4ea;border:2px solid #cfcfda;}
        .dot.active{background:#10b981;border-color:#10b981;}
        .bar{height:3px;background:#e4e4ea;flex:1;border-radius:3px;margin-top:-6px;}
        .bar.active{background:#10b981;}
        .label{font-size:.78rem;color:#666;margin-top:6px;text-align:center;}
        .ts{font-size:.68rem;color:#999;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(steps) * 2 - 1)
    key_to_index = {k: i for i, (k, _) in enumerate(steps)}
    current_idx = key_to_index.get(current, -1)
    for i, (key, label) in enumerate(steps):
        with cols[i * 2]:
            active = current_idx >= i and current_idx != -1
            st.markdown(
                f"<div class='step'><div class='dot{' active' if active else ''}'></div>"
                f"<div class='label'>{label}</div>"
                f"<div class='ts'>{ts_map.get(key,'')}</div></div>",
                unsafe_allow_html=True,
            )
        if i < len(steps) - 1:
            with cols[i * 2 + 1]:
                active_bar = current_idx > i
                st.markdown(f"<div class='bar{' active' if active_bar else ''}'></div>", unsafe_allow_html=True)


def main_page():
    st.title("📦 Track Your Order")
    st.markdown("---")

    API_BASE_URL = "http://127.0.0.1:8000/api"
    token = st.session_state.get('token', '')
    headers = {"Authorization": f"Token {token}"} if token else {}

    if not token:
        st.warning("Please log in to view and track your orders.")
        return

    # Fetch orders
    try:
        res = requests.get(f"{API_BASE_URL}/orders/", headers=headers)
        orders = res.json() if res.status_code == 200 else []
    except Exception as e:
        st.error(f"Error loading orders: {e}")
        return

    if not orders:
        st.info("No orders found.")
        return

    # Pick active order by default
    active = [o for o in orders if o.get('status') in ['pending','confirmed','out_for_delivery']]
    default_id = (active[0]['id'] if active else orders[0]['id']) if orders else None
    id_options = {f"#{o['id']} • {o.get('status','').capitalize()}": o['id'] for o in orders}
    sel_label = st.selectbox("Select an order", list(id_options.keys()), index=list(id_options.values()).index(default_id) if default_id in id_options.values() else 0)
    order_id = id_options.get(sel_label)

    # Fetch tracking + history + agent
    tracking = history = agent = None
    try:
        tr = requests.get(f"{API_BASE_URL}/orders/{order_id}/tracking/", headers=headers)
        tracking = tr.json() if tr.status_code == 200 else None
    except Exception:
        pass
    try:
        hr = requests.get(f"{API_BASE_URL}/orders/{order_id}/history/", headers=headers)
        history = hr.json() if hr.status_code == 200 else []
    except Exception:
        history = []
    try:
        ar = requests.get(f"{API_BASE_URL}/orders/{order_id}/agent/", headers=headers)
        agent = ar.json() if ar.status_code == 200 else None
    except Exception:
        agent = None

    # Find order object
    ord_obj = next((o for o in orders if o['id'] == order_id), None)
    items = ord_obj.get('items', []) if ord_obj else []
    total = ord_obj.get('total_amount') if ord_obj else None
    if (not items) or (not total or total <= 0):
        try:
            dres = requests.get(f"{API_BASE_URL}/orders/{order_id}/", headers=headers)
            if dres.status_code == 200:
                dd = dres.json()
                items = dd.get('items', items)
                total = dd.get('total_amount', total)
        except Exception:
            pass
    if total is None:
        try:
            total = sum(i.get('quantity',1) * (i.get('unit_price') or 100) for i in items)
        except Exception:
            total = 0

    # Status stepper
    st.subheader(f"Order #{order_id} • {ord_obj.get('status','').capitalize() if ord_obj else ''}")
    _status_stepper(ord_obj.get('status') if ord_obj else None, history)

    # Details columns
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Items")
        if items:
            for it in items:
                st.write(f"- {it.get('cake_name','Cake')} × {it.get('quantity',1)}")
        else:
            st.write("No items found.")
        st.write(f"**Total:** ₹{total}")

    with c2:
        st.markdown("### Delivery")
        st.write(f"ETA: {tracking.get('estimated_delivery_time','N/A') if tracking else 'N/A'}")
        if agent:
            st.write(f"Agent: {agent.get('name','-')} ({agent.get('phone','')})")
        else:
            st.write("Agent: Not assigned")

    # Actions
    a1, a2, a3 = st.columns(3)
    with a1:
        if ord_obj and ord_obj.get('status') in ['pending','confirmed']:
            if st.button("Cancel Order"):
                try:
                    rr = requests.delete(f"{API_BASE_URL}/orders/{order_id}/cancel/", headers=headers)
                    if rr.status_code == 200:
                        st.success("Order cancelled.")
                        st.rerun()
                    else:
                        st.error(rr.json().get('detail','Failed to cancel'))
                except Exception as e:
                    st.error(f"Error: {e}")
    with a2:
        if st.button("Track on Map"):
            st.session_state['track_order_id'] = order_id
            st.session_state.page = 'map_demo'
            st.rerun()
    with a3:
        if st.button("Reorder"):
            try:
                rr = requests.post(f"{API_BASE_URL}/orders/{order_id}/reorder/", headers=headers)
                if rr.status_code == 200:
                    st.success("Items added to cart.")
                else:
                    st.error("Could not add items to cart.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Review prompt when delivered
    if ord_obj and ord_obj.get('status') == 'delivered':
        st.markdown("---")
        st.subheader("How was your order?")
        with st.container(border=True):
            r1, r2 = st.columns([1,3])
            with r1:
                rating = st.slider("Rate", 1, 5, 5)
            with r2:
                comment = st.text_input("Leave a quick review (optional)")
            if st.button("Submit review"):
                try:
                    # Attempt to attach review to the first item cake
                    cake_id = items[0].get('cake') if items else None
                    ok = False
                    if cake_id:
                        pr = requests.post(f"{API_BASE_URL}/reviews/", headers=headers, json={"cake": cake_id, "rating": rating, "comment": comment})
                        ok = pr.status_code in (200, 201)
                    # Also push a store review if store_id is known in session
                    store_id = st.session_state.get('store_id')
                    if store_id:
                        sr = requests.post(f"{API_BASE_URL}/store-reviews/", headers=headers, json={"store": store_id, "rating": rating, "comment": comment})
                        ok = ok or sr.status_code in (200, 201)
                    if ok:
                        st.success("Thanks for your feedback!")
                    else:
                        st.info("Couldn't attach the review automatically. Please try from store/cake pages.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Live update toggle
    st.markdown("---")
    live = st.toggle("Live update (2s)", value=False)
    if live:
        import time
        time.sleep(2)
        st.rerun()
