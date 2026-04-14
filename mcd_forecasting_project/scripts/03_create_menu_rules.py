from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
output_dir = BASE_DIR / "data" / "processed"

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

menu_rules.to_csv(output_dir / "menu_rules.csv", index=False)

print(menu_rules)
print("\nmenu_rules.csv créé dans data/processed/")