import { useEffect, useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  BrainCircuit,
  CalendarDays,
  CircleDollarSign,
  Loader2,
  Search,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./PricePrediction.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function PricePrediction() {
  const [predictions, setPredictions] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPredictions();
  }, []);

  async function loadPredictions() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/price/all`);

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to load price predictions");
      }

      const data = await response.json();

      setPredictions(data.predictions || []);
    } catch (err) {
      console.error("Price prediction error:", err);

      setError(
        err.message ||
          "Unable to load AI price prediction data."
      );
    } finally {
      setLoading(false);
    }
  }

  const productColumn = useMemo(() => {
    const first = predictions[0];

    if (!first) {
      return null;
    }

    const possibleColumns = [
      "product_id",
      "product",
      "product_name",
      "sku",
      "id",
    ];

    return (
      possibleColumns.find(
        (column) =>
          Object.prototype.hasOwnProperty.call(first, column)
      ) || null
    );
  }, [predictions]);

  const priceColumn = useMemo(() => {
    const first = predictions[0];

    if (!first) {
      return null;
    }

    const possibleColumns = [
      "price",
      "current_price",
      "actual_price",
      "historical_price",
    ];

    return (
      possibleColumns.find(
        (column) =>
          Object.prototype.hasOwnProperty.call(first, column)
      ) || null
    );
  }, [predictions]);

  const predictedPriceColumn = useMemo(() => {
    const first = predictions[0];

    if (!first) {
      return null;
    }

    const possibleColumns = [
      "predicted_price",
      "predicted_price_30d",
      "forecast_price",
      "price_prediction",
    ];

    return (
      possibleColumns.find(
        (column) =>
          Object.prototype.hasOwnProperty.call(first, column)
      ) || null
    );
  }, [predictions]);

  const dateColumn = useMemo(() => {
    const first = predictions[0];

    if (!first) {
      return null;
    }

    const possibleColumns = [
      "date",
      "prediction_date",
      "forecast_date",
      "future_date",
      "ds",
    ];

    return (
      possibleColumns.find(
        (column) =>
          Object.prototype.hasOwnProperty.call(first, column)
      ) || null
    );
  }, [predictions]);

  const productList = useMemo(() => {
    if (!productColumn) {
      return [];
    }

    const uniqueProducts = [
      ...new Set(
        predictions
          .map((item) => item[productColumn])
          .filter(
            (value) =>
              value !== null &&
              value !== undefined &&
              String(value).trim() !== ""
          )
          .map((value) => String(value))
      ),
    ];

    return uniqueProducts.sort();
  }, [predictions, productColumn]);

  const filteredProducts = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return productList;
    }

    return productList.filter((product) =>
      product.toLowerCase().includes(query)
    );
  }, [productList, search]);

  useEffect(() => {
    if (
      productList.length > 0 &&
      !selectedProduct
    ) {
      setSelectedProduct(productList[0]);
    }
  }, [productList, selectedProduct]);

  const selectedPredictions = useMemo(() => {
    if (!productColumn || !selectedProduct) {
      return [];
    }

    return predictions
      .filter(
        (item) =>
          String(item[productColumn]) ===
          String(selectedProduct)
      )
      .sort((a, b) => {
        if (!dateColumn) {
          return 0;
        }

        return (
          new Date(a[dateColumn]) -
          new Date(b[dateColumn])
        );
      });
  }, [
    predictions,
    productColumn,
    selectedProduct,
    dateColumn,
  ]);

  const currentPrice = useMemo(() => {
    if (!priceColumn || selectedPredictions.length === 0) {
      return null;
    }

    const values = selectedPredictions
      .map((item) => Number(item[priceColumn]))
      .filter((value) => Number.isFinite(value));

    if (values.length === 0) {
      return null;
    }

    return values[values.length - 1];
  }, [selectedPredictions, priceColumn]);

  const firstPredictedPrice = useMemo(() => {
    if (
      !predictedPriceColumn ||
      selectedPredictions.length === 0
    ) {
      return null;
    }

    const values = selectedPredictions
      .map((item) =>
        Number(item[predictedPriceColumn])
      )
      .filter((value) => Number.isFinite(value));

    return values.length > 0 ? values[0] : null;
  }, [
    selectedPredictions,
    predictedPriceColumn,
  ]);

  const finalPredictedPrice = useMemo(() => {
    if (
      !predictedPriceColumn ||
      selectedPredictions.length === 0
    ) {
      return null;
    }

    const values = selectedPredictions
      .map((item) =>
        Number(item[predictedPriceColumn])
      )
      .filter((value) => Number.isFinite(value));

    return values.length > 0
      ? values[values.length - 1]
      : null;
  }, [
    selectedPredictions,
    predictedPriceColumn,
  ]);

  const expectedChange = useMemo(() => {
    if (
      currentPrice === null ||
      finalPredictedPrice === null ||
      currentPrice === 0
    ) {
      return null;
    }

    return (
      ((finalPredictedPrice - currentPrice) /
        currentPrice) *
      100
    );
  }, [currentPrice, finalPredictedPrice]);

  const chartData = useMemo(() => {
    return selectedPredictions.map((item, index) => {
      const rawDate = dateColumn
        ? item[dateColumn]
        : null;

      const predicted = predictedPriceColumn
        ? Number(item[predictedPriceColumn])
        : null;

      const actual = priceColumn
        ? Number(item[priceColumn])
        : null;

      return {
        day: index + 1,
        date: rawDate
          ? String(rawDate).slice(0, 10)
          : `Day ${index + 1}`,
        predictedPrice: Number.isFinite(predicted)
          ? Number(predicted.toFixed(2))
          : null,
        currentPrice: Number.isFinite(actual)
          ? Number(actual.toFixed(2))
          : null,
      };
    });
  }, [
    selectedPredictions,
    dateColumn,
    predictedPriceColumn,
    priceColumn,
  ]);

  const priceInsight = useMemo(() => {
    if (expectedChange === null) {
      return "The AI model has generated a future price forecast for this product.";
    }

    if (expectedChange > 5) {
      return `The model expects the price to increase by approximately ${expectedChange.toFixed(
        1
      )}% over the forecast period. This may indicate stronger demand or seasonal pricing pressure.`;
    }

    if (expectedChange < -5) {
      return `The model expects the price to decrease by approximately ${Math.abs(
        expectedChange
      ).toFixed(
        1
      )}%. This could indicate weaker demand, increased supply, or seasonal price pressure.`;
    }

    return `The model expects relatively stable pricing, with an estimated change of ${expectedChange.toFixed(
      1
    )}% over the forecast period.`;
  }, [expectedChange]);

  function formatPrice(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "N/A";
    }

    return `₹${number.toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;
  }

  if (loading) {
    return (
      <div className="price-page-loading">
        <Loader2
          size={32}
          className="price-loading-icon"
        />

        <p>
          Loading AI price predictions...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="price-error-card">
        <div className="price-error-icon">
          <TrendingDown size={26} />
        </div>

        <div>
          <h3>
            Price prediction unavailable
          </h3>

          <p>{error}</p>

          <button
            className="price-retry-button"
            onClick={loadPredictions}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="price-prediction-page">
      <div className="price-page-header">
        <div>
          <div className="price-title-row">
            <CircleDollarSign size={30} />

            <h1>
              AI Price Prediction
            </h1>
          </div>

          <p>
            Machine-learning powered product price
            forecasting based on historical pricing,
            demand and seasonality.
          </p>
        </div>

        <div className="price-model-badge">
          <BrainCircuit size={17} />
          Random Forest AI
        </div>
      </div>

      <div className="price-selection-card">
        <div className="price-search-box">
          <Search size={18} />

          <input
            type="text"
            placeholder="Search product..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>

        <select
          value={selectedProduct}
          onChange={(event) =>
            setSelectedProduct(event.target.value)
          }
        >
          {filteredProducts.map((product) => (
            <option
              key={product}
              value={product}
            >
              {product}
            </option>
          ))}
        </select>
      </div>

      {selectedProduct && (
        <>
          <div className="price-product-heading">
            <div>
              <span>
                PRODUCT
              </span>

              <h2>
                {selectedProduct}
              </h2>
            </div>

            <div className="forecast-days">
              <CalendarDays size={17} />
              {selectedPredictions.length}-Day Forecast
            </div>
          </div>

          <div className="price-kpi-grid">
            <div className="price-kpi-card">
              <div className="price-kpi-icon">
                <CircleDollarSign size={22} />
              </div>

              <div>
                <span>
                  CURRENT PRICE
                </span>

                <strong>
                  {formatPrice(currentPrice)}
                </strong>
              </div>
            </div>

            <div className="price-kpi-card">
              <div className="price-kpi-icon">
                <TrendingUp size={22} />
              </div>

              <div>
                <span>
                  FIRST PREDICTED PRICE
                </span>

                <strong>
                  {formatPrice(firstPredictedPrice)}
                </strong>
              </div>
            </div>

            <div className="price-kpi-card">
              <div className="price-kpi-icon">
                <BrainCircuit size={22} />
              </div>

              <div>
                <span>
                  FINAL PREDICTED PRICE
                </span>

                <strong>
                  {formatPrice(finalPredictedPrice)}
                </strong>
              </div>
            </div>

            <div
              className={`price-kpi-card ${
                expectedChange !== null &&
                expectedChange >= 0
                  ? "price-positive"
                  : "price-negative"
              }`}
            >
              <div className="price-kpi-icon">
                {expectedChange !== null &&
                expectedChange >= 0 ? (
                  <ArrowUp size={22} />
                ) : (
                  <ArrowDown size={22} />
                )}
              </div>

              <div>
                <span>
                  EXPECTED CHANGE
                </span>

                <strong>
                  {expectedChange !== null
                    ? `${
                        expectedChange >= 0
                          ? "+"
                          : ""
                      }${expectedChange.toFixed(
                        2
                      )}%`
                    : "N/A"}
                </strong>
              </div>
            </div>
          </div>

          <div className="price-main-grid">
            <div className="price-chart-card">
              <div className="price-card-header">
                <div>
                  <h3>
                    30-Day Price Forecast
                  </h3>

                  <p>
                    AI predicted price trajectory
                  </p>
                </div>

                <TrendingUp size={21} />
              </div>

              <div className="price-chart">
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient
                        id="priceGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="5%"
                          stopOpacity={0.3}
                        />

                        <stop
                          offset="95%"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="day"
                      tickFormatter={(value) =>
                        `Day ${value}`
                      }
                    />

                    <YAxis
                      tickFormatter={(value) =>
                        `₹${value}`
                      }
                    />

                    <Tooltip
                      formatter={(value) =>
                        formatPrice(value)
                      }
                      labelFormatter={(value) =>
                        `Forecast Day ${value}`
                      }
                    />

                    <Area
                      type="monotone"
                      dataKey="predictedPrice"
                      name="AI Predicted Price"
                      strokeWidth={3}
                      fill="url(#priceGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="price-insight-card">
              <div className="price-insight-header">
                <div className="price-ai-icon">
                  <BrainCircuit size={24} />
                </div>

                <div>
                  <span>
                    AI INSIGHT
                  </span>

                  <h3>
                    Pricing Intelligence
                  </h3>
                </div>
              </div>

              <p className="price-insight-text">
                {priceInsight}
              </p>

              <div className="price-insight-divider" />

              <div className="price-insight-row">
                <span>
                  Forecast horizon
                </span>

                <strong>
                  {selectedPredictions.length} days
                </strong>
              </div>

              <div className="price-insight-row">
                <span>
                  Starting forecast
                </span>

                <strong>
                  {formatPrice(firstPredictedPrice)}
                </strong>
              </div>

              <div className="price-insight-row">
                <span>
                  Ending forecast
                </span>

                <strong>
                  {formatPrice(finalPredictedPrice)}
                </strong>
              </div>

              <div
                className={`price-trend-box ${
                  expectedChange !== null &&
                  expectedChange >= 0
                    ? "trend-up"
                    : "trend-down"
                }`}
              >
                {expectedChange !== null &&
                expectedChange >= 0 ? (
                  <TrendingUp size={20} />
                ) : (
                  <TrendingDown size={20} />
                )}

                <span>
                  {expectedChange !== null &&
                  expectedChange >= 0
                    ? "Expected upward price trend"
                    : "Expected downward price trend"}
                </span>
              </div>
            </div>
          </div>
        </>
      )}

      {productList.length === 0 && (
        <div className="price-empty-state">
          <CircleDollarSign size={40} />

          <h3>
            No price predictions found
          </h3>

          <p>
            Run the AI price prediction engine
            first to generate forecast data.
          </p>
        </div>
      )}
    </div>
  );
}

export default PricePrediction;