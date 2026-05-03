import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Food Safety Monitoring Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# THEME SWITCH
# =========================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

def toggle_theme():
    st.session_state.theme_mode = (
        "Light" if st.session_state.theme_mode == "Dark" else "Dark"
    )

is_dark = st.session_state.theme_mode == "Dark"

# =========================================================
# THEME COLORS
# =========================================================
if is_dark:
    BG = "linear-gradient(180deg, #020817 0%, #071226 100%)"
    CARD_BG = "rgba(10, 20, 40, 0.95)"
    BAR_BG = "rgba(10, 20, 40, 0.92)"
    BORDER = "#1d3a66"
    TEXT = "#eaf2ff"
    MUTED = "#9db2ce"
    GRID = "rgba(120, 160, 220, 0.12)"
    MAP_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json"
else:
    BG = "linear-gradient(180deg, #f6f9ff 0%, #eef4ff 100%)"
    CARD_BG = "rgba(255,255,255,0.95)"
    BAR_BG = "rgba(255,255,255,0.92)"
    BORDER = "#dbe7ff"
    TEXT = "#243247"
    MUTED = "#6c7a93"
    GRID = "rgba(120, 140, 170, 0.18)"
    MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json"

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(f"""
<style>
    .stApp {{
        background: {BG};
    }}

    .block-container {{
        max-width: 1600px;
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }}

    .top-bar {{
        background: {BAR_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 14px 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 24px rgba(40, 70, 140, 0.10);
    }}

    .card {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 8px 24px rgba(40, 70, 140, 0.08);
        margin-bottom: 14px;
    }}

    .kpi-card {{
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    .kpi-blue {{
        background: {"linear-gradient(135deg, rgba(7,32,68,0.95), rgba(11,30,58,0.95))" if is_dark else "linear-gradient(135deg, rgba(229,242,255,0.98), rgba(242,247,255,0.98))"};
        border: 1px solid {"#3d7fd4" if is_dark else "#8ac5ff"};
    }}

    .kpi-pink {{
        background: {"linear-gradient(135deg, rgba(65,18,38,0.95), rgba(53,18,42,0.95))" if is_dark else "linear-gradient(135deg, rgba(255,234,241,0.98), rgba(255,245,248,0.98))"};
        border: 1px solid {"#d86a98" if is_dark else "#ff90b1"};
    }}

    .kpi-green {{
        background: {"linear-gradient(135deg, rgba(14,52,33,0.95), rgba(15,42,34,0.95))" if is_dark else "linear-gradient(135deg, rgba(231,255,239,0.98), rgba(245,255,249,0.98))"};
        border: 1px solid {"#5fb87d" if is_dark else "#7ed79d"};
    }}

    .kpi-title {{
        font-size: 15px;
        color: {TEXT};
        font-weight: 600;
        margin-bottom: 10px;
    }}

    .kpi-value {{
        font-size: 38px;
        font-weight: 800;
        line-height: 1.1;
    }}

    .kpi-blue .kpi-value {{ color: #47bfff; }}
    .kpi-pink .kpi-value {{ color: #ff6489; }}
    .kpi-green .kpi-value {{ color: #63d98d; }}

    .section-title {{
        font-size: 18px;
        font-weight: 700;
        color: {TEXT};
        margin-bottom: 10px;
    }}

    .footer-note {{
        color: {MUTED};
        font-size: 13px;
        text-align: center;
        margin-top: 6px;
    }}

    .stSelectbox label, .stTextInput label {{
        color: {TEXT} !important;
        font-weight: 600;
    }}

    .stMarkdown, .stCaption, p, div {{
        color: {TEXT};
    }}

    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextInput"] > div {{
        border-radius: 12px !important;
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# GENERATE DUMMY DATA
# =========================================================
def generate_dummy_data():
    np.random.seed(42)

    # السعودية فيها كثافة عالية جدًا
    saudi_hotspots = [
        ("Riyadh", "Saudi Arabia", 24.7136, 46.6753, 22),
        ("Jeddah", "Saudi Arabia", 21.5433, 39.1728, 20),
        ("Dammam", "Saudi Arabia", 26.4207, 50.0888, 15),
        ("Makkah", "Saudi Arabia", 21.3891, 39.8579, 12),
        ("Madinah", "Saudi Arabia", 24.5247, 39.5692, 10),
        ("Khobar", "Saudi Arabia", 26.2172, 50.1971, 10),
    ]

    global_hotspots = [
        ("Dubai", "UAE", 25.2048, 55.2708, 15),
        ("London", "UK", 51.5072, -0.1276, 14),
        ("New York", "USA", 40.7128, -74.0060, 14),
        ("Mumbai", "India", 19.0760, 72.8777, 13),
        ("Tokyo", "Japan", 35.6762, 139.6503, 12),
        ("Paris", "France", 48.8566, 2.3522, 11),
        ("Istanbul", "Turkey", 41.0082, 28.9784, 10),
        ("Cairo", "Egypt", 30.0444, 31.2357, 10),
    ]

    regular_places = [
        ("Doha", "Qatar", 25.2854, 51.5310),
        ("Kuwait City", "Kuwait", 29.3759, 47.9774),
        ("Manama", "Bahrain", 26.2235, 50.5876),
        ("Muscat", "Oman", 23.5880, 58.3829),
        ("Abu Dhabi", "UAE", 24.4539, 54.3773),
        ("Berlin", "Germany", 52.5200, 13.4050),
        ("Madrid", "Spain", 40.4168, -3.7038),
        ("Rome", "Italy", 41.9028, 12.4964),
        ("Toronto", "Canada", 43.6532, -79.3832),
        ("Chicago", "USA", 41.8781, -87.6298),
        ("Los Angeles", "USA", 34.0522, -118.2437),
        ("Mexico City", "Mexico", 19.4326, -99.1332),
        ("Sao Paulo", "Brazil", -23.5558, -46.6396),
        ("Johannesburg", "South Africa", -26.2041, 28.0473),
        ("Lagos", "Nigeria", 6.5244, 3.3792),
        ("Delhi", "India", 28.7041, 77.1025),
        ("Bangkok", "Thailand", 13.7563, 100.5018),
        ("Kuala Lumpur", "Malaysia", 3.1390, 101.6869),
        ("Jakarta", "Indonesia", -6.2088, 106.8456),
        ("Singapore", "Singapore", 1.3521, 103.8198),
        ("Beijing", "China", 39.9042, 116.4074),
        ("Shanghai", "China", 31.2304, 121.4737),
        ("Seoul", "South Korea", 37.5665, 126.9780),
        ("Sydney", "Australia", -33.8688, 151.2093),
        ("Melbourne", "Australia", -37.8136, 144.9631),
    ]

    product_categories = ["Dairy", "Poultry", "Vegetables", "Seafood", "Other"]
    product_probs = [0.17, 0.34, 0.22, 0.12, 0.15]

    symptoms = ["Vomiting", "Fever", "Diarrhea", "Nausea"]
    symptom_probs = [0.40, 0.30, 0.20, 0.10]

    sources = ["Social Media", "Official Recall", "Consumer Complaint", "News"]
    source_probs = [0.38, 0.27, 0.21, 0.14]

    hazards = ["Salmonella", "E. coli", "Listeria", "Food Poisoning", "Norovirus"]
    statuses = ["Open", "Investigating", "Closed"]
    levels = ["High", "Medium", "Low"]

    today = datetime.now().date()
    rows = []
    idx = 1

    # اليوم الحالي
    total_today = 260
    # قديم
    total_old = 220

    saudi_weights = np.array([x[4] for x in saudi_hotspots], dtype=float)
    saudi_weights = saudi_weights / saudi_weights.sum()

    global_weights = np.array([x[4] for x in global_hotspots], dtype=float)
    global_weights = global_weights / global_weights.sum()

    # 150 من اليوم داخل السعودية تقريبًا
    saudi_today = 150
    global_today = total_today - saudi_today

    for _ in range(saudi_today):
        chosen_idx = np.random.choice(len(saudi_hotspots), p=saudi_weights)
        city, country, lat, lon, _ = saudi_hotspots[chosen_idx]

        category = np.random.choice(product_categories, p=product_probs)
        symptom = np.random.choice(symptoms, p=symptom_probs)
        source = np.random.choice(sources, p=source_probs)
        hazard = np.random.choice(hazards)
        status = np.random.choice(statuses, p=[0.46, 0.34, 0.20])
        level = np.random.choice(levels, p=[0.42, 0.36, 0.22])
        cases = np.random.randint(3, 45)

        rows.append({
            "alert_id": idx,
            "date": today,
            "city": city,
            "country": country,
            "lat": lat + np.random.normal(0, 0.14),
            "lon": lon + np.random.normal(0, 0.14),
            "product_category": category,
            "symptom": symptom,
            "source": source,
            "hazard": hazard,
            "status": status,
            "alert_level": level,
            "cases": cases,
            "title": f"{hazard} alert related to {category.lower()} products in {city}"
        })
        idx += 1

    for _ in range(global_today):
        if np.random.rand() < 0.7:
            chosen_idx = np.random.choice(len(global_hotspots), p=global_weights)
            city, country, lat, lon, _ = global_hotspots[chosen_idx]
            jitter_lat = np.random.normal(0, 0.18)
            jitter_lon = np.random.normal(0, 0.18)
        else:
            city, country, lat, lon = regular_places[np.random.randint(0, len(regular_places))]
            jitter_lat = np.random.normal(0, 0.20)
            jitter_lon = np.random.normal(0, 0.20)

        category = np.random.choice(product_categories, p=product_probs)
        symptom = np.random.choice(symptoms, p=symptom_probs)
        source = np.random.choice(sources, p=source_probs)
        hazard = np.random.choice(hazards)
        status = np.random.choice(statuses, p=[0.46, 0.34, 0.20])
        level = np.random.choice(levels, p=[0.42, 0.36, 0.22])
        cases = np.random.randint(3, 40)

        rows.append({
            "alert_id": idx,
            "date": today,
            "city": city,
            "country": country,
            "lat": lat + jitter_lat,
            "lon": lon + jitter_lon,
            "product_category": category,
            "symptom": symptom,
            "source": source,
            "hazard": hazard,
            "status": status,
            "alert_level": level,
            "cases": cases,
            "title": f"{hazard} alert related to {category.lower()} products in {city}"
        })
        idx += 1

    # البيانات القديمة
    all_old_places = [(x[0], x[1], x[2], x[3]) for x in saudi_hotspots] + [(x[0], x[1], x[2], x[3]) for x in global_hotspots] + regular_places

    for _ in range(total_old):
        # برضه نخلي السعودية فيها كثافة أكبر
        if np.random.rand() < 0.45:
            chosen_idx = np.random.choice(len(saudi_hotspots), p=saudi_weights)
            city, country, lat, lon, _ = saudi_hotspots[chosen_idx]
            jitter_lat = np.random.normal(0, 0.15)
            jitter_lon = np.random.normal(0, 0.15)
        else:
            city, country, lat, lon = all_old_places[np.random.randint(0, len(all_old_places))]
            jitter_lat = np.random.normal(0, 0.22)
            jitter_lon = np.random.normal(0, 0.22)

        category = np.random.choice(product_categories, p=product_probs)
        symptom = np.random.choice(symptoms, p=symptom_probs)
        source = np.random.choice(sources, p=source_probs)
        hazard = np.random.choice(hazards)
        status = np.random.choice(statuses, p=[0.35, 0.40, 0.25])
        level = np.random.choice(levels, p=[0.35, 0.40, 0.25])
        cases = np.random.randint(1, 30)
        days_back = np.random.randint(1, 31)

        rows.append({
            "alert_id": idx,
            "date": today - timedelta(days=int(days_back)),
            "city": city,
            "country": country,
            "lat": lat + jitter_lat,
            "lon": lon + jitter_lon,
            "product_category": category,
            "symptom": symptom,
            "source": source,
            "hazard": hazard,
            "status": status,
            "alert_level": level,
            "cases": cases,
            "title": f"{hazard} concern involving {category.lower()} items in {city}"
        })
        idx += 1

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = generate_dummy_data()

# =========================================================
# TOP BAR
# =========================================================
st.markdown('<div class="top-bar">', unsafe_allow_html=True)

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns([1.35, 1.25, 1.1, 1.0])

with row1_col1:
    st.markdown("### Filters & Search")

with row1_col2:
    selected_category = st.selectbox(
        "Product Category",
        ["All"] + sorted(df["product_category"].unique().tolist()),
        index=0
    )

with row1_col3:
    selected_range = st.selectbox(
        "Date Range",
        ["Today", "Last 7 Days", "Last 30 Days", "All"],
        index=0
    )

with row1_col4:
    selected_source = st.selectbox(
        "Source",
        ["All"] + sorted(df["source"].unique().tolist()),
        index=0
    )

row2_col1, row2_col2, row2_col3 = st.columns([4, 1.2, 6])

with row2_col1:
    search_text = st.text_input("Search", placeholder="City / title / symptom")

with row2_col2:
    st.write("")
    st.write("")
    st.button(
        "🌙 Dark" if not is_dark else "☀️ Light",
        on_click=toggle_theme,
        use_container_width=True
    )

with row2_col3:
    st.write("")

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# APPLY FILTERS
# =========================================================
filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["product_category"] == selected_category]

today = pd.to_datetime(datetime.now().date())

if selected_range == "Today":
    filtered_df = filtered_df[filtered_df["date"] == today]
elif selected_range == "Last 7 Days":
    filtered_df = filtered_df[filtered_df["date"] >= today - pd.Timedelta(days=6)]
elif selected_range == "Last 30 Days":
    filtered_df = filtered_df[filtered_df["date"] >= today - pd.Timedelta(days=29)]

if selected_source != "All":
    filtered_df = filtered_df[filtered_df["source"] == selected_source]

if search_text:
    q = search_text.strip().lower()
    filtered_df = filtered_df[
        filtered_df["city"].str.lower().str.contains(q, na=False) |
        filtered_df["country"].str.lower().str.contains(q, na=False) |
        filtered_df["symptom"].str.lower().str.contains(q, na=False) |
        filtered_df["product_category"].str.lower().str.contains(q, na=False) |
        filtered_df["title"].str.lower().str.contains(q, na=False)
    ]

# =========================================================
# KPI VALUES
# =========================================================
total_alerts = len(filtered_df)
top_category = filtered_df["product_category"].mode()[0] if not filtered_df.empty else "-"
top_symptom = filtered_df["symptom"].mode()[0] if not filtered_df.empty else "-"

# =========================================================
# KPI CARDS
# =========================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card kpi-card kpi-blue">
        <div class="kpi-title">Total Alerts Detected</div>
        <div class="kpi-value">{total_alerts}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card kpi-card kpi-pink">
        <div class="kpi-title">Most Common Product Category</div>
        <div class="kpi-value">{top_category}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card kpi-card kpi-green">
        <div class="kpi-title">Most Mentioned Symptom</div>
        <div class="kpi-value">{top_symptom}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# MAP
# =========================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Map: Alerts per Region</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    map_df = filtered_df.copy()
    map_df["radius_glow"] = map_df["cases"] * 2600
    map_df["radius_core"] = map_df["cases"] * 900

    if is_dark:
        map_df["glow_color"] = [[255, 90, 90, 58]] * len(map_df)
        map_df["core_color"] = [[255, 82, 82, 182]] * len(map_df)
    else:
        map_df["glow_color"] = [[255, 120, 120, 46]] * len(map_df)
        map_df["core_color"] = [[255, 96, 96, 158]] * len(map_df)

    glow_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_radius="radius_glow",
        get_fill_color="glow_color",
        pickable=True,
        opacity=0.35,
    )

    core_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_radius="radius_core",
        get_fill_color="core_color",
        pickable=True,
        opacity=0.88,
    )

    tooltip = {
        "html": """
        <b>City:</b> {city}<br/>
        <b>Country:</b> {country}<br/>
        <b>Category:</b> {product_category}<br/>
        <b>Symptom:</b> {symptom}<br/>
        <b>Source:</b> {source}<br/>
        <b>Cases:</b> {cases}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "#1f2937",
            "borderRadius": "10px"
        }
    }

    deck = pdk.Deck(
        layers=[glow_layer, core_layer],
        initial_view_state=pdk.ViewState(
            latitude=23,
            longitude=24,
            zoom=1.15,
            pitch=0
        ),
        map_style=MAP_STYLE,
        tooltip=tooltip
    )

    st.pydeck_chart(deck, use_container_width=True, height=460)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# CHARTS
