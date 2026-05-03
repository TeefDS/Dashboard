import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Food Safety Monitoring Dashboard",
    layout="wide"
)

# =========================================================
# DUMMY DATA
# =========================================================
data = pd.DataFrame([
    {
        "id": 1,
        "city": "Riyadh",
        "country": "Saudi Arabia",
        "lat": 24.7136,
        "lon": 46.6753,
        "alert_level": "High",
        "hazard": "Salmonella",
        "product": "Frozen Berries",
        "category": "Frozen Foods",
        "source": "Official Recall",
        "status": "Open",
        "cases": 12
    },
    {
        "id": 2,
        "city": "Jeddah",
        "country": "Saudi Arabia",
        "lat": 21.5433,
        "lon": 39.1728,
        "alert_level": "Medium",
        "hazard": "Food Poisoning",
        "product": "Chicken Shawarma",
        "category": "Ready-to-Eat",
        "source": "Social Media",
        "status": "Investigating",
        "cases": 8
    },
    {
        "id": 3,
        "city": "Dammam",
        "country": "Saudi Arabia",
        "lat": 26.4207,
        "lon": 50.0888,
        "alert_level": "Low",
        "hazard": "Listeria",
        "product": "Packaged Salad",
        "category": "Vegetables",
        "source": "Consumer Complaint",
        "status": "Closed",
        "cases": 3
    },
    {
        "id": 4,
        "city": "Dubai",
        "country": "UAE",
        "lat": 25.2048,
        "lon": 55.2708,
        "alert_level": "High",
        "hazard": "E. coli",
        "product": "Lettuce",
        "category": "Vegetables",
        "source": "Official Recall",
        "status": "Open",
        "cases": 15
    },
    {
        "id": 5,
        "city": "London",
        "country": "UK",
        "lat": 51.5072,
        "lon": -0.1276,
        "alert_level": "Medium",
        "hazard": "Norovirus",
        "product": "Sushi",
        "category": "Seafood",
        "source": "Social Media",
        "status": "Investigating",
        "cases": 7
    },
    {
        "id": 6,
        "city": "New York",
        "country": "USA",
        "lat": 40.7128,
        "lon": -74.0060,
        "alert_level": "High",
        "hazard": "Salmonella",
        "product": "Egg Sandwich",
        "category": "Bakery",
        "source": "Consumer Complaint",
        "status": "Open",
        "cases": 10
    },
    {
        "id": 7,
        "city": "Virginia",
        "country": "USA",
        "lat": 37.4316,
        "lon": -78.6569,
        "alert_level": "Low",
        "hazard": "Spoilage",
        "product": "Milk",
        "category": "Dairy",
        "source": "Social Media",
        "status": "Closed",
        "cases": 2
    },
    {
        "id": 8,
        "city": "Woking",
        "country": "UK",
        "lat": 51.3168,
        "lon": -0.5600,
        "alert_level": "Medium",
        "hazard": "Food Poisoning",
        "product": "Sushi",
        "category": "Seafood",
        "source": "Consumer Complaint",
        "status": "Investigating",
        "cases": 5
    }
])

# =========================================================
# COLOR MAPPING
# =========================================================
def color_by_alert(level):
    if level == "High":
        return [220, 53, 69, 180]   # red
    elif level == "Medium":
        return [255, 193, 7, 180]   # yellow
    else:
        return [40, 167, 69, 180]   # green

data["color"] = data["alert_level"].apply(color_by_alert)
data["radius"] = data["cases"] * 4000

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.title("Filters")

selected_country = st.sidebar.multiselect(
    "Country",
    options=sorted(data["country"].unique()),
    default=sorted(data["country"].unique())
)

selected_alert = st.sidebar.multiselect(
    "Alert Level",
    options=["High", "Medium", "Low"],
    default=["High", "Medium", "Low"]
)

selected_source = st.sidebar.multiselect(
    "Source",
    options=sorted(data["source"].unique()),
    default=sorted(data["source"].unique())
)

