import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/processed/inventory_features.csv"
OUTPUT_DIR = "reports/eda"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("AI INVENTORY INTELLIGENCE")
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)

df = pd.read_csv(INPUT_PATH)

df["date"] = pd.to_datetime(df["date"])

print(f"\nDataset shape: {df.shape}")

print(f"Products: {df['product_id'].nunique()}")

print(f"Categories: {df['category'].nunique()}")


# ============================================================
# 1. DAILY DEMAND TREND
# ============================================================

print("\nCreating daily demand trend...")

daily_demand = (
    df.groupby("date")["units_sold"]
    .sum()
    .reset_index()
)

plt.figure(figsize=(14, 6))

plt.plot(
    daily_demand["date"],
    daily_demand["units_sold"],
)

plt.title("Daily Total Product Demand")

plt.xlabel("Date")

plt.ylabel("Units Sold")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/daily_demand_trend.png",
    dpi=150,
)

plt.close()


# ============================================================
# 2. MONTHLY DEMAND
# ============================================================

print("Creating monthly demand chart...")

monthly_demand = (
    df.groupby(["year", "month"])["units_sold"]
    .sum()
    .reset_index()
)

monthly_demand["period"] = (
    monthly_demand["year"].astype(str)
    + "-"
    + monthly_demand["month"].astype(str).str.zfill(2)
)

plt.figure(figsize=(14, 6))

plt.plot(
    monthly_demand["period"],
    monthly_demand["units_sold"],
    marker="o",
)

plt.title("Monthly Demand Trend")

plt.xlabel("Month")

plt.ylabel("Units Sold")

plt.xticks(rotation=45)

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/monthly_demand.png",
    dpi=150,
)

plt.close()


# ============================================================
# 3. CATEGORY DEMAND
# ============================================================

print("Creating category demand chart...")

category_demand = (
    df.groupby("category")["units_sold"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10, 6))

category_demand.plot(
    kind="bar",
)

plt.title("Total Demand by Category")

plt.xlabel("Category")

plt.ylabel("Units Sold")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/category_demand.png",
    dpi=150,
)

plt.close()


# ============================================================
# 4. TOP 10 PRODUCTS BY SALES
# ============================================================

print("Creating top products chart...")

top_products = (
    df.groupby("product_name")["units_sold"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
)

plt.figure(figsize=(10, 7))

top_products.plot(
    kind="barh",
)

plt.title("Top 10 Products by Total Units Sold")

plt.xlabel("Units Sold")

plt.ylabel("Product")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/top_10_products.png",
    dpi=150,
)

plt.close()


# ============================================================
# 5. INVENTORY LEVEL TREND
# ============================================================

print("Creating inventory trend...")

inventory = (
    df.groupby("date")["inventory_level"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(14, 6))

plt.plot(
    inventory["date"],
    inventory["inventory_level"],
)

plt.title("Average Inventory Level Over Time")

plt.xlabel("Date")

plt.ylabel("Average Inventory")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/inventory_trend.png",
    dpi=150,
)

plt.close()


# ============================================================
# 6. PRICE VS DEMAND
# ============================================================

print("Creating price vs demand chart...")

sample = df.sample(
    min(5000, len(df)),
    random_state=42,
)

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=sample,
    x="price",
    y="units_sold",
    hue="category",
    alpha=0.5,
)

plt.title("Price vs Units Sold")

plt.xlabel("Price")

plt.ylabel("Units Sold")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/price_vs_demand.png",
    dpi=150,
)

plt.close()


# ============================================================
# 7. DISCOUNT VS DEMAND
# ============================================================

print("Creating discount vs demand chart...")

discount_demand = (
    df.groupby("discount")["units_sold"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(10, 6))

plt.plot(
    discount_demand["discount"] * 100,
    discount_demand["units_sold"],
    marker="o",
)

plt.title("Discount vs Average Demand")

plt.xlabel("Discount (%)")

plt.ylabel("Average Units Sold")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/discount_vs_demand.png",
    dpi=150,
)

plt.close()


# ============================================================
# 8. WEEKDAY DEMAND
# ============================================================

print("Creating weekday demand chart...")

weekday_demand = (
    df.groupby("day_of_week")["units_sold"]
    .mean()
)

weekday_names = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

weekday_demand.index = [
    weekday_names[i]
    for i in weekday_demand.index
]

plt.figure(figsize=(10, 6))

weekday_demand.plot(
    kind="bar",
)

plt.title("Average Demand by Day of Week")

plt.xlabel("Day")

plt.ylabel("Average Units Sold")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/weekday_demand.png",
    dpi=150,
)

plt.close()


# ============================================================
# 9. CORRELATION HEATMAP
# ============================================================

print("Creating correlation heatmap...")

correlation_columns = [
    "price",
    "discount",
    "units_sold",
    "inventory_level",
    "rating",
    "reviews",
    "promotion",
    "holiday",
    "day_of_week",
    "month",
    "lag_7",
    "lag_30",
    "rolling_mean_7",
    "rolling_mean_30",
    "sales_velocity",
    "demand_growth",
    "price_change",
    "revenue",
    "days_of_inventory",
]

correlation_matrix = df[
    correlation_columns
].corr()

plt.figure(figsize=(16, 12))

sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
)

plt.title("Feature Correlation Matrix")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/correlation_heatmap.png",
    dpi=150,
)

plt.close()


# ============================================================
# 10. DEMAND DISTRIBUTION
# ============================================================

print("Creating demand distribution...")

plt.figure(figsize=(10, 6))

sns.histplot(
    df["units_sold"],
    bins=40,
    kde=True,
)

plt.title("Distribution of Daily Product Demand")

plt.xlabel("Units Sold")

plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/demand_distribution.png",
    dpi=150,
)

plt.close()


# ============================================================
# 11. DEMAND CATEGORY DISTRIBUTION
# ============================================================

print("Creating demand category chart...")

demand_categories = (
    df["demand_category"]
    .value_counts()
    .reindex(
        [
            "Low",
            "Medium",
            "High",
            "Very High",
        ]
    )
)

plt.figure(figsize=(9, 6))

demand_categories.plot(
    kind="bar",
)

plt.title("Demand Category Distribution")

plt.xlabel("Demand Category")

plt.ylabel("Number of Records")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/demand_categories.png",
    dpi=150,
)

plt.close()


# ============================================================
# 12. PRINT BUSINESS INSIGHTS
# ============================================================

print("\n" + "=" * 60)
print("KEY DATASET INSIGHTS")
print("=" * 60)

print(
    "\nTotal units sold:",
    f"{df['units_sold'].sum():,.0f}",
)

print(
    "Total revenue:",
    f"₹{df['revenue'].sum():,.2f}",
)

print(
    "Average daily demand:",
    f"{df['units_sold'].mean():.2f}",
)

print(
    "Average product price:",
    f"₹{df['price'].mean():.2f}",
)

print(
    "Average inventory:",
    f"{df['inventory_level'].mean():.2f}",
)


# Top product

top_product = (
    df.groupby("product_name")["units_sold"]
    .sum()
    .idxmax()
)

top_product_sales = (
    df.groupby("product_name")["units_sold"]
    .sum()
    .max()
)

print(
    f"\nTop product: {top_product}"
)

print(
    f"Top product units sold: "
    f"{top_product_sales:,}"
)


# Top category

top_category = (
    df.groupby("category")["units_sold"]
    .sum()
    .idxmax()
)

print(
    f"\nTop category: {top_category}"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("EDA COMPLETE")
print("=" * 60)

print(
    f"\nCharts saved to: {OUTPUT_DIR}"
)