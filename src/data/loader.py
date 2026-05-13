from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "raw" / "semiconductor_operations.csv"

def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError("Sample data not found. Run: python scripts_generate_data.py --records 5000")
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    return df
