from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data" / "processed"

component_hourly = pd.read_csv(data_dir / "component_hourly_demand.csv")
components = pd.read_csv(data_dir / "components.csv")

# ----------------------------
# Aggregate hourly demand to daily demand
# ----------------------------
daily_demand = (
    component_hourly
    .groupby(["store_id", "date", "component_id"], as_index=False)
    .agg(daily_component_demand=("qty_component_needed", "sum"))
)

daily_demand = daily_demand.merge(
    components[
        [
            "component_id",
            "component_name",
            "component_type",
            "storage_zone",
            "unit_type",
            "units_per_case",
            "unit_cost",
            "shelf_life_days",
            "waste_ratio_ops",
            "waste_ratio_dlc",
        ]
    ],
    on="component_id",
    how="left"
)

daily_demand["date"] = pd.to_datetime(daily_demand["date"])
daily_demand = daily_demand.sort_values(["store_id", "component_id", "date"]).reset_index(drop=True)

# ----------------------------
# Assumptions by storage zone
# ----------------------------
def lead_time_days(storage_zone):
    if storage_zone == "negative":
        return 2
    if storage_zone == "cold":
        return 2
    if storage_zone == "dry":
        return 3
    return 2

def target_cover_days(storage_zone):
    if storage_zone == "negative":
        return 3
    if storage_zone == "cold":
        return 4
    if storage_zone == "dry":
        return 5
    return 4

def safety_factor(storage_zone):
    if storage_zone == "negative":
        return 0.35
    if storage_zone == "cold":
        return 0.30
    if storage_zone == "dry":
        return 0.25
    return 0.30

# ----------------------------
# Compute stock simulation
# ----------------------------
results = []

for (store_id, component_id), grp in daily_demand.groupby(["store_id", "component_id"]):
    grp = grp.sort_values("date").copy()

    avg_daily_demand = grp["daily_component_demand"].mean()
    units_per_case = float(grp["units_per_case"].iloc[0])
    storage_zone = grp["storage_zone"].iloc[0]
    unit_cost = float(grp["unit_cost"].iloc[0])
    waste_ratio_ops = float(grp["waste_ratio_ops"].iloc[0])
    waste_ratio_dlc = float(grp["waste_ratio_dlc"].iloc[0])

    lt_days = lead_time_days(storage_zone)
    cover_days = target_cover_days(storage_zone)
    sf = safety_factor(storage_zone)

    demand_std = grp["daily_component_demand"].std()
    if pd.isna(demand_std):
        demand_std = 0.0

    safety_stock_units = avg_daily_demand * sf + demand_std * 0.5
    reorder_point_units = avg_daily_demand * lt_days + safety_stock_units
    target_stock_units = avg_daily_demand * cover_days + safety_stock_units

    # Initial stock: enough to cover target stock at start
    current_stock_units = max(target_stock_units, avg_daily_demand * 2)

    for _, row in grp.iterrows():
        daily_component_demand = float(row["daily_component_demand"])
        waste_ops_units = daily_component_demand * waste_ratio_ops
        waste_dlc_units = daily_component_demand * waste_ratio_dlc

        total_outflow_units = daily_component_demand + waste_ops_units + waste_dlc_units

        opening_stock_units = current_stock_units
        closing_stock_pre_order_units = opening_stock_units - total_outflow_units

        order_recommended_units = 0.0
        order_recommended_cases = 0

        if closing_stock_pre_order_units <= reorder_point_units:
            gap_to_target = max(target_stock_units - closing_stock_pre_order_units, 0)

            if units_per_case > 0:
                order_recommended_cases = int(np.ceil(gap_to_target / units_per_case))
                order_recommended_units = order_recommended_cases * units_per_case
            else:
                order_recommended_units = gap_to_target
                order_recommended_cases = 0

        closing_stock_post_order_units = closing_stock_pre_order_units + order_recommended_units

        stockout_risk_flag = 1 if closing_stock_pre_order_units < 0 else 0
        low_stock_flag = 1 if closing_stock_pre_order_units <= reorder_point_units else 0
        waste_risk_flag = 1 if waste_dlc_units > (daily_component_demand * 0.03) else 0

        results.append({
            "store_id": store_id,
            "date": row["date"].date(),
            "component_id": component_id,
            "component_name": row["component_name"],
            "component_type": row["component_type"],
            "storage_zone": storage_zone,
            "unit_type": row["unit_type"],
            "units_per_case": units_per_case,
            "unit_cost": unit_cost,
            "daily_component_demand": round(daily_component_demand, 2),
            "waste_ops_units": round(waste_ops_units, 2),
            "waste_dlc_units": round(waste_dlc_units, 2),
            "total_outflow_units": round(total_outflow_units, 2),
            "opening_stock_units": round(opening_stock_units, 2),
            "closing_stock_pre_order_units": round(closing_stock_pre_order_units, 2),
            "avg_daily_demand": round(avg_daily_demand, 2),
            "demand_std": round(demand_std, 2),
            "lead_time_days": lt_days,
            "safety_stock_units": round(safety_stock_units, 2),
            "reorder_point_units": round(reorder_point_units, 2),
            "target_stock_units": round(target_stock_units, 2),
            "order_recommended_units": round(order_recommended_units, 2),
            "order_recommended_cases": order_recommended_cases,
            "closing_stock_post_order_units": round(closing_stock_post_order_units, 2),
            "stockout_risk_flag": stockout_risk_flag,
            "low_stock_flag": low_stock_flag,
            "waste_risk_flag": waste_risk_flag,
            "recommended_order_value": round(order_recommended_units * unit_cost, 2),
        })

        current_stock_units = closing_stock_post_order_units

inventory_replenishment = pd.DataFrame(results)

inventory_replenishment.to_csv(data_dir / "inventory_replenishment_daily.csv", index=False)

print(inventory_replenishment.head().to_string(index=False))
print("\nRows:", len(inventory_replenishment))
print("Total recommended order value:", round(inventory_replenishment["recommended_order_value"].sum(), 2))
print("Total stockout risk flags:", int(inventory_replenishment["stockout_risk_flag"].sum()))
print("Total low stock flags:", int(inventory_replenishment["low_stock_flag"].sum()))
print("Total waste risk flags:", int(inventory_replenishment["waste_risk_flag"].sum()))
print("\ninventory_replenishment_daily.csv créé dans data/processed/")