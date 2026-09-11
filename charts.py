import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Mysql12345@localhost:3306/mydb")
sns.set_style("whitegrid")

# --- Chart 1: Monthly revenue trend ---
revenue = pd.read_sql("""
    SELECT DATE_FORMAT(o.order_purchase_timestamp, '%%Y-%%m') AS month,
           SUM(oi.price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY month ORDER BY month
""", engine)

plt.figure(figsize=(10, 5))
plt.plot(revenue["month"], revenue["revenue"], marker="o", color="#2E86AB")
plt.xticks(rotation=45)
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (R$)")
plt.tight_layout()
plt.savefig("chart1_monthly_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart1_monthly_revenue.png")

# --- Chart 2: Top 10 categories by revenue ---
categories = pd.read_sql("""
    SELECT t.product_category_name_english AS category,
           SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN product_category_translation t ON p.product_category_name = t.product_category_name
    GROUP BY category ORDER BY revenue DESC LIMIT 10
""", engine)

plt.figure(figsize=(10, 6))
plt.barh(categories["category"], categories["revenue"], color="#A23B72")
plt.gca().invert_yaxis()
plt.title("Top 10 Product Categories by Revenue")
plt.xlabel("Revenue (R$)")
plt.tight_layout()
plt.savefig("chart2_top_categories.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart2_top_categories.png")

# --- Chart 3: RFM segment breakdown ---
rfm = pd.read_csv("rfm_segments.csv")
seg_counts = rfm["Segment"].value_counts()

plt.figure(figsize=(8, 5))
plt.bar(seg_counts.index, seg_counts.values, color="#F18F01")
plt.title("Customer Segments (RFM Analysis)")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig("chart3_rfm_segments.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart3_rfm_segments.png")

# --- Chart 4: Delivery delay vs review score ---
orders = pd.read_sql("SELECT order_id, order_delivered_customer_date, order_estimated_delivery_date FROM orders", engine)
reviews = pd.read_sql("SELECT order_id, review_score FROM order_reviews", engine)

orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])
orders["delivery_delay_days"] = (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]).dt.days

merged = orders.merge(reviews, on="order_id").dropna(subset=["delivery_delay_days", "review_score"])
merged["on_time"] = merged["delivery_delay_days"].apply(lambda x: "On Time" if x <= 0 else "Late")

plt.figure(figsize=(7, 5))
sns.boxplot(data=merged, x="on_time", y="review_score", palette=["#2E86AB", "#C73E1D"])
plt.title("Review Score: On-Time vs Late Deliveries")
plt.xlabel("")
plt.ylabel("Review Score")
plt.tight_layout()
plt.savefig("chart4_delay_vs_review.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart4_delay_vs_review.png")

print("\nAll 4 charts generated successfully.")