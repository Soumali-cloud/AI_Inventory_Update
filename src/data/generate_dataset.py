import os
import random

import numpy as np
import pandas as pd


# ============================================================
# 1. REPRODUCIBILITY
# ============================================================

np.random.seed(42)
random.seed(42)


# ============================================================
# 2. CONFIGURATION
# ============================================================

START_DATE = "2025-01-01"
END_DATE = "2026-12-31"

OUTPUT_PATH = "data/raw/inventory_sales.csv"


# ============================================================
# 3. PRODUCT CATALOG
# ============================================================

products = [
    ("P0001", "Wireless Mouse", "Electronics", 799, 45),
    ("P0002", "Mechanical Keyboard", "Electronics", 2499, 25),
    ("P0003", "USB-C Cable", "Electronics", 499, 80),
    ("P0004", "Bluetooth Speaker", "Electronics", 1999, 30),
    ("P0005", "Power Bank", "Electronics", 1499, 35),

    ("P0006", "Running Shoes", "Fashion", 2999, 35),
    ("P0007", "Cotton T-Shirt", "Fashion", 699, 70),
    ("P0008", "Jeans", "Fashion", 1799, 45),
    ("P0009", "Backpack", "Fashion", 1299, 40),
    ("P0010", "Wrist Watch", "Fashion", 2499, 25),

    ("P0011", "Coffee Maker", "Home & Kitchen", 3499, 20),
    ("P0012", "Air Fryer", "Home & Kitchen", 5999, 25),
    ("P0013", "Electric Kettle", "Home & Kitchen", 1599, 40),
    ("P0014", "Mixer Grinder", "Home & Kitchen", 3999, 25),
    ("P0015", "Non-Stick Pan", "Home & Kitchen", 1199, 50),

    ("P0016", "Notebook", "Stationery", 199, 100),
    ("P0017", "Pen Set", "Stationery", 149, 120),
    ("P0018", "Office Organizer", "Stationery", 499, 60),
    ("P0019", "Calculator", "Stationery", 599, 45),
    ("P0020", "Desk Lamp", "Stationery", 899, 40),

    ("P0021", "Face Wash", "Beauty", 399, 60),
    ("P0022", "Shampoo", "Beauty", 499, 70),
    ("P0023", "Body Lotion", "Beauty", 449, 55),
    ("P0024", "Perfume", "Beauty", 1499, 35),
    ("P0025", "Hair Dryer", "Beauty", 1999, 30),

    ("P0026", "Yoga Mat", "Sports", 999, 40),
    ("P0027", "Dumbbells", "Sports", 2499, 30),
    ("P0028", "Cricket Bat", "Sports", 2999, 25),
    ("P0029", "Football", "Sports", 899, 45),
    ("P0030", "Water Bottle", "Sports", 699, 70),
]


# ============================================================
# 4. CATEGORY DEMAND MULTIPLIERS
# ============================================================

demand_multiplier = {
    "Electronics": 1.20,
    "Fashion": 1.00,
    "Home & Kitchen": 0.85,
    "Stationery": 1.15,
    "Beauty": 0.95,
    "Sports": 0.90,
}


# ============================================================
# 5. DATE RANGE
# ============================================================

dates = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D",
)


# ============================================================
# 6. GENERATE RECORDS
# ============================================================

records = []


