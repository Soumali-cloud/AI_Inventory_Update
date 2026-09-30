# AI Inventory Intelligence

An AI-powered inventory intelligence platform that uses machine learning, demand forecasting, price prediction, and AI-driven decision analytics to help businesses optimize inventory, reduce stockouts, and improve replenishment decisions.

---

## Overview

AI Inventory Intelligence analyzes historical sales, inventory, pricing, promotions, seasonality, and product information to generate actionable inventory insights.

The system combines:

- Machine Learning
- Demand Forecasting
- Price Prediction
- Inventory Risk Detection
- AI Decision Intelligence
- Interactive Analytics
- FastAPI
- React
- Recharts
- Power BI-ready datasets

The platform is designed to answer practical business questions such as:

- Which products are likely to have high demand?
- Which products may run out of stock soon?
- Which products are overstocked?
- How much inventory should be maintained?
- What could the future product price look like?
- When should inventory be replenished?
- Should inventory be increased, reduced, or maintained?
- How accurate are the machine-learning models?

---

# Key Features

## 1. Demand Prediction

Uses historical sales and inventory information to predict future product demand.

The demand pipeline considers factors such as:

- Historical units sold
- Previous demand
- Rolling demand averages
- Seasonality
- Day of week
- Month
- Promotions
- Holidays
- Product information

The system generates demand forecasts for individual products.

---

## 2. Inventory Intelligence

The platform analyzes current inventory against predicted demand.

It calculates metrics including:

- Current inventory
- Average daily demand
- Days of inventory
- Demand growth
- Inventory health
- Stockout risk
- Demand category

---

## 3. Stockout Risk Detection

Products are classified according to estimated inventory coverage.

Example risk levels include:

| Risk Level | Inventory Coverage |
|---|---|
| Critical | ≤ 3 days |
| High | ≤ 7 days |
| Medium | ≤ 14 days |
| Low | > 14 days |

This helps identify products that require immediate attention.

---

## 4. AI Replenishment Recommendations

The system converts predictions into business actions.

Possible AI decisions include:

- URGENTLY REPLENISH
- REPLENISH SOON
- INCREASE STOCK
- REDUCE INVENTORY
- CONSIDER PRICE INCREASE
- CONSIDER PROMOTION
- MAINTAIN STOCK
- MONITOR

Each decision is accompanied by:

- Confidence score
- Priority
- Explanation
- Inventory information
- Demand information
- Risk information

---

## 5. AI Decision Center

The AI Decision Center provides a centralized view of machine-learning recommendations.

It allows users to:

- View all product decisions
- Filter decisions
- Analyze decision distribution
- Review confidence scores
- Understand AI explanations
- Identify high-priority inventory actions

---

## 6. Price Prediction

The price prediction pipeline estimates future product prices using historical pricing and demand-related features.

The model incorporates:

- Historical prices
- Demand
- Price changes
- Price rolling averages
- Demand rolling averages
- Seasonal features
- Previous prices

The system generates future price predictions for products.

---

## 7. Product Intelligence

The Product Intelligence view provides a detailed product-level analysis.

For a selected product, users can view:

- Current inventory
- 30-day demand
- Days of inventory
- Demand surge
- Stockout risk
- AI decision
- AI confidence
- AI explanation
- Demand forecast
- Replenishment recommendation

---

## 8. Analytics & Reports

The analytics dashboard provides interactive visualizations for inventory and demand intelligence.

It includes:

- Demand by product
- Inventory vs predicted demand
- Stockout-risk distribution
- AI decision distribution
- Top-demand products
- Product/category filtering
- Search functionality

---

## 9. Model Performance

The platform evaluates the machine-learning models and exposes their performance through the application.

Metrics include:

- MAE
- RMSE
- R² Score
- MAE Percentage
- Number of evaluation samples
- Number of features
- Target variable

The current demand model evaluation demonstrates strong predictive performance with an R² score of approximately 0.90.

---

# Machine Learning

## Demand Prediction Model

The demand prediction pipeline uses a Random Forest regression model.

Important features include:

- Lag features
- Rolling averages
- Rolling standard deviation
- Sales velocity
- Demand growth
- Price
- Discount
- Promotion
- Holiday
- Calendar features

Example lag features:

```text
lag_1
lag_7
lag_14
lag_30