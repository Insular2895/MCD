from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
output_dir = BASE_DIR / "data" / "processed"

stores = pd.DataFrame([
    {
        "store_id": "S001",
        "store_name": "McDonald's Dreux Centre Ville",
        "city": "Dreux",
        "region": "Eure-et-Loir",
        "cluster_type": "city_center",
        "near_lycee": 1,
        "near_main_road": 0,
        "fair_impact_zone": 1,
        "opening_hour": 10,
        "closing_hour": 23,
        "base_daily_demand_index": 1.00
    },
    {
        "store_id": "S002",
        "store_name": "McDonald's Vernouillet / Haut de Ville",
        "city": "Dreux",
        "region": "Eure-et-Loir",
        "cluster_type": "roadside",
        "near_lycee": 0,
        "near_main_road": 1,
        "fair_impact_zone": 0,
        "opening_hour": 10,
        "closing_hour": 23,
        "base_daily_demand_index": 1.15
    }
])

stores.to_csv(output_dir / "stores.csv", index=False)

print(stores)
print("\nstores.csv créé dans data/processed/")