for product_id, product_name, category, base_price, base_demand in products:

    inventory = random.randint(300, 1000)

    for date in dates:

        # ----------------------------------------------------
        # Calendar features
        # ----------------------------------------------------

        day_of_week = date.dayofweek
        month = date.month
        year = date.year

        is_weekend = day_of_week >= 5

        # ----------------------------------------------------
        # Seasonal demand
        # ----------------------------------------------------

        seasonal_factor = 1.0

        # Summer
        if month in [4, 5, 6]:
            seasonal_factor *= 1.10

        # Festive season
        if month in [10, 11]:
            seasonal_factor *= 1.30

        # December
        if month == 12:
            seasonal_factor *= 1.20

        # Weekend demand
        if is_weekend:
            seasonal_factor *= 1.10

        # ----------------------------------------------------
        # Holiday effect
        # ----------------------------------------------------

        holiday = 0

        if (
            (month == 1 and date.day == 26)
            or (month == 8 and date.day == 15)
            or (month == 10 and date.day in [20, 21])
            or (month == 12 and date.day == 25)
        ):
            holiday = 1
            seasonal_factor *= 1.35

        # ----------------------------------------------------
        # Promotion
        # ----------------------------------------------------

        promotion = 0
        discount = 0.0

        if random.random() < 0.12:

            promotion = 1

            discount = random.choice(
                [0.05, 0.10, 0.15, 0.20, 0.25]
            )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        price_variation = np.random.normal(0, 0.03)

        price = base_price * (1 + price_variation)

        price *= (1 - discount)

        price = max(
            price,
            base_price * 0.60,
        )

        # ----------------------------------------------------
        # Price effect on demand
        # ----------------------------------------------------

        price_effect = 1.0

        if discount > 0:
            price_effect += discount * 2.5

        # ----------------------------------------------------
        # Category effect
        # ----------------------------------------------------

        category_factor = demand_multiplier[category]

        # ----------------------------------------------------
        # Random demand variation
        # ----------------------------------------------------

        random_factor = np.random.normal(
            1.0,
            0.15,
        )

        # ----------------------------------------------------
        # Expected demand
        # ----------------------------------------------------

        expected_demand = (
            base_demand
            * category_factor
            * seasonal_factor
            * price_effect
            * random_factor
        )

        units_sold = max(
            0,
            int(round(expected_demand)),
        )

        # ----------------------------------------------------
        # Inventory constraint
        # ----------------------------------------------------

        units_sold = min(
            units_sold,
            inventory,
        )

        # ----------------------------------------------------
        # Update inventory
        # ----------------------------------------------------

        inventory -= units_sold

        # ----------------------------------------------------
        # Replenishment
        # ----------------------------------------------------

        if inventory < 100:

            replenishment = random.randint(
                400,
                900,
            )

            inventory += replenishment

        # ----------------------------------------------------
        # Product rating
        # ----------------------------------------------------

        rating = round(
            np.clip(
                np.random.normal(
                    4.2,
                    0.35,
                ),
                2.5,
                5.0,
            ),
            1,
        )

        # ----------------------------------------------------
        # Product reviews
        # ----------------------------------------------------

        reviews = max(
            10,
            int(
                np.random.normal(
                    5000,
                    1500,
                )
            ),
        )

        # ----------------------------------------------------
        # Store record
        # ----------------------------------------------------

        records.append(
            {
                "date": date,
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price": round(price, 2),
                "discount": discount,
                "units_sold": units_sold,
                "inventory_level": inventory,
                "rating": rating,
                "reviews": reviews,
                "promotion": promotion,
                "holiday": holiday,
                "day_of_week": day_of_week,
                "month": month,
                "year": year,
            }
        )


# ============================================================
# 7. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# 8. SORT DATA
# ============================================================

df = df.sort_values(
    ["product_id", "date"]
).reset_index(drop=True)


# ============================================================
# 9. CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True,
)


# ============================================================
# 10. SAVE DATASET
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# 11. DISPLAY RESULTS
# ============================================================

print("=" * 60)
print("AI INVENTORY INTELLIGENCE")
print("DATASET GENERATED SUCCESSFULLY")
print("=" * 60)

print(f"Rows       : {len(df):,}")
print(f"Columns    : {len(df.columns)}")
print(f"Products   : {df['product_id'].nunique()}")
print(f"Categories : {df['category'].nunique()}")

print(
    f"Date range : "
    f"{df['date'].min().date()} "
    f"to "
    f"{df['date'].max().date()}"
)

print("\nColumns:")
print(list(df.columns))

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset saved to:")
print(OUTPUT_PATH)