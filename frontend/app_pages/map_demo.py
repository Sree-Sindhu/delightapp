"""Swiggy-style live map: animated rider path, markers, ETA.
Uses a simulated road-like route with deck.gl TripsLayer for smooth playback.
If a WebSocket is present, you can switch off simulation and show the live agent.
"""
import streamlit as st
import json
import websocket
import threading
import pydeck as pdk
import pandas as pd
import requests
import math
import time
from .data import STORE_DETAILS, STORES
from .utils import fake_geocode, haversine_km

# This is a placeholder for your API URL. You'll need to update this.
API_BASE_URL = "http://127.0.0.1:8000/api"


def _gen_route_points(slat, slon, clat, clon, steps: int = 80):
    """Generate a road-like polyline between store and customer with slight bends.
    Returns list of dicts with lat/lon and a parallel list of timestamps (seconds).
    """
    points = []
    timestamps = []
    for i in range(steps + 1):
        t = i / steps
        # bezier-like bend using ease-in-out and a lateral offset
        lat = slat + (clat - slat) * t
        lon = slon + (clon - slon) * t
        # lateral offset to simulate following streets
        # rotate vector by 90 deg for lateral, scaled small
        dlat = clat - slat
        dlon = clon - slon
        # normalized lateral (swap and invert)
        norm = math.sqrt(dlat * dlat + dlon * dlon) or 1.0
        off_lat = -dlon / norm * 0.002 * math.sin(t * math.pi)
        off_lon = dlat / norm * 0.002 * math.sin(t * math.pi)
        lat += off_lat
        lon += off_lon
        points.append([lon, lat])
        timestamps.append(i)  # 1 second per step
    return points, timestamps

