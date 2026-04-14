from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
file_path = BASE_DIR / "data" / "processed" / "finished_products.csv"

df = pd.read_csv(file_path)

price_map = {
    "P001": 5.90,
    "P002": 3.20,
    "P003": 5.50,
    "P004": 4.20,
    "P005": 5.20,
    "P006": 6.50,
    "P007": 11.90,
    "P008": 3.00,
    "P009": 3.50,
    "P010": 3.00,
    "P011": 3.50,
    "P012": 3.00,
    "P013": 4.20,
    "P014": 9.90,
    "P015": 9.70,
}

df["base_price"] = df["product_id"].map(price_map)

if df["base_price"].isna().sum() > 0:
    missing_ids = df.loc[df["base_price"].isna(), "product_id"].tolist()
    raise ValueError(f"Prix manquants pour : {missing_ids}")

df.to_csv(file_path, index=False)

print(df[["product_id", "product_name", "base_price"]].to_string(index=False))
print("\nfinished_products.csv corrigé.")