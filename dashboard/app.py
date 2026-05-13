import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import pandas as pd

from src.data.loader import load_data
from src.ai.engine import enrich, kpis, recommendations, root_causes
from src.reports.pdf import create_pdf

st.set_page_config(
    page_title="Accusaga Semiconductor AI Command Center",
    page_icon="🧠",
    layout="wide"
)

st_autorefresh(interval=60000, key="realtime_refresh")

st.markdown("""
<style>
.main {background-color: #f6f8fb;}
.block-container {padding-top: 1.2rem;}
.metric-card {
    background: linear-gradient(135deg, #ffffff, #eef4ff);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,.08);
    border: 1px solid #e2e8f0;
}
.hero {
    background: linear-gradient(135deg, #0f4c81, #173b63);
    color: white;
    padding: 26px;
    border-radius: 22px;
    margin-bottom: 18px;
}
.hero h1 {margin-bottom: 0px;}
.small-text {color:#64748b; font-size:14px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>Accusaga Semiconductor AI Command Center</h1>
<p>Enterprise demo for predictive semiconductor operations, AI-driven engineering intelligence, ROI improvement, and real-time decision support.</p>
</div>
""", unsafe_allow_html=True)

try:
    df = enrich(load_data())
except Exception as e:
    st.error(str(e))
    st.info("Run this command first: python scripts_generate_data.py --records 5000")
    st.stop()

with st.sidebar:
    st.header("Demo Controls")
    lot = st.selectbox("Select Lot", ["All"] + sorted(df["lot_id"].unique().tolist()))
    node = st.selectbox("Process Node", ["All"] + sorted(df["process_node_nm"].astype(str).unique().tolist()))
    live_rows = st.slider("Real-time display window", 100, 2000, 500, 100)

filtered = df.copy()
if lot != "All":
    filtered = filtered[filtered["lot_id"] == lot]
if node != "All":
    filtered = filtered[filtered["process_node_nm"].astype(str) == node]

view = filtered.tail(live_rows)
K = kpis(view)
recs = recommendations(view)

tabs = st.tabs([
    "Executive Cockpit",
    "Real-Time AI Operations",
    "AI Model Layer",
    "Root Cause & Recommendations",
    "ROI & Business Impact",
    "Accusaga Capability Map",
    "Executive Report"
])

with tabs[0]:
    st.subheader("Executive Cockpit")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records Processed", f"{K['records']:,}")
    c2.metric("Predicted Yield", f"{K['yield']}%")
    c3.metric("Avg Failure Risk", f"{K['risk']}%")
    c4.metric("Estimated ROI Impact", f"${K['roi']:,.0f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Timing Violations", K["timing"])
    c6.metric("Thermal Hotspots", K["hotspots"])
    c7.metric("Congestion Risks", K["congestion"])
    c8.metric("Power Anomalies", K["power"])

    st.plotly_chart(px.line(view, x="timestamp", y=["predicted_yield_pct","ai_failure_risk_pct"],
                            title="Live Yield vs Failure Risk Trend"), use_container_width=True)

with tabs[1]:
    st.subheader("Real-Time AI Operations")
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.scatter(view, x="temperature_c", y="ai_failure_risk_pct",
                               color="thermal_hotspot", size="defect_density",
                               title="Thermal Risk Intelligence"), use_container_width=True)
    c2.plotly_chart(px.density_heatmap(view, x="routing_utilization", y="overflow_count",
                                       z="congestion_score", title="Routing Congestion Heatmap"),
                    use_container_width=True)

    st.dataframe(view[["timestamp","wafer_id","lot_id","predicted_yield_pct","ai_failure_risk_pct",
                       "recommended_bin","test_action"]].tail(50), use_container_width=True)

