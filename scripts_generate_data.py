import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

def generate(records=5000):
    np.random.seed(42)

    df = pd.DataFrame({
        "record_id": range(records),
        "timestamp": pd.date_range("2026-01-01", periods=records, freq="min"),
        "wafer_id": [f"WAFER_{i%250}" for i in range(records)],
        "lot_id": [f"LOT_{i%50}" for i in range(records)],
        "process_node_nm": np.random.choice([2,3,5,7,14], records, p=[.08,.20,.32,.25,.15]),
        "required_time_ns": np.round(np.random.uniform(1.5, 9.5, records), 3),
        "arrival_time_ns": np.round(np.random.uniform(1.0, 10.8, records), 3),
        "temperature_c": np.round(np.random.normal(74, 11, records), 3),
        "leakage_power_mw": np.round(np.random.uniform(5, 95, records), 3),
        "dynamic_power_mw": np.round(np.random.uniform(10, 180, records), 3),
        "routing_utilization": np.round(np.random.uniform(35, 99, records), 3),
        "overflow_count": np.random.randint(0, 80, records),
        "defect_density": np.round(np.random.uniform(.05, 6.8, records), 3),
        "test_time_sec": np.round(np.random.uniform(20, 420, records), 3),
        "test_coverage_pct": np.round(np.random.uniform(82, 99.9, records), 3),
        "fail_rate_pct": np.round(np.random.uniform(.2, 17, records), 3),
        "good_chips": np.random.randint(720, 1000, records),
        "total_chips": 1000,
        "center_defect_score": np.round(np.random.uniform(0, 1, records), 3),
        "edge_defect_score": np.round(np.random.uniform(0, 1, records), 3),
        "scratch_score": np.round(np.random.uniform(0, 1, records), 3),
        "cluster_score": np.round(np.random.uniform(0, 1, records), 3),
    })

    df["slack_ns"] = np.round(df["required_time_ns"] - df["arrival_time_ns"], 3)
    df["yield_pct"] = np.round(df["good_chips"] / df["total_chips"] * 100, 3)
    df["congestion_score"] = np.round((df["routing_utilization"] * .65) + (df["overflow_count"] * .45), 3)

    # Inject business-like risk patterns
    high_risk = (df["temperature_c"] > 86) | (df["slack_ns"] < -1) | (df["defect_density"] > 4.3) | (df["congestion_score"] > 85)
    df.loc[high_risk, "yield_pct"] = np.maximum(70, df.loc[high_risk, "yield_pct"] - np.random.uniform(2, 9, high_risk.sum()))

    df.to_csv(RAW / "semiconductor_operations.csv", index=False)
    print(f"Generated {records} rows at {RAW / 'semiconductor_operations.csv'}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--records", type=int, default=5000)
    args = p.parse_args()
    generate(args.records)
