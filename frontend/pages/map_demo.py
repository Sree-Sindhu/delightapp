import streamlit as st
import pydeck as pdk
import pandas as pd
import json

st.set_page_config(layout="wide")

st.title("📦 Live Delivery Tracking")

# Mock data for demonstration
# In a real app, this would come from your WebSocket connection
live_agent_location = {
    'lat': 17.4333,
    'lon': 78.4833
}

if live_agent_location:
    # Create a DataFrame for pydeck
    map_data = pd.DataFrame([live_agent_location])

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=live_agent_location['lat'],
            longitude=live_agent_location['lon'],
            zoom=12,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HeatmapLayer',
                data=map_data,
                opacity=0.9,
                get_position=['lon', 'lat'],
                threshold=1,
                radius_pixels=50,
            ),
            pdk.Layer(
                "IconLayer",
                data=map_data,
                get_icon="https://cdn.iconscout.com/icon/free/png-256/delivery-van-1817112-1538356.png",
                get_size=4,
                size_scale=15,
                get_position=['lon', 'lat'],
            )
        ],
    ))
else:
    st.info("Waiting for live agent location...")