with tabs[2]:
    st.subheader("Executive AI / ML Models Layer")
    model_cards = [
        ("Yield Prediction", "Predict wafer, lot and manufacturing yield."),
        ("Defect Anomaly Detection", "Detect abnormal dies, latent defects and process anomalies."),
        ("Wafer Pattern Recognition", "Identify center, edge, scratch and cluster defect patterns."),
        ("Reliability Prediction", "Estimate failure probability and device degradation risk."),
        ("Dynamic Binning", "Optimize product binning for value and yield utilization."),
        ("Test-Time Optimization", "Reduce redundant testing while protecting coverage."),
        ("Drift Detection", "Identify process, yield and manufacturing drift."),
        ("Explainable AI", "Explain why risk is high using engineering indicators.")
    ]
    cols = st.columns(2)
    for i, (title, text) in enumerate(model_cards):
        with cols[i % 2]:
            st.container(border=True).markdown(f"### {title}\n{text}")

    st.plotly_chart(px.histogram(view, x="wafer_pattern", color="wafer_pattern",
                                 title="Wafer Pattern Recognition Output"), use_container_width=True)
    st.plotly_chart(px.histogram(view, x="recommended_bin", color="recommended_bin",
                                 title="Dynamic Binning Optimization"), use_container_width=True)

with tabs[3]:
    st.subheader("Root Cause Analysis & AI Recommendations")
    sample = view.copy().tail(200)
    sample["root_cause"] = sample.apply(root_causes, axis=1)
    st.dataframe(sample[["wafer_id","lot_id","ai_failure_risk_pct","root_cause","test_action"]]
                 .sort_values("ai_failure_risk_pct", ascending=False).head(50),
                 use_container_width=True)

    st.markdown("### AI Recommendations")
    for title, msg in recs:
        st.success(f"**{title}:** {msg}")

with tabs[4]:
    st.subheader("ROI & Business Impact")
    roi = pd.DataFrame({
        "Business Lever": [
            "Engineering Automation", "Faster Root Cause Analysis", "Yield Improvement",
            "Test-Time Optimization", "Predictive Monitoring", "Infrastructure Optimization"
        ],
        "Client Problem Solved": [
            "Manual report review", "Delayed debugging", "Scrap and yield loss",
            "High validation cost", "Late issue detection", "High compute/storage cost"
        ],
        "Accusaga AI Solution": [
            "Automated parsing and insight generation", "AI root-cause engine",
            "Predictive yield intelligence", "Test reduction recommendations",
            "Real-time risk monitoring", "Cloud-native scalable architecture"
        ],
        "ROI Impact": [
            "Higher productivity", "Lower debugging cost", "Improved profitability",
            "Reduced manufacturing cycle time", "Lower downtime risk", "Optimized spend"
        ]
    })
    st.dataframe(roi, use_container_width=True)
    st.plotly_chart(px.bar(roi, x="Business Lever", y=[1,1,1,1,1,1],
                           title="ROI Levers Enabled by Accusaga", text="ROI Impact"),
                    use_container_width=True)

with tabs[5]:
    st.subheader("Accusaga Capability Map")
    cap = pd.DataFrame({
        "Resource Group": [
            "AI Solution Architects", "Data Engineers", "ML Engineers",
            "Software Engineers", "Visualization Experts", "Domain Experts"
        ],
        "Capability": [
            "Enterprise AI architecture and cloud roadmap",
            "Kafka, Spark, ETL and billion-scale data pipelines",
            "Predictive models, anomaly detection, XAI",
            "Streamlit/FastAPI platforms, security, APIs",
            "Executive dashboards and KPI storytelling",
            "Semiconductor workflow validation and business alignment"
        ],
        "Client Value": [
            "Future-ready transformation", "1B+ record processing",
            "Predictive intelligence", "Production-grade applications",
            "Decision visibility", "Domain-specific accuracy"
        ]
    })
    st.dataframe(cap, use_container_width=True)

with tabs[6]:
    st.subheader("Executive Report")
    st.write("Generate a client-ready PDF report with KPIs and AI recommendations.")
    if st.button("Generate PDF Report"):
        path = create_pdf(K, recs)
        with open(path, "rb") as f:
            st.download_button("Download Executive PDF", f, file_name="accusaga_semiconductor_ai_executive_report.pdf")
