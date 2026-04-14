from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

excel_file = BASE_DIR / "data" / "raw" / "MCD_Forecasting_excel.xlsx"
output_dir = BASE_DIR / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

finished_products = pd.read_excel(excel_file, sheet_name="finished_products")
components = pd.read_excel(excel_file, sheet_name="components")
bom_recipes = pd.read_excel(excel_file, sheet_name="bom_recipes")

print("finished_products:", finished_products.shape)
print("components:", components.shape)
print("bom_recipes:", bom_recipes.shape)

finished_products.to_csv(output_dir / "finished_products.csv", index=False)
components.to_csv(output_dir / "components.csv", index=False)
bom_recipes.to_csv(output_dir / "bom_recipes.csv", index=False)

print("Export terminé.")