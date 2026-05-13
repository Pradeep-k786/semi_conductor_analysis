import numpy as np
import pandas as pd

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timing_violation"] = df["slack_ns"] < 0
    df["thermal_hotspot"] = df["temperature_c"] > 85
    df["power_anomaly"] = df["leakage_power_mw"] > df["leakage_power_mw"].quantile(.90)
    df["congestion_risk"] = df["congestion_score"] > 85

    df["wafer_pattern"] = df[["center_defect_score","edge_defect_score","scratch_score","cluster_score"]].idxmax(axis=1)
    df["wafer_pattern"] = df["wafer_pattern"].str.replace("_score","").str.replace("_defect","").str.title()

    risk = (
        (df["thermal_hotspot"].astype(int) * 22) +
        (df["timing_violation"].astype(int) * 25) +
        (df["power_anomaly"].astype(int) * 15) +
        (df["congestion_risk"].astype(int) * 18) +
        (df["defect_density"] * 4)
    )
    df["ai_failure_risk_pct"] = np.clip(np.round(risk, 2), 0, 99)

    df["predicted_yield_pct"] = np.round(
        df["yield_pct"] 
        - df["thermal_hotspot"].astype(int) * 2.1
        - df["timing_violation"].astype(int) * 1.8
        - df["congestion_risk"].astype(int) * 1.4
        - np.maximum(0, df["defect_density"] - 3) * 1.2,
        2
    )

    df["recommended_bin"] = np.select(
        [
            (df["predicted_yield_pct"] >= 95) & (df["ai_failure_risk_pct"] < 20),
            (df["predicted_yield_pct"] >= 90) & (df["ai_failure_risk_pct"] < 40),
            (df["predicted_yield_pct"] >= 85),
        ],
        ["Premium Bin", "Performance Bin", "Standard Bin"],
        default="Recovery Bin"
    )

    df["test_action"] = np.select(
        [
            (df["test_coverage_pct"] > 96) & (df["fail_rate_pct"] < 3) & (df["test_time_sec"] > 150),
            df["fail_rate_pct"] > 10,
            df["test_coverage_pct"] < 90
        ],
        ["Reduce redundant test steps", "Increase diagnostic testing", "Improve test coverage"],
        default="Maintain current flow"
    )

    return df

def kpis(df):
    return {
        "records": len(df),
        "yield": round(float(df["predicted_yield_pct"].mean()), 2),
        "risk": round(float(df["ai_failure_risk_pct"].mean()), 2),
        "timing": int(df["timing_violation"].sum()),
        "hotspots": int(df["thermal_hotspot"].sum()),
        "congestion": int(df["congestion_risk"].sum()),
        "power": int(df["power_anomaly"].sum()),
        "roi": estimate_roi(df)
    }

def estimate_roi(df):
    base_engineering_hours = len(df) * 0.002
    automated_hours_saved = base_engineering_hours * 0.55
    yield_gain_value = max(0, 92 - df["predicted_yield_pct"].mean()) * 12000
    test_saving = (df["test_action"] == "Reduce redundant test steps").sum() * 18
    return round(automated_hours_saved * 65 + yield_gain_value + test_saving, 2)

def recommendations(df):
    out = []
    if df["timing_violation"].sum() > 0:
        out.append(("Timing Risk", "Prioritize critical negative slack paths and optimize clock tree / logic depth."))
    if df["thermal_hotspot"].sum() > 0:
        out.append(("Thermal Hotspots", "Improve floorplanning, rebalance workloads, and introduce proactive thermal throttling."))
    if df["congestion_risk"].sum() > 0:
        out.append(("Routing Congestion", "Apply congestion-aware placement and optimize high-density routing zones."))
    if df["power_anomaly"].sum() > 0:
        out.append(("Power Leakage", "Use clock gating, voltage scaling, and leakage-aware optimization."))
    if df["predicted_yield_pct"].mean() < 92:
        out.append(("Yield Improvement", "Investigate defect density, wafer patterns, process drift, and thermal correlation."))
    out.append(("Executive Action", "Move from reactive engineering reviews to predictive semiconductor operations."))
    return out

def root_causes(row):
    causes = []
    if row["temperature_c"] > 85: causes.append("Thermal hotspot")
    if row["slack_ns"] < 0: causes.append("Negative timing slack")
    if row["leakage_power_mw"] > 75: causes.append("High leakage power")
    if row["congestion_score"] > 85: causes.append("Routing congestion")
    if row["defect_density"] > 4: causes.append("High defect density")
    return ", ".join(causes) if causes else "No major risk driver"