filtered_df = data[
    (data["country"].isin(selected_country)) &
    (data["alert_level"].isin(selected_alert)) &
    (data["source"].isin(selected_source))
].copy()

# =========================================================
# HEADER
# =========================================================
st.title("Food Safety Monitoring Dashboard")
st.caption("Prototype UI using dummy data only")

# =========================================================
# KPI SECTION
# =========================================================
total_alerts = len(filtered_df)
open_alerts = (filtered_df["status"] == "Open").sum()
investigating_alerts = (filtered_df["status"] == "Investigating").sum()
total_cases = filtered_df["cases"].sum()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Alerts", total_alerts)

with k2:
    st.metric("Open Alerts", open_alerts)

with k3:
    st.metric("Under Investigation", investigating_alerts)

with k4:
    st.metric("Reported Cases", total_cases)

# =========================================================
# MAP + SIDE CHARTS
# =========================================================
left, right = st.columns([2.2, 1])

with left:
    st.subheader("Geographical Distribution")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
        opacity=0.8
    )

    view_state = pdk.ViewState(
        latitude=29,
        longitude=20,
        zoom=1.4,
        pitch=0
    )

    tooltip = {
        "html": """
        <b>City:</b> {city} <br/>
        <b>Country:</b> {country} <br/>
        <b>Alert:</b> {alert_level} <br/>
        <b>Hazard:</b> {hazard} <br/>
        <b>Product:</b> {product} <br/>
        <b>Cases:</b> {cases}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="mapbox://styles/mapbox/light-v9"
        ),
        use_container_width=True
    )

with right:
    st.subheader("Alerts by Level")

    level_chart = (
        filtered_df.groupby("alert_level")
        .size()
        .reset_index(name="count")
    )

    chart1 = alt.Chart(level_chart).mark_bar().encode(
        x=alt.X("alert_level:N", title="Alert Level"),
        y=alt.Y("count:Q", title="Count"),
        tooltip=["alert_level", "count"]
    ).properties(height=220)

    st.altair_chart(chart1, use_container_width=True)

    st.subheader("Cases by Source")

    source_chart = (
        filtered_df.groupby("source")["cases"]
        .sum()
        .reset_index()
    )

    chart2 = alt.Chart(source_chart).mark_arc(innerRadius=45).encode(
        theta="cases:Q",
        color="source:N",
        tooltip=["source", "cases"]
    ).properties(height=260)

    st.altair_chart(chart2, use_container_width=True)

# =========================================================
# SECOND ROW
# =========================================================
c1, c2 = st.columns([1.2, 1.2])

with c1:
    st.subheader("Top Hazard Types")

    hazard_chart = (
        filtered_df.groupby("hazard")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    chart3 = alt.Chart(hazard_chart).mark_bar().encode(
        x=alt.X("count:Q", title="Count"),
        y=alt.Y("hazard:N", sort="-x", title="Hazard"),
        tooltip=["hazard", "count"]
    ).properties(height=300)

    st.altair_chart(chart3, use_container_width=True)

with c2:
    st.subheader("Top Product Categories")

    category_chart = (
        filtered_df.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    chart4 = alt.Chart(category_chart).mark_bar().encode(
        x=alt.X("count:Q", title="Count"),
        y=alt.Y("category:N", sort="-x", title="Category"),
        tooltip=["category", "count"]
    ).properties(height=300)

    st.altair_chart(chart4, use_container_width=True)

# =========================================================
# TABLE
# =========================================================
st.subheader("Alert Details")

display_df = filtered_df[[
    "id", "city", "country", "alert_level", "hazard",
    "product", "category", "source", "status", "cases"
]].sort_values(by=["alert_level", "cases"], ascending=[True, False])

st.dataframe(display_df, use_container_width=True)

# =========================================================
# DOWNLOAD
# =========================================================
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Alerts Data",
    data=csv_data,
    file_name="food_safety_alerts_dummy.csv",
    mime="text/csv"
)
