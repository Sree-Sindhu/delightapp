# frontend/app_pages/cakes_catalog.py
import streamlit as st
import difflib
from .data import CAKES


def _search_box(label: str):
    q = st.text_input(label, key=f"{label}_q").strip()
    return q.lower()


def _fuzzy_filter(cakes, q: str):
    if not q:
        return cakes
    q = q.lower()
    # direct substring matches first
    direct = [c for c in cakes if q in c.get('name','').lower() or q in c.get('id','').lower()]
    remaining = [c for c in cakes if c not in direct]
    # fuzzy by SequenceMatcher ratio on name
    scored = [(c, difflib.SequenceMatcher(a=q, b=c.get('name','').lower()).ratio()) for c in remaining]
    # include related ones by splitting words (e.g., 'black' -> 'black forest', 'blackcurrant')
    related = [c for c in remaining if any(tok.startswith(q) or q in tok for tok in c.get('name','').lower().split())]
    # combine unique, sorted by ratio
    fuzzy_sorted = [c for (c,score) in sorted(scored, key=lambda x: x[1], reverse=True) if score >= 0.45]
    result = []
    seen = set()
    for part in [direct, related, fuzzy_sorted]:
        for c in part:
            cid = c.get('id')
            if cid not in seen:
                seen.add(cid)
                result.append(c)
    return result


def main_page():
    st.header("🍰 Cakes Catalog")
    # floating chips are rendered globally in home wrapper

    q = _search_box("Search cakes")
    filtered = _fuzzy_filter(CAKES, q)

    # which cake's stores to show
    show_for_id = st.session_state.get('selected_cake_for_store')

    if not filtered:
        st.info("No cakes found.")
        return

    for cake in filtered:
        with st.container(border=True):
            st.write(f"• {cake['name']}")
            if st.button("🏪\nView Stores", key=f"viewstores_{cake['id']}"):
                st.session_state.selected_cake_for_store = cake['id']
                st.session_state.page = 'stores'
                st.rerun()
            # Show stores list for the selected cake
            if show_for_id == cake['id']:
                store_ids = cake.get('stores', [])
                if not store_ids:
                    st.info("Not available in any store right now.")
                else:
                    st.markdown("Available at:")
                    cols = st.columns(min(3, len(store_ids)))
                    for i, sid in enumerate(store_ids):
                        label = sid
                        # If STORES mapping exists, show the proper store name
                        try:
                            from .data import STORES as _STORES
                            label = _STORES.get(sid, sid)
                        except Exception:
                            pass
                        with cols[i % len(cols)]:
                            if st.button(label, key=f"open_store_{cake['id']}_{sid}"):
                                st.session_state.store_id = sid
                                st.session_state.highlight_cake_id = cake['id']
                                st.session_state.page = 'store_detail'
                                st.rerun()