def map_demo_page():
    # --- WebSocket Live Tracking ---
    order_id = st.session_state.get('track_order_id', None)
    ws_url = f"ws://127.0.0.1:8000/ws/orders/{order_id}/" if order_id else None
    agent_location_data = st.session_state.get('agent_location_data', None)

    def on_message(ws, message):
        data = json.loads(message)
        # Expecting {'location': ..., 'agent_id': ...}
        st.session_state['agent_location_data'] = data.get('location', None)
        # set a flag for update rather than immediate rerun (avoid recursion)
        st.session_state['agent_location_updated'] = True

    def run_ws():
        if not ws_url:
            return
        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        ws.run_forever()

    if 'ws_thread_started' not in st.session_state and ws_url:
        ws_thread = threading.Thread(target=run_ws, daemon=True)
        ws_thread.start()
        st.session_state['ws_thread_started'] = True

    # Page config should be set only once in main app; skip here if already set.
    st.markdown("<h1 style='text-align: center;'>🚚 Live Order Tracking</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Track your order in real time!</p>", unsafe_allow_html=True)

    API_BASE_URL = "http://127.0.0.1:8000/api"
    headers = {"Authorization": f"Token {st.session_state.get('token', '')}"}
    order_id = st.session_state.get('track_order_id', None)

    tracking = None
    agent = None
    if order_id:
        # Fetch order tracking info
        try:
            res = requests.get(f"{API_BASE_URL}/orders/{order_id}/tracking/", headers=headers)
            tracking = res.json() if res.status_code == 200 else None
        except Exception as e:
            st.error(f"Error fetching tracking info: {e}")
            tracking = None

        # Fetch agent location if assigned
        try:
            agent_res = requests.get(f"{API_BASE_URL}/orders/{order_id}/agent/", headers=headers)
            agent = agent_res.json() if agent_res.status_code == 200 else None
        except Exception:
            agent = None

    # Choose store from session if provided
    store_id = st.session_state.get('route_store_id') or st.session_state.get('store_id')
    if store_id and store_id in STORE_DETAILS:
        sd = STORE_DETAILS[store_id]
        slat, slon = fake_geocode(sd.get('address',''), sd.get('city',''))
        store_location = {'name': STORES.get(store_id, 'Store'), 'lat': slat, 'lon': slon}
    else:
        store_location = {'name': 'Delight Bakery', 'lat': 17.4334, 'lon': 78.4835}

    # Determine customer location:
    # Try user's selected address from API; else ask for a quick pin input
    customer_location = None
    try:
        addr_res = requests.get(f"{API_BASE_URL}/addresses/", headers=headers)
        addrs = addr_res.json() if addr_res.status_code == 200 else []
        if addrs:
            a = addrs[0]
            clat, clon = fake_geocode(
                f"{a.get('flat_number','')} {a.get('building_name','')} {a.get('street','')} {a.get('area_or_colony','')} {a.get('city','')} {a.get('state','')} {a.get('pincode','')}",
                a.get('city','')
            )
            customer_location = {'name': 'Customer', 'lat': clat, 'lon': clon}
    except Exception:
        customer_location = None
    if not customer_location:
        # fallback near store if no address
        customer_location = {'name': 'Customer', 'lat': store_location['lat'] + 0.02, 'lon': store_location['lon'] - 0.02}
    # Use live agent location if available from WebSocket
    if agent_location_data:
        agent_location = {'name': agent.get('name','Agent') if agent else 'Agent', 'lat': agent_location_data.get('lat', 17.422), 'lon': agent_location_data.get('lon', 78.488)}
    else:
        agent_location = {'name': agent.get('name','Agent') if agent else 'Agent', 'lat': 17.422, 'lon': 78.488} if agent else None

    # Build a simulated route between store and customer for TripsLayer
    route_path, route_ts = _gen_route_points(store_location['lat'], store_location['lon'], customer_location['lat'], customer_location['lon'])
    trips_data = [{
        'path': route_path,              # [[lon, lat], ...]
        'timestamps': route_ts           # [0, 1, 2, ...]
    }]

    # Playback controls
    # Initialize widget defaults before rendering
    if 'map_play' not in st.session_state:
        st.session_state['map_play'] = True
    if 'map_speed' not in st.session_state:
        st.session_state['map_speed'] = 1.0

    ctl_cols = st.columns([1,1,2,2,2])
    with ctl_cols[0]:
        st.toggle("Play", key="map_play")
    with ctl_cols[1]:
        if st.button("⏸️ Reset", key="map_reset"):
            st.session_state['map_time'] = 0.0
            st.session_state['map_last_tick'] = time.time()
    with ctl_cols[2]:
        st.slider("Speed (x)", 0.5, 3.0, st.session_state.get('map_speed', 1.0), 0.1, key="map_speed")
    with ctl_cols[3]:
        st.caption(f"Store: {store_location['name']}")
    with ctl_cols[4]:
        st.caption("Agent simulated on route")

    # Advance playback time
    total_duration = float(route_ts[-1]) if route_ts else 60.0
    if 'map_time' not in st.session_state:
        st.session_state['map_time'] = 0.0
    if 'map_last_tick' not in st.session_state:
        st.session_state['map_last_tick'] = time.time()
    if st.session_state.get('map_play'):
        now = time.time()
        dt = now - st.session_state.get('map_last_tick', now)
        st.session_state['map_last_tick'] = now
        st.session_state['map_time'] = (st.session_state.get('map_time', 0.0) + dt * float(st.session_state.get('map_speed', 1.0)))
        if st.session_state['map_time'] > total_duration:
            st.session_state['map_time'] = 0.0

    # --- CREATE THE MAP ---
    # Compute agent position along path for ETA (interpolate by map_time)
    def _interp_point(path, t):
        if not path:
            return None
        idx = min(int(t), len(path) - 1)
        return path[idx]

    agent_xy = _interp_point(route_path, st.session_state['map_time'])
    agent_latlon = {'lat': agent_xy[1], 'lon': agent_xy[0]} if agent_xy else None

    deck = pdk.Deck(
        map_style='light',
        map_provider='carto',
        initial_view_state=pdk.ViewState(
            latitude=store_location['lat'],
            longitude=store_location['lon'],
            zoom=13,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'TripsLayer',
                data=trips_data,
                get_path='path',
                get_timestamps='timestamps',
                get_color=[0, 122, 255],
                opacity=0.8,
                width_min_pixels=4,
                rounded=True,
                trail_length=60,
                current_time=float(st.session_state['map_time']),
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=[{'name': 'Store', 'lat': store_location['lat'], 'lon': store_location['lon']}],
                get_position='[lon, lat]',
                get_fill_color=[255, 99, 132],
                get_radius=60,
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=[{'name': 'Customer', 'lat': customer_location['lat'], 'lon': customer_location['lon']}],
                get_position='[lon, lat]',
                get_fill_color=[0, 200, 83],
                get_radius=60,
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=[agent_latlon] if agent_latlon else [],
                get_position='[lon, lat]',
                get_fill_color=[2, 136, 209],
                get_radius=70,
                pickable=True,
            ),
            pdk.Layer(
                'TextLayer',
                data=[
                    {'text': 'Store', 'lat': store_location['lat'], 'lon': store_location['lon']},
                    {'text': 'You', 'lat': customer_location['lat'], 'lon': customer_location['lon']},
                ] + ([{'text': 'Agent', 'lat': agent_latlon['lat'], 'lon': agent_latlon['lon']}] if agent_latlon else []),
                get_text='text',
                get_position='[lon, lat]',
                get_size=16,
                get_color=[33, 33, 33],
            ),
        ],
    )
    st.pydeck_chart(deck)

    st.markdown("---")
    st.markdown("### Details")
    if order_id:
        st.write(f"**Order ID:** {order_id}")
        st.write(f"**Status:** {tracking.get('status','N/A') if tracking else 'N/A'}")
    # Simple ETA calculation using haversine distance and avg speed 25 km/h
    dist_km = haversine_km(agent_latlon['lat'], agent_latlon['lon'], customer_location['lat'], customer_location['lon']) if agent_latlon else haversine_km(store_location['lat'], store_location['lon'], customer_location['lat'], customer_location['lon'])
    avg_speed_kmh = 25.0
    eta_min = (dist_km / avg_speed_kmh) * 60.0
    st.write(f"**ETA (approx):** {eta_min:.0f} min for {dist_km:.1f} km")
    if order_id:
        st.write(f"**Agent:** {agent.get('name','N/A') if agent else 'N/A'}")
        if agent_latlon:
            st.write(f"**Agent Location:** {agent_latlon['lat']:.4f}, {agent_latlon['lon']:.4f}")
        else:
            st.write("Agent not assigned yet.")

    # Simple animation timer: if playing, rerun periodically
    if st.session_state.get('map_play'):
        time.sleep(0.5)
        st.rerun()

