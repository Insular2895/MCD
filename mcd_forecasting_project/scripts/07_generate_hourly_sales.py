from pathlib import Path
import pandas as pd
import numpy as np

np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data" / "processed"

stores = pd.read_csv(data_dir / "stores.csv")
calendar_hourly = pd.read_csv(data_dir / "calendar_hourly.csv")
finished_products = pd.read_csv(data_dir / "finished_products.csv")
local_events = pd.read_csv(data_dir / "local_events.csv")

# Keep only sellable products for sales generation
products = finished_products.copy()

# Base product mix weights
product_weights = {
    "Big Mac": 0.10,
    "Cheeseburger": 0.12,
    "McChicken": 0.08,
    "McNuggets 4": 0.05,
    "McNuggets 6": 0.07,
    "McNuggets 9": 0.05,
    "McNuggets 20": 0.02,
    "Frites M": 0.08,
    "Frites L": 0.03,
    "Coca M": 0.08,
    "Coca L": 0.03,
    "Sundae": 0.05,
    "McFlurry": 0.04,
    "Menu Big Mac": 0.12,
    "Menu McChicken": 0.08,
}

# Hour profile by store type
def hour_multiplier(hour, cluster_type):
    # general traffic shape
    if hour == 10:
        base = 0.35
    elif hour == 11:
        base = 0.80
    elif hour == 12:
        base = 1.60
    elif hour == 13:
        base = 1.80
    elif hour == 14:
        base = 1.30
    elif hour == 15:
        base = 0.95
    elif hour == 16:
        base = 0.75
    elif hour == 17:
        base = 0.85
    elif hour == 18:
        base = 1.00
    elif hour == 19:
        base = 1.10
    elif hour == 20:
        base = 0.95
    elif hour == 21:
        base = 0.75
    elif hour == 22:
        base = 0.55
    elif hour == 23:
        base = 0.25
    else:
        base = 0.10

    # city center stronger at lunch, weaker in evening
    if cluster_type == "city_center":
        if hour in [12, 13, 14]:
            base *= 1.18
        if hour in [18, 19, 20, 21, 22]:
            base *= 0.78

    # roadside store more balanced, stronger evenings
    if cluster_type == "roadside":
        if hour in [18, 19, 20]:
            base *= 1.10

    return base

# Day profile
def day_multiplier(day_of_week, is_weekend, is_school_holiday):
    mult = 1.0

    if day_of_week == "Wednesday":
        mult *= 1.18
    if day_of_week == "Friday":
        mult *= 1.10
    if day_of_week == "Saturday":
        mult *= 1.28
    if day_of_week == "Sunday":
        mult *= 1.22

    if is_school_holiday == 1:
        mult *= 1.08

    return mult

# Apply local events
def event_multiplier(store_id, current_date, hour):
    uplift = 1.0

    for _, event in local_events.iterrows():
        start_date = pd.to_datetime(event["start_date"]).date()
        end_date = pd.to_datetime(event["end_date"]).date()
        active_hours = [int(x) for x in str(event["active_hours"]).split(",")]

        if start_date <= current_date <= end_date and hour in active_hours:
            if event["target_store_id"] == store_id:
                uplift *= (1 + event["traffic_uplift_pct"])

            else:
                if event["traffic_downlift_pct_other_store"] != 0:
                    uplift *= (1 + event["traffic_downlift_pct_other_store"])

    return max(uplift, 0.05)

# Base demand by store
store_base_lambda = {
    "S001": 22,  # Dreux centre ville
    "S002": 25,  # Vernouillet / haut de ville
}

rows = []

for _, store in stores.iterrows():
    store_id = store["store_id"]
    cluster_type = store["cluster_type"]
    base_daily_index = store["base_daily_demand_index"]

    for _, cal in calendar_hourly.iterrows():
        current_date = pd.to_datetime(cal["date"]).date()
        hour = int(cal["hour"])
        day_of_week = cal["day_of_week"]
        is_weekend = int(cal["is_weekend"])
        is_school_holiday = int(cal["is_school_holiday"])

        hm = hour_multiplier(hour, cluster_type)
        dm = day_multiplier(day_of_week, is_weekend, is_school_holiday)
        em = event_multiplier(store_id, current_date, hour)

        total_hourly_lambda = store_base_lambda[store_id] * base_daily_index * hm * dm * em
        total_hourly_sales = np.random.poisson(total_hourly_lambda)

        for _, product in products.iterrows():
            product_name = product["product_name"]
            product_id = product["product_id"]
            base_price = float(product["base_price"])
            category = product["category"]
            is_menu = int(product["is_menu"])

            weight = product_weights.get(product_name, 0.01)

            # product-level contextual multipliers
            product_mult = 1.0

            # lunch boosts burgers and menus
            if hour in [12, 13, 14]:
                if category in ["burger", "menu"]:
                    product_mult *= 1.18

            # evening boosts nuggets / desserts slightly
            if hour in [18, 19, 20]:
                if category in ["nuggets", "dessert"]:
                    product_mult *= 1.12

            # weekend stronger for desserts
            if is_weekend == 1 and category == "dessert":
                product_mult *= 1.15

            expected_qty = total_hourly_sales * weight * product_mult
            qty_sold = np.random.poisson(expected_qty)

            revenue = round(qty_sold * base_price, 2)

            rows.append({
                "store_id": store_id,
                "date": cal["date"],
                "hour": hour,
                "datetime_hour": cal["datetime_hour"],
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "is_school_holiday": is_school_holiday,
                "is_fair_period": int(cal["is_fair_period"]),
                "is_fair_peak_weekend": int(cal["is_fair_peak_weekend"]),
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "is_menu": is_menu,
                "qty_sold": qty_sold,
                "unit_price": base_price,
                "revenue": revenue,
                "hour_multiplier": round(hm, 3),
                "day_multiplier": round(dm, 3),
                "event_multiplier": round(em, 3),
            })

fact_sales_hourly = pd.DataFrame(rows)

fact_sales_hourly.to_csv(data_dir / "fact_sales_hourly.csv", index=False)

print(fact_sales_hourly.head())
print("\nNombre de lignes :", len(fact_sales_hourly))
print("Volume total vendu :", int(fact_sales_hourly['qty_sold'].sum()))
print("CA total simulé :", round(fact_sales_hourly['revenue'].sum(), 2))
print("\nfact_sales_hourly.csv créé dans data/processed/")