import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Mysql12345@localhost:3306/mydb")

orders = pd.read_sql("SELECT * FROM orders", engine)
payments = pd.read_sql("SELECT * FROM order_payments", engine)
customers = pd.read_sql("SELECT * FROM customers", engine)
reviews = pd.read_sql("SELECT * FROM order_reviews", engine)

print("Data loaded:", orders.shape, payments.shape, customers.shape, reviews.shape)

# Merge orders with customers to get customer_unique_id, and with payments for spend
df = orders.merge(customers, on="customer_id")
df = df.merge(payments, on="order_id")

# Convert date column
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

# Reference date = one day after the latest order in the dataset
snapshot_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

# RFM calculation per unique customer
rfm = df.groupby("customer_unique_id").agg(
    Recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
    Frequency=("order_id", "nunique"),
    Monetary=("payment_value", "sum")
).reset_index()

print("\nRFM table sample:")
print(rfm.head())

# Score each dimension 1-4 using quantiles (4 = best)
rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)

rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

# Simple segment labels
def segment(row):
    if row["RFM_score"] >= 10:
        return "Champions"
    elif row["RFM_score"] >= 7:
        return "Loyal / Potential"
    elif row["RFM_score"] >= 5:
        return "At Risk"
    else:
        return "Lost / Low Value"

rfm["Segment"] = rfm.apply(segment, axis=1)

print("\nSegment counts:")
print(rfm["Segment"].value_counts())

rfm.to_csv("rfm_segments.csv", index=False)
print("\nSaved rfm_segments.csv")
# --- Delivery delay vs review score ---
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])

orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
).dt.days

delay_reviews = orders.merge(reviews, on="order_id")
delay_reviews = delay_reviews.dropna(subset=["delivery_delay_days", "review_score"])

correlation = delay_reviews["delivery_delay_days"].corr(delay_reviews["review_score"])
print(f"\nCorrelation between delivery delay and review score: {correlation:.3f}")

# Average review score for on-time vs late orders
delay_reviews["on_time"] = delay_reviews["delivery_delay_days"] <= 0
avg_by_ontime = delay_reviews.groupby("on_time")["review_score"].mean()
print("\nAverage review score:")
print(avg_by_ontime)