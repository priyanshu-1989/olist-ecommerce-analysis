import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Mysql12345@localhost:3306/mydb")

files = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

for table_name, filename in files.items():
    df = pd.read_csv(filename)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Loaded {table_name}: {len(df)} rows")

print("All tables loaded successfully.")