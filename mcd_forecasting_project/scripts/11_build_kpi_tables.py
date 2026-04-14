from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data" / "processed"

sales = pd.read_csv(data_dir / "fact_sales_hourly.csv")
inventory = pd.read_csv(data_dir / "inventory_replenishment_daily.csv")
component_demand = pd.read_csv(data_dir / "component_hourly_demand.csv")

# ----------------------------
# 1. Network sales summary
# ----------------------------
network_sales_summary = sales.groupby("store_id", as_index=False).agg(
    total_qty_sold=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
)

# ----------------------------
# 2. Sales by hour
# ----------------------------
sales_by_hour = sales.groupby("hour", as_index=False).agg(
    total_qty_sold=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
)

# ----------------------------
# 3. Top products
# ----------------------------
top_products = (
    sales.groupby(["store_id", "product_name"], as_index=False)
    .agg(
        total_qty_sold=("qty_sold", "sum"),
        total_revenue=("revenue", "sum")
    )
    .sort_values(["store_id", "total_qty_sold"], ascending=[True, False])
)

# ----------------------------
# 4. Inventory KPI by store
# ----------------------------
inventory_kpi_by_store = inventory.groupby("store_id", as_index=False).agg(
    total_order_value=("recommended_order_value", "sum"),
    total_order_cases=("order_recommended_cases", "sum"),
    stockout_flags=("stockout_risk_flag", "sum"),
    low_stock_flags=("low_stock_flag", "sum"),
    waste_risk_flags=("waste_risk_flag", "sum")
)

# ----------------------------
# 5. Top ordered components
# ----------------------------
top_ordered_components = (
    inventory.groupby(["store_id", "component_name"], as_index=False)
    .agg(
        total_order_units=("order_recommended_units", "sum"),
        total_order_cases=("order_recommended_cases", "sum"),
        total_order_value=("recommended_order_value", "sum")
    )
    .sort_values(["store_id", "total_order_value"], ascending=[True, False])
)

# ----------------------------
# 6. Top consumed components
# ----------------------------
top_consumed_components = (
    component_demand.groupby(["store_id", "component_name", "storage_zone"], as_index=False)
    .agg(
        total_component_qty=("qty_component_needed", "sum")
    )
    .sort_values(["store_id", "total_component_qty"], ascending=[True, False])
)

# ----------------------------
# 7. Daily store KPI
# ----------------------------
daily_store_sales = (
    sales.groupby(["store_id", "date"], as_index=False)
    .agg(
        total_qty_sold=("qty_sold", "sum"),
        total_revenue=("revenue", "sum")
    )
)

daily_store_inventory = (
    inventory.groupby(["store_id", "date"], as_index=False)
    .agg(
        total_order_value=("recommended_order_value", "sum"),
        stockout_flags=("stockout_risk_flag", "sum"),
        low_stock_flags=("low_stock_flag", "sum"),
        waste_risk_flags=("waste_risk_flag", "sum")
    )
)

daily_store_kpi = daily_store_sales.merge(
    daily_store_inventory,
    on=["store_id", "date"],
    how="left"
)

# ----------------------------
# Export all KPI tables
# ----------------------------
network_sales_summary.to_csv(data_dir / "kpi_network_sales_summary.csv", index=False)
sales_by_hour.to_csv(data_dir / "kpi_sales_by_hour.csv", index=False)
top_products.to_csv(data_dir / "kpi_top_products.csv", index=False)
inventory_kpi_by_store.to_csv(data_dir / "kpi_inventory_by_store.csv", index=False)
top_ordered_components.to_csv(data_dir / "kpi_top_ordered_components.csv", index=False)
top_consumed_components.to_csv(data_dir / "kpi_top_consumed_components.csv", index=False)
daily_store_kpi.to_csv(data_dir / "kpi_daily_store_kpi.csv", index=False)

print("Files created:")
print("- kpi_network_sales_summary.csv")
print("- kpi_sales_by_hour.csv")
print("- kpi_top_products.csv")
print("- kpi_inventory_by_store.csv")
print("- kpi_top_ordered_components.csv")
print("- kpi_top_consumed_components.csv")
print("- kpi_daily_store_kpi.csv")

print("\n=== network_sales_summary ===")
print(network_sales_summary.to_string(index=False))

print("\n=== inventory_kpi_by_store ===")
print(inventory_kpi_by_store.to_string(index=False))

print("\n=== sales_by_hour ===")
print(sales_by_hour.to_string(index=False))