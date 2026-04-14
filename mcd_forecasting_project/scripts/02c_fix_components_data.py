from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
file_path = BASE_DIR / "data" / "processed" / "components.csv"

df = pd.read_csv(file_path)

unit_cost_map = {
    "C001": 0.28,
    "C002": 0.18,
    "C003": 0.55,
    "C004": 0.60,
    "C005": 0.16,
    "C006": 1.08,
    "C007": 0.09,
    "C008": 4.05,
    "C009": 3.05,
    "C010": 2.03,
    "C011": 18.00,
    "C012": 4.00,
    "C013": 2.05,
    "C014": 0.06,
    "C015": 0.04,
    "C016": 0.04,
    "C017": 0.05,
    "C018": 0.07,
    "C019": 0.03,
    "C020": 0.04,
    "C021": 0.03,
    "C022": 0.04,
    "C023": 0.01,
    "C024": 0.01,
    "C025": 0.005,
    "C026": 0.03,
    "C027": 0.04,
    "C028": 0.01,
    "C029": 0.002,
}

df["unit_cost"] = df["component_id"].map(unit_cost_map)

if df["unit_cost"].isna().sum() > 0:
    missing_ids = df.loc[df["unit_cost"].isna(), "component_id"].tolist()
    raise ValueError(f"Unit costs missing for: {missing_ids}")

df["storage_zone"] = df["storage_zone"].replace({"stock_dry": "dry"})

df.to_csv(file_path, index=False)

print(df[["component_id", "component_name", "unit_cost", "storage_zone"]].to_string(index=False))
print("\ncomponents.csv corrigé.")