# =========================================================
left_col, right_col = st.columns([1.35, 1])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Product Category Chart</div>', unsafe_allow_html=True)

    cat_df = filtered_df["product_category"].value_counts().reset_index()
    cat_df.columns = ["Product Category", "Count"]

    if cat_df.empty:
        st.info("No category data.")
    else:
        color_map = {
            "Dairy": "#59b7ff",
            "Poultry": "#ff6788",
            "Vegetables": "#7ed957",
            "Seafood": "#ff7f66",
            "Other": "#a579ff"
        }

        fig_bar = px.bar(
            cat_df,
            x="Product Category",
            y="Count",
            color="Product Category",
            color_discrete_map=color_map
        )

        fig_bar.update_traces(
            marker_line_width=1.5,
            marker_line_color="rgba(255,255,255,0.55)"
        )

        fig_bar.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="",
            yaxis_title="",
            font=dict(color=TEXT)
        )

        fig_bar.update_xaxes(showgrid=False)
        fig_bar.update_yaxes(gridcolor=GRID)

        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Symptom Frequency</div>', unsafe_allow_html=True)

    symptom_df = filtered_df["symptom"].value_counts().reset_index()
    symptom_df.columns = ["Symptom", "Count"]

    if symptom_df.empty:
        st.info("No symptom data.")
    else:
        symptom_colors = {
            "Vomiting": "#63d89b",
            "Fever": "#ff7c5c",
            "Diarrhea": "#7da8ff",
            "Nausea": "#aa6cf7"
        }

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=symptom_df["Symptom"],
                    values=symptom_df["Count"],
                    hole=0.58,
                    marker=dict(
                        colors=[symptom_colors.get(s, "#cccccc") for s in symptom_df["Symptom"]]
                    ),
                    textinfo="label+percent"
                )
            ]
        )

        fig_donut.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(
                orientation="v",
                x=1.0,
                y=0.5,
                font=dict(color=TEXT)
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT)
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# OPTIONAL TABLE
# =========================================================
with st.expander("Show Dummy Data Table"):
    show_df = filtered_df.sort_values(["date", "cases"], ascending=[False, False]).reset_index(drop=True)
    st.dataframe(show_df, use_container_width=True)

saudi_count = (df["country"] == "Saudi Arabia").sum()

st.markdown(
    f'<div class="footer-note">Dummy data rows: {len(df)} | Saudi Arabia rows: {saudi_count} | Filtered rows: {len(filtered_df)} | Mode: {st.session_state.theme_mode}</div>',
    unsafe_allow_html=True
)
