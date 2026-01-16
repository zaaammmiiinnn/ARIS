import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Aadhaar Risk Intelligence System (ARIS)",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# GLOBAL UI STYLING
# ==================================================
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #f7f9fc 0%, #eef2f7 100%);
}
h1, h2, h3 {
    color: #1f2a44;
}
.kpi {
    background: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    text-align: center;
}
.section {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# PATHS
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_PATH = os.path.join(BASE_DIR, "assets", "india-soi.geojson")

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    state_df = pd.read_csv("data/processed/state_risk.csv")
    district_df = pd.read_csv("data/processed/district_risk.csv")
    return state_df, district_df

state_df, district_df = load_data()

# ==================================================
# LOAD INDIA SOI GEOJSON (COUNTRY LEVEL)
# ==================================================
if not os.path.exists(GEOJSON_PATH):
    st.error("❌ india-soi.geojson not found in frontend/assets/")
    st.stop()

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    india_geojson = json.load(f)

# ==================================================
# COMPUTE METRICS
# ==================================================
national_risk = round(state_df["risk_percent"].mean(), 2)

top5 = (
    state_df
    .sort_values("risk_percent", ascending=False)
    .head(5)
)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<h1 style="text-align:center;">🔐 Aadhaar Risk Intelligence System (ARIS)</h1>
<p style="text-align:center; font-size:16px; color:#555;">
India‑level Aadhaar risk overview using Survey of India boundaries
</p>
<hr>
""", unsafe_allow_html=True)

# ==================================================
# KPI CARDS
# ==================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="kpi">
        <h3>States Analysed</h3>
        <h1>{state_df["state"].nunique()}</h1>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi">
        <h3>Districts Analysed</h3>
        <h1>{district_df["district"].nunique()}</h1>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi">
        <h3>National Avg Risk (%)</h3>
        <h1>{national_risk}</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# INDIA MAP + TOP 5
# ==================================================
left, right = st.columns([2, 1])

# ---------------- INDIA MAP ----------------
with left:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🗺️ India Overview (Survey of India Boundary)")

    india_df = pd.DataFrame({
        "country": ["India"],
        "risk": [national_risk]
    })

    fig = px.choropleth(
        india_df,
        geojson=india_geojson,
        locations="country",
        featureidkey="properties.Source",
        color="risk",
        color_continuous_scale="Reds",
        range_color=(0, 100),
        labels={"risk": "Avg Risk (%)"}
    )

    fig.update_geos(
        projection_type="mercator",
        showland=True,
        landcolor="#f0f2f6",
        visible=False
    )

    fig.update_layout(
        height=550,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TOP 5 ----------------
with right:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🚨 Top 5 Risky States")

    bar_fig = px.bar(
        top5,
        x="risk_percent",
        y="state",
        orientation="h",
        color="risk_percent",
        color_continuous_scale="Reds",
        text="risk_percent"
    )

    bar_fig.update_layout(
        xaxis_title="Risk (%)",
        yaxis_title="",
        height=350,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(bar_fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# STATE TABLE
# ==================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📊 State‑Level Risk Breakdown")

st.dataframe(
    state_df.sort_values("risk_percent", ascending=False),
    width="stretch",
    height=420
)
st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# FOOTER
# ==================================================
st.markdown("""
<hr>
<center>
<small>
Map: Survey of India (SOI).  
Risk values derived from UIDAI update datasets.  
Risk ≠ Fraud.
</small>
</center>
""", unsafe_allow_html=True)
