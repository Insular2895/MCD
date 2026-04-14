from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data" / "processed"

sales = pd.read_csv(data_dir / "fact_sales_hourly.csv")

print("=== TOTAL SALES BY STORE ===")
store_summary = sales.groupby("store_id").agg(
    total_qty=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()
print(store_summary.to_string(index=False))

print("\n=== SALES BY HOUR ===")
hour_summary = sales.groupby("hour").agg(
    total_qty=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()
print(hour_summary.to_string(index=False))

print("\n=== CITY CENTER LUNCH VS EVENING ===")
s001 = sales[sales["store_id"] == "S001"]

lunch_s001 = s001[s001["hour"].isin([12, 13, 14])]["qty_sold"].sum()
evening_s001 = s001[s001["hour"].isin([18, 19, 20, 21, 22])]["qty_sold"].sum()

print(f"S001 lunch qty: {lunch_s001}")
print(f"S001 evening qty: {evening_s001}")

if evening_s001 > 0:
    ratio = round(lunch_s001 / evening_s001, 2)
    print(f"S001 lunch/evening ratio: {ratio}")

print("\n=== FAIR PERIOD IMPACT ===")
fair = sales[sales["is_fair_period"] == 1]
non_fair = sales[sales["is_fair_period"] == 0]

fair_summary = fair.groupby("store_id").agg(
    total_qty=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()

non_fair_summary = non_fair.groupby("store_id").agg(
    total_qty=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()

print("\nFair period:")
print(fair_summary.to_string(index=False))

print("\nNon fair period:")
print(non_fair_summary.to_string(index=False))

print("\n=== TOP PRODUCTS ===")
top_products = sales.groupby(["product_name"]).agg(
    total_qty=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
).reset_index().sort_values("total_qty", ascending=False)

print(top_products.head(10).to_string(index=False))

print("\n=== WEEKDAY SUMMARY ===")
weekday_summary = sales.groupby("day_of_week").agg(
    total_qty=("qty_sold", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()

weekday_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]
weekday_summary["day_of_week"] = pd.Categorical(
    weekday_summary["day_of_week"],
    categories=weekday_order,
    ordered=True
)
weekday_summary = weekday_summary.sort_values("day_of_week")

print(weekday_summary.to_string(index=False))

print("\nAnalyse terminée.")