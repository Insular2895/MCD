from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = DATA_DIR / "order_recommendations.csv"

# =========================
# LOAD
# =========================
inventory = pd.read_csv(DATA_DIR / "inventory_replenishment_daily.csv")
components = pd.read_csv(DATA_DIR / "components.csv")

# =========================
# CLEAN TYPES
# =========================
numeric_cols = [
    "daily_component_demand",
    "opening_stock_units",
    "closing_stock_pre_order_units",
    "closing_stock_post_order_units",
    "avg_daily_demand",
    "demand_std",
    "safety_stock_units",
    "reorder_point_units",
    "target_stock_units",
    "order_recommended_units",
    "order_recommended_cases",
    "recommended_order_value",
    "unit_cost",
    "units_per_case",
]

for col in numeric_cols:
    if col in inventory.columns:
        inventory[col] = pd.to_numeric(inventory[col], errors="coerce")

if "unit_cost" in components.columns:
    components["unit_cost"] = pd.to_numeric(components["unit_cost"], errors="coerce")
if "units_per_case" in components.columns:
    components["units_per_case"] = pd.to_numeric(components["units_per_case"], errors="coerce")

inventory["date"] = pd.to_datetime(inventory["date"], errors="coerce")

# =========================
# BUILD NEXT 3 DAYS FORECAST
# =========================
inventory = inventory.sort_values(["store_id", "component_id", "date"]).copy()

inventory["forecast_d1"] = inventory.groupby(["store_id", "component_id"])["daily_component_demand"].shift(-1)
inventory["forecast_d2"] = inventory.groupby(["store_id", "component_id"])["daily_component_demand"].shift(-2)
inventory["forecast_d3"] = inventory.groupby(["store_id", "component_id"])["daily_component_demand"].shift(-3)

inventory[["forecast_d1", "forecast_d2", "forecast_d3"]] = inventory[
    ["forecast_d1", "forecast_d2", "forecast_d3"]
].fillna(0)

inventory["forecast_next_3d"] = (
    inventory["forecast_d1"] + inventory["forecast_d2"] + inventory["forecast_d3"]
)

# =========================
# CURRENT STOCK BASE
# =========================
# On prend le stock post-order comme stock "réel" de fin de journée disponible pour la suite
inventory["current_stock_units"] = inventory["closing_stock_post_order_units"].fillna(0)

# =========================
# RECOMMENDED ORDER LOGIC
# =========================
def compute_recommended_units(row):
    current_stock = row["current_stock_units"]
    reorder_point = row["reorder_point_units"]
    target_stock = row["target_stock_units"]
    forecast_3d = row["forecast_next_3d"]
    units_per_case = row["units_per_case"]

    if pd.isna(units_per_case) or units_per_case <= 0:
        units_per_case = 1

    # Base need:
    # - if below reorder point, replenish up to target
    # - if next 3 days forecast is above current stock, cover shortage too
    replenish_gap = max(target_stock - current_stock, 0)
    forecast_gap = max(forecast_3d - current_stock, 0)

    raw_need = max(replenish_gap, forecast_gap)

    if raw_need <= 0:
        return 0.0

    # Round to case size
    cases = np.ceil(raw_need / units_per_case)
    return float(cases * units_per_case)

inventory["recommended_order_units_v2"] = inventory.apply(compute_recommended_units, axis=1)
inventory["recommended_order_cases_v2"] = (
    inventory["recommended_order_units_v2"] / inventory["units_per_case"].replace(0, np.nan)
).fillna(0)

inventory["recommended_order_value_v2"] = (
    inventory["recommended_order_units_v2"] * inventory["unit_cost"]
).fillna(0)

# =========================
# URGENCY LOGIC
# =========================
def compute_urgency(row):
    current_stock = row["current_stock_units"]
    reorder_point = row["reorder_point_units"]
    safety_stock = row["safety_stock_units"]
    forecast_3d = row["forecast_next_3d"]
    stockout_flag = row.get("stockout_risk_flag", 0)
    low_stock_flag = row.get("low_stock_flag", 0)

    if current_stock <= 0 or stockout_flag == 1:
        return "critical"
    if current_stock < safety_stock:
        return "high"
    if current_stock < reorder_point or low_stock_flag == 1:
        return "medium"
    if forecast_3d > current_stock:
        return "medium"
    return "low"

inventory["urgency_level"] = inventory.apply(compute_urgency, axis=1)

# =========================
# JUSTIFICATION
# =========================
def build_justification(row):
    reasons = []

    if row.get("stockout_risk_flag", 0) == 1:
        reasons.append("stockout risk")
    if row.get("low_stock_flag", 0) == 1:
        reasons.append("below reorder threshold")
    if row["current_stock_units"] < row["safety_stock_units"]:
        reasons.append("below safety stock")
    if row["forecast_next_3d"] > row["current_stock_units"]:
        reasons.append("next 3d demand exceeds current stock")
    if row.get("waste_risk_flag", 0) == 1:
        reasons.append("monitor waste risk")

    if not reasons:
        reasons.append("stable stock position")

    return " | ".join(reasons)

inventory["justification"] = inventory.apply(build_justification, axis=1)

# =========================
# KEEP USEFUL OUTPUT ONLY
# =========================
output = inventory[
    [
        "store_id",
        "date",
        "component_id",
        "component_name",
        "storage_zone",
        "unit_type",
        "units_per_case",
        "unit_cost",
        "current_stock_units",
        "reorder_point_units",
        "target_stock_units",
        "forecast_d1",
        "forecast_d2",
        "forecast_d3",
        "forecast_next_3d",
        "recommended_order_units_v2",
        "recommended_order_cases_v2",
        "recommended_order_value_v2",
        "urgency_level",
        "justification",
    ]
].copy()

output = output.rename(
    columns={
        "recommended_order_units_v2": "recommended_order_units",
        "recommended_order_cases_v2": "recommended_order_cases",
        "recommended_order_value_v2": "recommended_order_value",
    }
)

# Optionnel: on garde seulement les lignes où une commande est utile
output_filtered = output[
    (output["recommended_order_units"] > 0) | (output["urgency_level"].isin(["critical", "high", "medium"]))
].copy()

output_filtered["date"] = output_filtered["date"].dt.strftime("%Y-%m-%d")

# Tri
urgency_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
output_filtered["urgency_rank"] = output_filtered["urgency_level"].map(urgency_order)

output_filtered = output_filtered.sort_values(
    ["date", "urgency_rank", "store_id", "recommended_order_value"],
    ascending=[True, True, True, False]
).drop(columns=["urgency_rank"])

# Save
output_filtered.to_csv(OUTPUT_PATH, index=False)

print("=== ORDER RECOMMENDATIONS PREVIEW ===")
print(output_filtered.head(20).to_string(index=False))

print("\nRows:", len(output_filtered))
print("Total recommended order value:", round(output_filtered["recommended_order_value"].sum(), 2))
print("Critical lines:", (output_filtered["urgency_level"] == "critical").sum())
print("High lines:", (output_filtered["urgency_level"] == "high").sum())
print("Medium lines:", (output_filtered["urgency_level"] == "medium").sum())

print(f"\nFile created: {OUTPUT_PATH}")