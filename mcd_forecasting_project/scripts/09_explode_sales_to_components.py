from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data" / "processed"

sales = pd.read_csv(data_dir / "fact_sales_hourly.csv")
bom = pd.read_csv(data_dir / "bom_recipes.csv")

menu_rules = pd.DataFrame([
    {
        "menu_product_id": "P014",
        "menu_product_name": "Menu Big Mac",
        "main_product_id": "P001",
        "main_product_name": "Big Mac",
        "fries_m_share": 0.75,
        "fries_l_share": 0.05,
        "other_side_share": 0.20,
        "coke_m_share": 0.75,
        "coke_l_share": 0.05,
        "other_drink_share": 0.20,
    },
    {
        "menu_product_id": "P015",
        "menu_product_name": "Menu McChicken",
        "main_product_id": "P003",
        "main_product_name": "McChicken",
        "fries_m_share": 0.75,
        "fries_l_share": 0.05,
        "other_side_share": 0.20,
        "coke_m_share": 0.75,
        "coke_l_share": 0.05,
        "other_drink_share": 0.20,
    },
])

finished_products = pd.read_csv(data_dir / "finished_products.csv")
components = pd.read_csv(data_dir / "components.csv")

# ----------------------------
# Helper maps
# ----------------------------
product_name_to_id = dict(zip(finished_products["product_name"], finished_products["product_id"]))
product_id_to_name = dict(zip(finished_products["product_id"], finished_products["product_name"]))

big_mac_id = product_name_to_id["Big Mac"]
mcchicken_id = product_name_to_id["McChicken"]
fries_m_id = product_name_to_id["Frites M"]
fries_l_id = product_name_to_id["Frites L"]
coke_m_id = product_name_to_id["Coca M"]
coke_l_id = product_name_to_id["Coca L"]

# ----------------------------
# Expand menu sales into underlying sellable products
# ----------------------------
expanded_rows = []

for _, row in sales.iterrows():
    store_id = row["store_id"]
    date = row["date"]
    hour = row["hour"]
    datetime_hour = row["datetime_hour"]
    product_id = row["product_id"]
    product_name = row["product_name"]
    qty_sold = row["qty_sold"]

    # non-menu products stay as-is
    if row["is_menu"] == 0:
        expanded_rows.append({
            "store_id": store_id,
            "date": date,
            "hour": hour,
            "datetime_hour": datetime_hour,
            "source_product_id": product_id,
            "source_product_name": product_name,
            "exploded_product_id": product_id,
            "exploded_product_name": product_name,
            "exploded_qty": qty_sold
        })
        continue

    # menu products are expanded
    menu_rule = menu_rules[menu_rules["menu_product_id"] == product_id].iloc[0]

    main_product_id = menu_rule["main_product_id"]
    main_product_name = menu_rule["main_product_name"]

    fries_m_share = float(menu_rule["fries_m_share"])
    fries_l_share = float(menu_rule["fries_l_share"])
    coke_m_share = float(menu_rule["coke_m_share"])
    coke_l_share = float(menu_rule["coke_l_share"])

    # Main burger in every menu
    expanded_rows.append({
        "store_id": store_id,
        "date": date,
        "hour": hour,
        "datetime_hour": datetime_hour,
        "source_product_id": product_id,
        "source_product_name": product_name,
        "exploded_product_id": main_product_id,
        "exploded_product_name": main_product_name,
        "exploded_qty": qty_sold
    })

    # Fries split
    expanded_rows.append({
        "store_id": store_id,
        "date": date,
        "hour": hour,
        "datetime_hour": datetime_hour,
        "source_product_id": product_id,
        "source_product_name": product_name,
        "exploded_product_id": fries_m_id,
        "exploded_product_name": "Frites M",
        "exploded_qty": qty_sold * fries_m_share
    })

    expanded_rows.append({
        "store_id": store_id,
        "date": date,
        "hour": hour,
        "datetime_hour": datetime_hour,
        "source_product_id": product_id,
        "source_product_name": product_name,
        "exploded_product_id": fries_l_id,
        "exploded_product_name": "Frites L",
        "exploded_qty": qty_sold * fries_l_share
    })

    # Coke split
    expanded_rows.append({
        "store_id": store_id,
        "date": date,
        "hour": hour,
        "datetime_hour": datetime_hour,
        "source_product_id": product_id,
        "source_product_name": product_name,
        "exploded_product_id": coke_m_id,
        "exploded_product_name": "Coca M",
        "exploded_qty": qty_sold * coke_m_share
    })

    expanded_rows.append({
        "store_id": store_id,
        "date": date,
        "hour": hour,
        "datetime_hour": datetime_hour,
        "source_product_id": product_id,
        "source_product_name": product_name,
        "exploded_product_id": coke_l_id,
        "exploded_product_name": "Coca L",
        "exploded_qty": qty_sold * coke_l_share
    })

expanded_sales = pd.DataFrame(expanded_rows)

# Aggregate exploded product demand
exploded_product_demand = (
    expanded_sales
    .groupby(
        ["store_id", "date", "hour", "datetime_hour", "exploded_product_id", "exploded_product_name"],
        as_index=False
    )["exploded_qty"]
    .sum()
)

exploded_product_demand.to_csv(data_dir / "exploded_product_demand.csv", index=False)

# ----------------------------
# Convert exploded products into components using BOM
# ----------------------------
component_rows = []

for _, sale_row in exploded_product_demand.iterrows():
    exploded_product_id = sale_row["exploded_product_id"]
    exploded_qty = float(sale_row["exploded_qty"])

    matching_bom = bom[bom["product_id"] == exploded_product_id]

    for _, bom_row in matching_bom.iterrows():
        component_rows.append({
            "store_id": sale_row["store_id"],
            "date": sale_row["date"],
            "hour": sale_row["hour"],
            "datetime_hour": sale_row["datetime_hour"],
            "product_id": exploded_product_id,
            "product_name": sale_row["exploded_product_name"],
            "component_id": bom_row["component_id"],
            "qty_component_needed": exploded_qty * float(bom_row["qty_per_product"])
        })

component_demand = pd.DataFrame(component_rows)

component_demand = (
    component_demand
    .groupby(
        ["store_id", "date", "hour", "datetime_hour", "component_id"],
        as_index=False
    )["qty_component_needed"]
    .sum()
)

component_demand = component_demand.merge(
    components[["component_id", "component_name", "component_type", "storage_zone", "unit_type"]],
    on="component_id",
    how="left"
)

component_demand.to_csv(data_dir / "component_hourly_demand.csv", index=False)

print("=== exploded_product_demand preview ===")
print(exploded_product_demand.head().to_string(index=False))

print("\n=== component_hourly_demand preview ===")
print(component_demand.head().to_string(index=False))

print("\nExploded product rows:", len(exploded_product_demand))
print("Component demand rows:", len(component_demand))
print("Total component qty needed:", round(component_demand["qty_component_needed"].sum(), 2))

print("\nFiles created:")
print("- exploded_product_demand.csv")
print("- component_hourly_demand.csv")