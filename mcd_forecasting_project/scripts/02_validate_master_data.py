from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
data_dir = BASE_DIR / "data" / "processed"

finished_products = pd.read_csv(data_dir / "finished_products.csv")
components = pd.read_csv(data_dir / "components.csv")
bom_recipes = pd.read_csv(data_dir / "bom_recipes.csv")

print("=== SHAPES ===")
print("finished_products:", finished_products.shape)
print("components:", components.shape)
print("bom_recipes:", bom_recipes.shape)

print("\n=== MISSING VALUES ===")
print("\nfinished_products")
print(finished_products.isna().sum())

print("\ncomponents")
print(components.isna().sum())

print("\nbom_recipes")
print(bom_recipes.isna().sum())

print("\n=== DUPLICATE IDS ===")
print("duplicate product_id:", finished_products["product_id"].duplicated().sum())
print("duplicate component_id:", components["component_id"].duplicated().sum())

print("\n=== BOM REFERENTIAL CHECK ===")
valid_product_ids = set(finished_products["product_id"])
valid_component_ids = set(components["component_id"])

invalid_bom_products = bom_recipes.loc[~bom_recipes["product_id"].isin(valid_product_ids)]
invalid_bom_components = bom_recipes.loc[~bom_recipes["component_id"].isin(valid_component_ids)]

print("invalid bom product refs:", len(invalid_bom_products))
print("invalid bom component refs:", len(invalid_bom_components))

if len(invalid_bom_products) > 0:
    print("\nInvalid BOM product refs:")
    print(invalid_bom_products)

if len(invalid_bom_components) > 0:
    print("\nInvalid BOM component refs:")
    print(invalid_bom_components)

print("\n=== BOM DUPLICATES ===")
dup_bom = bom_recipes.duplicated(subset=["product_id", "component_id"]).sum()
print("duplicate product_id + component_id pairs:", dup_bom)

print("\nValidation terminée.")