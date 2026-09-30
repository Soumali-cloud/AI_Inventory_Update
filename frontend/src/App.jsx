import { useEffect, useMemo, useState } from "react";
import AIDecisionCenter from "./components/AIDecisionCenter";
import PricePrediction from "./components/PricePrediction";
import ModelPerformance from "./components/ModelPerformance";
import {
  AlertTriangle,
  BarChart3,
  Boxes,
  BrainCircuit,
  ChevronDown,
  CircleDollarSign,
  FileBarChart,
  Package,
  RefreshCw,
  Search,
  Target,
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

import InventorySimulator from "./components/InventorySimulator";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import AIReport from "./components/AIReport";
import ProductIntelligence from "./components/ProductIntelligence";

import "./App.css";


const API_BASE_URL = "http://127.0.0.1:8000";


function App() {

  // ==========================================================
  // STATE
  // ==========================================================

  const [summary, setSummary] = useState(null);

  const [products, setProducts] = useState([]);

  const [alerts, setAlerts] = useState([]);

  const [health, setHealth] = useState(null);

  const [selectedProduct, setSelectedProduct] =
    useState(null);

  const [productDetails, setProductDetails] =
    useState(null);

  const [forecast, setForecast] = useState([]);

  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  const [simulatorProduct, setSimulatorProduct] =
    useState(null);

  const [activePage, setActivePage] =
    useState("dashboard");


  // ==========================================================
  // LOAD DASHBOARD DATA
  // ==========================================================

  async function loadDashboard() {

    try {

      setLoading(true);
      setError(null);

      const [
        summaryResponse,
        productsResponse,
        alertsResponse,
        healthResponse,
      ] = await Promise.all([

        fetch(
          `${API_BASE_URL}/dashboard/summary`
        ),

        fetch(
          `${API_BASE_URL}/dashboard/products`
        ),

        fetch(
          `${API_BASE_URL}/dashboard/alerts`
        ),

        fetch(
          `${API_BASE_URL}/dashboard/inventory-health`
        ),

      ]);


      if (
        !summaryResponse.ok ||
        !productsResponse.ok ||
        !alertsResponse.ok ||
        !healthResponse.ok
      ) {

        throw new Error(
          "Backend request failed."
        );

      }


      const summaryData =
        await summaryResponse.json();

      const productsData =
        await productsResponse.json();

      const alertsData =
        await alertsResponse.json();

      const healthData =
        await healthResponse.json();


      setSummary(
        summaryData
      );


      setProducts(
        Array.isArray(
          productsData.products
        )
          ? productsData.products
          : []
      );


      setAlerts(
        Array.isArray(
          alertsData.alerts
        )
          ? alertsData.alerts
          : []
      );


      setHealth(
        healthData
      );


    } catch (err) {

      console.error(
        "Dashboard loading error:",
        err
      );

      setError(
        "Unable to connect to the FastAPI backend."
      );

    } finally {

      setLoading(false);

    }

  }


  // ==========================================================
  // INITIAL LOAD
  // ==========================================================

  useEffect(() => {

    loadDashboard();

  }, []);


  // ==========================================================
  // LOAD PRODUCT FORECAST
  // ==========================================================

  async function loadForecast(
    productId
  ) {

    if (
      productId === undefined ||
      productId === null
    ) {

      setForecast([]);

      return;

    }


    try {

      const response =
        await fetch(
          `${API_BASE_URL}/forecast/${productId}`
        );


      if (!response.ok) {

        throw new Error(
          "Forecast request failed."
        );

      }


      const data =
        await response.json();


      setForecast(
        Array.isArray(
          data.forecast
        )
          ? data.forecast
          : []
      );


    } catch (err) {

      console.error(
        "Forecast loading error:",
        err
      );

      setForecast([]);

    }

  }


  // ==========================================================
  // SELECT PRODUCT
  // ==========================================================

  function handleProductSelect(
    product
  ) {

    setSelectedProduct(
      product
    );

    setProductDetails(
      product
    );

    loadForecast(
      product.product_id
    );

  }


  // ==========================================================
  // CLOSE PRODUCT DETAILS
  // ==========================================================

  function closeProductDetails() {

    setProductDetails(
      null
    );

  }


  // ==========================================================
  // SIMULATOR
  // ==========================================================

  function openSimulator(
    product
  ) {

    setSimulatorProduct(
      product
    );

  }


  function closeSimulator() {

    setSimulatorProduct(
      null
    );

  }


  // ==========================================================
  // SEARCH
  // ==========================================================

  const filteredProducts =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();


      if (!query) {

        return products;

      }


      return products.filter(
        (product) => {

          const name =
            String(
              product.product_name || ""
            ).toLowerCase();


          const category =
            String(
              product.category || ""
            ).toLowerCase();


          return (
            name.includes(query) ||
            category.includes(query)
          );

        }
      );

    }, [
      products,
      search,
    ]);


  // ==========================================================
  // FORECAST CHART DATA
  // ==========================================================

  const chartData =
    useMemo(() => {

      return forecast.map(
        (item) => {

          const rawDate =
            String(
              item.date || ""
            );


          return {

            date:
              rawDate.length >= 10
                ? rawDate.slice(5, 10)
                : rawDate,

            demand:
              Number(
                item.predicted_demand ??
                item.forecasted_demand ??
                item.demand ??
                0
              ),

          };

        }
      );

    }, [forecast]);


  // ==========================================================
  // SUMMARY VALUES
  // ==========================================================

  const totalProducts =
    Number(
      summary?.total_products ??
      products.length ??
      0
    );


  const criticalStockouts =
    Number(
      summary?.stockout_risk?.critical ??
      health?.critical ??
      0
    );


  const demandSurges =
    Number(
      summary?.demand_surge?.extreme ??
      0
    )
    +
    Number(
      summary?.demand_surge?.high ??
      0
    );


  const purchaseValue =
    Number(
      summary?.reorder?.estimated_purchase_value ??
      0
    );


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <div className="loading-screen">

        <div className="loading-spinner">

          <RefreshCw
            size={30}
          />

        </div>

        <h2>
          Loading AI Inventory Intelligence
        </h2>

        <p>
          Connecting to the prediction engine...
        </p>

      </div>

    );

  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {

    return (

      <div className="error-screen">

        <AlertTriangle
          size={48}
        />

        <h2>
          Backend Connection Error
        </h2>

        <p>
          {error}
        </p>

        <button
          onClick={
            loadDashboard
          }
        >

          Retry

        </button>

      </div>

    );

  }


  // ==========================================================
  // MAIN APPLICATION
  // ==========================================================

  return (

    <div className="app">


      {/* ==================================================== */}
      {/* SIDEBAR */}
      {/* ==================================================== */}

      <aside className="sidebar">


        {/* BRAND */}

        <div className="brand">

          <div className="brand-icon">

            <BrainCircuit
              size={25}
            />

          </div>

          <div>

            <h1>
              AI Inventory
            </h1>

            <span>
              Intelligence
            </span>

          </div>

        </div>


        {/* NAVIGATION */}

        <nav>


          {/* DASHBOARD */}

          <div
            className={
              `nav-item ${
                activePage === "dashboard"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "dashboard"
              );

            }}
          >

            <BarChart3
              size={19}
            />

            <span>
              Dashboard
            </span>

          </div>


          {/* INVENTORY */}

          <div
            className={
              `nav-item ${
                activePage === "inventory"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "inventory"
              );

            }}
          >

            <Package
              size={19}
            />

            <span>
              Inventory
            </span>

          </div>


          {/* DEMAND FORECAST */}

          <div
            className={
              `nav-item ${
                activePage === "forecast"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "forecast"
              );

            }}
          >

            <TrendingUp
              size={19}
            />

            <span>
              Demand Forecast
            </span>

          </div>


          {/* RECOMMENDATIONS */}

          <div
            className={
              `nav-item ${
                activePage === "recommendations"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "recommendations"
              );

            }}
          >

            <Boxes
              size={19}
            />

            <span>
              Recommendations
            </span>

          </div>


          {/* ANALYTICS */}

          <div
            className={
              `nav-item ${
                activePage === "analytics"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "analytics"
              );

            }}
          >

            <FileBarChart
              size={19}
            />

            <span>
              Analytics & Reports
            </span>

          </div>


          {/* AI REPORT */}

          <div
            className={
              `nav-item ${
                activePage === "reports"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "reports"
              );

            }}
          >

            <BrainCircuit
              size={19}
            />

            <span>
              AI Reports
            </span>

          </div>


          {/* PRICE PREDICTION */}

          <div
            className={
              `nav-item ${
                activePage === "price"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "price"
              );

            }}
          >

            <CircleDollarSign
              size={19}
            />

            <span>
              Price Prediction
            </span>

          </div>


          {/* AI DECISION CENTER */}

          <div
            className={
              `nav-item ${
                activePage === "decisions"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "decisions"
              );

            }}
          >

            <BrainCircuit
              size={19}
            />

            <span>
              AI Decision Center
            </span>

          </div>


          {/* MODEL PERFORMANCE */}

          <div
            className={
              `nav-item ${
                activePage === "performance"
                  ? "active"
                  : ""
              }`
            }
            onClick={() => {

              setProductDetails(null);

              setActivePage(
                "performance"
              );

            }}
          >

            <Target
              size={19}
            />

            <span>
              Model Performance
            </span>

          </div>



        </nav>


        {/* SIDEBAR FOOTER */}

        <div className="sidebar-footer">

          <div className="system-status">

            <span className="status-dot"></span>

            AI Engine Online

          </div>

          <small>
            Demand + Inventory Intelligence
          </small>

        </div>

      </aside>


      {/* ==================================================== */}
      {/* MAIN */}
      {/* ==================================================== */}

      <main className="main">


        {/* ================================================== */}
        {/* PRODUCT INTELLIGENCE */}
        {/* ================================================== */}

        {productDetails ? (

          <ProductIntelligence

            product={
              productDetails
            }

            forecast={
              forecast
            }

            onBack={
              closeProductDetails
            }

            onSimulate={
              openSimulator
            }

          />

        ) : (

          <>


            {/* ================================================= */}
            {/* ANALYTICS */}
            {/* ================================================= */}

            {activePage === "analytics" && (

              <AnalyticsDashboard

                products={
                  products
                }

                summary={
                  summary
                }

              />

            )}


            {/* ================================================= */}
            {/* AI REPORT */}
            {/* ================================================= */}

            {activePage === "reports" && (

              <AIReport

                products={
                  products
                }

                summary={
                  summary
                }

              />

            )}


            {/* ================================================= */}
            {/* PRICE PREDICTION */}
            {/* ================================================= */}

            {activePage === "price" && (

              <PricePrediction />

            )}


            {/* ================================================= */}
            {/* AI DECISION CENTER */}
            {/* ================================================= */}

            {activePage === "decisions" && (

              <AIDecisionCenter />

            )}


            {/* ================================================= */}
            {/* MODEL PERFORMANCE */}
            {/* ================================================= */}

            {activePage === "performance" && (

              <ModelPerformance />

            )}


            {/* ================================================= */}
            {/* MODEL PERFORMANCE */}
            {/* ================================================= */}

            {activePage === "performance" && (

              <ModelPerformance />

            )}


            {/* ================================================= */}
            {/* STANDARD PAGES */}
            {/* ================================================= */}

            {activePage !== "analytics" &&
            activePage !== "reports" &&
            activePage !== "price" &&
            activePage !== "decisions" &&
            activePage !== "performance" && (

              <>


                {/* ============================================= */}
                {/* HEADER */}
                {/* ============================================= */}

                <header className="header">

                  <div>

                    <h2>

                      {activePage === "dashboard"
                        ? "Inventory Dashboard"
                        : activePage === "inventory"
                        ? "Inventory Management"
                        : activePage === "forecast"
                        ? "Demand Forecast"
                        : "AI Recommendations"}

                    </h2>

                    <p>
                      AI-powered demand and inventory intelligence
                    </p>

                  </div>


                  <div className="header-actions">

                    <button
                      className="refresh-button"
                      onClick={
                        loadDashboard
                      }
                    >

                      <RefreshCw
                        size={17}
                      />

                      Refresh

                    </button>

                  </div>

                </header>


                {/* ============================================= */}
                {/* DASHBOARD */}
                {/* ============================================= */}

                {activePage === "dashboard" && (

                  <>


                    {/* KPI CARDS */}

                    <section className="kpi-grid">


                      <div className="kpi-card">

                        <div className="kpi-icon">

                          <Package
                            size={21}
                          />

                        </div>

                        <div>

                          <span>
                            Total Products
                          </span>

                          <strong>
                            {totalProducts}
                          </strong>

                        </div>

                      </div>


                      <div className="kpi-card critical">

                        <div className="kpi-icon">

                          <AlertTriangle
                            size={21}
                          />

                        </div>

                        <div>

                          <span>
                            Critical Stockouts
                          </span>

                          <strong>
                            {criticalStockouts}
                          </strong>

                        </div>

                      </div>


                      <div className="kpi-card warning">

                        <div className="kpi-icon">

                          <TrendingUp
                            size={21}
                          />

                        </div>

                        <div>

                          <span>
                            Demand Surges
                          </span>

                          <strong>
                            {demandSurges}
                          </strong>

                        </div>

                      </div>


                      <div className="kpi-card">

                        <div className="kpi-icon">

                          <CircleDollarSign
                            size={21}
                          />

                        </div>

                        <div>

                          <span>
                            Purchase Value
                          </span>

                          <strong>

                            ₹
                            {purchaseValue.toLocaleString(
                              "en-IN",
                              {
                                maximumFractionDigits: 0,
                              }
                            )}

                          </strong>

                        </div>

                      </div>


                    </section>


                    {/* ======================================= */}
                    {/* FORECAST + HEALTH */}
                    {/* ======================================= */}

                    <section className="dashboard-grid">


                      {/* DEMAND FORECAST */}

                      <div className="panel chart-panel">

                        <div className="panel-header">

                          <div>

                            <h3>
                              Demand Forecast
                            </h3>

                            <p>
                              Select a product to view its predicted demand
                            </p>

                          </div>

                        </div>


                        {selectedProduct &&
                        chartData.length > 0 ? (

                          <>

                            <div className="selected-product">

                              <strong>
                                {
                                  selectedProduct.product_name
                                }
                              </strong>

                              <span>
                                {
                                  selectedProduct.category
                                }
                              </span>

                            </div>


                            <div className="chart">

                              <ResponsiveContainer
                                width="100%"
                                height={300}
                              >

                                <AreaChart
                                  data={
                                    chartData
                                  }
                                >

                                  <CartesianGrid
                                    strokeDasharray="3 3"
                                  />

                                  <XAxis
                                    dataKey="date"
                                  />

                                  <YAxis />

                                  <Tooltip />

                                  <Area
                                    type="monotone"
                                    dataKey="demand"
                                    fillOpacity={0.25}
                                  />

                                </AreaChart>

                              </ResponsiveContainer>

                            </div>

                          </>

                        ) : (

                          <div className="empty-chart">

                            <TrendingUp
                              size={42}
                            />

                            <p>
                              Select a product below to view its demand forecast.
                            </p>

                          </div>

                        )}

                      </div>


                      {/* INVENTORY HEALTH */}

                      <div className="panel health-panel">

                        <div className="panel-header">

                          <div>

                            <h3>
                              Inventory Health
                            </h3>

                            <p>
                              Current inventory status
                            </p>

                          </div>

                        </div>


                        <div className="health-score">

                          <div className="score-circle">

                            <strong>
                              {Math.round(
                                Number(
                                  health?.average_health_score ??
                                  0
                                )
                              )}
                            </strong>

                            <span>
                              / 100
                            </span>

                          </div>

                          <p>
                            Average Health Score
                          </p>

                        </div>


                        <div className="health-stats">


                          <div>

                            <span>
                              Healthy
                            </span>

                            <strong>
                              {
                                health?.healthy ??
                                0
                              }
                            </strong>

                          </div>


                          <div>

                            <span>
                              Low Stock
                            </span>

                            <strong>
                              {
                                health?.low_stock ??
                                0
                              }
                            </strong>

                          </div>


                          <div>

                            <span>
                              Overstock
                            </span>

                            <strong>
                              {
                                health?.overstocked ??
                                0
                              }
                            </strong>

                          </div>


                          <div>

                            <span>
                              Critical
                            </span>

                            <strong>
                              {
                                health?.critical ??
                                0
                              }
                            </strong>

                          </div>


                        </div>

                      </div>


                    </section>


                    {/* ======================================= */}
                    {/* AI ALERTS */}
                    {/* ======================================= */}

                    <section className="panel alerts-panel">

                      <div className="panel-header">

                        <div>

                          <h3>
                            AI Alerts
                          </h3>

                          <p>
                            Inventory events requiring attention
                          </p>

                        </div>


                        <span className="alert-count">

                          {
                            alerts.length
                          }

                        </span>

                      </div>


                      {alerts.length === 0 ? (

                        <div className="no-alerts">

                          <span>
                            ✓
                          </span>

                          No critical alerts detected.

                        </div>

                      ) : (

                        <div className="alerts-list">

                          {alerts
                            .slice(
                              0,
                              8
                            )
                            .map(
                              (
                                alert,
                                index
                              ) => (

                                <div
                                  className="alert-row"
                                  key={
                                    `${alert.product_name}-${index}`
                                  }
                                >

                                  <div
                                    className={
                                      `alert-severity ${
                                        String(
                                          alert.severity ||
                                          ""
                                        ).toLowerCase()
                                      }`
                                    }
                                  >

                                    {
                                      alert.severity ||
                                      "ALERT"
                                    }

                                  </div>


                                  <div className="alert-content">

                                    <strong>
                                      {
                                        alert.product_name ||
                                        "Unknown Product"
                                      }
                                    </strong>

                                    <span>
                                      {
                                        alert.message ||
                                        "Inventory attention required."
                                      }
                                    </span>

                                  </div>


                                  <span className="alert-type">

                                    {
                                      alert.type ||
                                      "INVENTORY"
                                    }

                                  </span>

                                </div>

                              )
                            )}

                        </div>

                      )}

                    </section>


                  </>

                )}


                {/* ============================================= */}
                {/* INVENTORY PAGE */}
                {/* ============================================= */}

                {activePage === "inventory" && (

                  <section className="panel products-panel">

                    <div className="panel-header">

                      <div>

                        <h3>
                          Inventory Overview
                        </h3>

                        <p>
                          Current inventory levels across all products
                        </p>

                      </div>


                      <div className="search-box">

                        <Search
                          size={17}
                        />

                        <input
                          type="text"
                          placeholder="Search products..."
                          value={
                            search
                          }
                          onChange={
                            (event) =>
                              setSearch(
                                event.target.value
                              )
                          }
                        />

                      </div>

                    </div>


                    <div className="table-wrapper">

                      <table>

                        <thead>

                          <tr>

                            <th>
                              Product
                            </th>

                            <th>
                              Inventory
                            </th>

                            <th>
                              Stockout Risk
                            </th>

                            <th>
                              AI Decision
                            </th>

                            <th>
                              Actions
                            </th>

                          </tr>

                        </thead>


                        <tbody>

                          {filteredProducts.map(
                            (product) => (

                              <tr
                                key={
                                  product.product_id
                                }
                              >

                                <td>

                                  <div className="product-name">

                                    <strong>
                                      {
                                        product.product_name
                                      }
                                    </strong>

                                    <span>
                                      {
                                        product.category
                                      }
                                    </span>

                                  </div>

                                </td>


                                <td>

                                  {Number(
                                    product.current_inventory ??
                                    0
                                  ).toLocaleString()}

                                </td>


                                <td>

                                  <span
                                    className={
                                      `badge ${
                                        String(
                                          product.stockout_risk ||
                                          ""
                                        ).toLowerCase()
                                      }`
                                    }
                                  >

                                    {
                                      product.stockout_risk ||
                                      "Unknown"
                                    }

                                  </span>

                                </td>


                                <td>

                                  <span
                                    className={
                                      `decision ${
                                        String(
                                          product.ai_decision ||
                                          ""
                                        )
                                          .toLowerCase()
                                          .replaceAll(
                                            " ",
                                            "-"
                                          )
                                      }`
                                    }
                                  >

                                    {
                                      product.ai_decision ||
                                      "Monitor"
                                    }

                                  </span>

                                </td>


                                <td>

                                  <div className="action-buttons">

                                    <button
                                      className="view-button"
                                      onClick={() =>
                                        handleProductSelect(
                                          product
                                        )
                                      }
                                    >

                                      View

                                      <ChevronDown
                                        size={14}
                                      />

                                    </button>


                                    <button
                                      className="simulate-button"
                                      onClick={() =>
                                        openSimulator(
                                          product
                                        )
                                      }
                                    >

                                      Simulate

                                    </button>

                                  </div>

                                </td>

                              </tr>

                            )
                          )}


                          {filteredProducts.length === 0 && (

                            <tr>

                              <td
                                colSpan="5"
                                style={{
                                  textAlign:
                                    "center",
                                  padding:
                                    "30px",
                                }}
                              >

                                No products found.

                              </td>

                            </tr>

                          )}

                        </tbody>

                      </table>

                    </div>

                  </section>

                )}


                {/* ============================================= */}
                {/* FORECAST PAGE */}
                {/* ============================================= */}

                {activePage === "forecast" && (

                  <>

                    <section className="panel products-panel">

                      <div className="panel-header">

                        <div>

                          <h3>
                            Product Demand Forecast
                          </h3>

                          <p>
                            Select a product to visualize its 30-day predicted demand
                          </p>

                        </div>

                      </div>


                      <div className="table-wrapper">

                        <table>

                          <thead>

                            <tr>

                              <th>
                                Product
                              </th>

                              <th>
                                Category
                              </th>

                              <th>
                                Current Inventory
                              </th>

                              <th>
                                30-Day Forecast
                              </th>

                              <th>
                                Demand Surge
                              </th>

                              <th>
                                Action
                              </th>

                            </tr>

                          </thead>


                          <tbody>

                            {products.map(
                              (product) => (

                                <tr
                                  key={
                                    product.product_id
                                  }
                                >

                                  <td>

                                    <div className="product-name">

                                      <strong>
                                        {
                                          product.product_name
                                        }
                                      </strong>

                                    </div>

                                  </td>


                                  <td>
                                    {
                                      product.category
                                    }
                                  </td>


                                  <td>
                                    {Number(
                                      product.current_inventory ??
                                      0
                                    ).toLocaleString()}
                                  </td>


                                  <td>
                                    {Number(
                                      product.forecast_30_day ??
                                      0
                                    ).toLocaleString()}
                                  </td>


                                  <td>

                                    <span
                                      className={
                                        `badge ${
                                          String(
                                            product.demand_surge ||
                                            "Stable"
                                          )
                                            .toLowerCase()
                                            .replaceAll(
                                              " ",
                                              "-"
                                            )
                                        }`
                                      }
                                    >

                                      {
                                        product.demand_surge ||
                                        "Stable"
                                      }

                                    </span>

                                  </td>


                                  <td>

                                    <button
                                      className="view-button"
                                      onClick={() =>
                                        handleProductSelect(
                                          product
                                        )
                                      }
                                    >

                                      View Forecast

                                    </button>

                                  </td>

                                </tr>

                              )
                            )}

                          </tbody>

                        </table>

                      </div>

                    </section>


                    {selectedProduct &&
                    chartData.length > 0 && (

                      <section
                        className="panel chart-panel"
                        style={{
                          marginTop:
                            "18px",
                        }}
                      >

                        <div className="panel-header">

                          <div>

                            <h3>
                              {
                                selectedProduct.product_name
                              }
                            </h3>

                            <p>
                              30-day AI demand prediction
                            </p>

                          </div>

                        </div>


                        <div className="chart">

                          <ResponsiveContainer
                            width="100%"
                            height={380}
                          >

                            <AreaChart
                              data={
                                chartData
                              }
                            >

                              <CartesianGrid
                                strokeDasharray="3 3"
                              />

                              <XAxis
                                dataKey="date"
                              />

                              <YAxis />

                              <Tooltip />

                              <Area
                                type="monotone"
                                dataKey="demand"
                                fillOpacity={0.25}
                              />

                            </AreaChart>

                          </ResponsiveContainer>

                        </div>

                      </section>

                    )}

                  </>

                )}


                {/* ============================================= */}
                {/* RECOMMENDATIONS PAGE */}
                {/* ============================================= */}

                {activePage === "recommendations" && (

                  <section className="panel products-panel">

                    <div className="panel-header">

                      <div>

                        <h3>
                          AI Inventory Recommendations
                        </h3>

                        <p>
                          AI-generated replenishment decisions
                        </p>

                      </div>

                    </div>


                    <div className="table-wrapper">

                      <table>

                        <thead>

                          <tr>

                            <th>
                              Product
                            </th>

                            <th>
                              Inventory
                            </th>

                            <th>
                              30-Day Demand
                            </th>

                            <th>
                              Stockout
                            </th>

                            <th>
                              Reorder Qty
                            </th>

                            <th>
                              Purchase Value
                            </th>

                            <th>
                              AI Decision
                            </th>

                            <th>
                              Action
                            </th>

                          </tr>

                        </thead>


                        <tbody>

                          {products.map(
                            (product) => (

                              <tr
                                key={
                                  product.product_id
                                }
                              >

                                <td>

                                  <div className="product-name">

                                    <strong>
                                      {
                                        product.product_name
                                      }
                                    </strong>

                                    <span>
                                      {
                                        product.category
                                      }
                                    </span>

                                  </div>

                                </td>


                                <td>

                                  {Number(
                                    product.current_inventory ??
                                    0
                                  ).toLocaleString()}

                                </td>


                                <td>

                                  {Number(
                                    product.forecast_30_day ??
                                    0
                                  ).toLocaleString()}

                                </td>


                                <td>

                                  <span
                                    className={
                                      `badge ${
                                        String(
                                          product.stockout_risk ||
                                          ""
                                        ).toLowerCase()
                                      }`
                                    }
                                  >

                                    {
                                      product.stockout_risk ||
                                      "Unknown"
                                    }

                                  </span>

                                </td>


                                <td>

                                  {Number(
                                    product.recommended_reorder_quantity ??
                                    product.reorder_quantity ??
                                    0
                                  ).toLocaleString()}

                                </td>


                                <td>

                                  ₹
                                  {Number(
                                    product.recommended_purchase_value ??
                                    0
                                  ).toLocaleString(
                                    "en-IN",
                                    {
                                      maximumFractionDigits: 0,
                                    }
                                  )}

                                </td>


                                <td>

                                  <span
                                    className={
                                      `decision ${
                                        String(
                                          product.ai_decision ||
                                          ""
                                        )
                                          .toLowerCase()
                                          .replaceAll(
                                            " ",
                                            "-"
                                          )
                                      }`
                                    }
                                  >

                                    {
                                      product.ai_decision ||
                                      "Monitor"
                                    }

                                  </span>

                                </td>


                                <td>

                                  <div className="action-buttons">

                                    <button
                                      className="view-button"
                                      onClick={() =>
                                        handleProductSelect(
                                          product
                                        )
                                      }
                                    >

                                      View

                                    </button>


                                    <button
                                      className="simulate-button"
                                      onClick={() =>
                                        openSimulator(
                                          product
                                        )
                                      }
                                    >

                                      Simulate

                                    </button>

                                  </div>

                                </td>

                              </tr>

                            )
                          )}

                        </tbody>

                      </table>

                    </div>

                  </section>

                )}


              </>

            )}

          </>

        )}

      </main>


      {/* ==================================================== */}
      {/* INVENTORY SIMULATOR */}
      {/* ==================================================== */}

      {simulatorProduct && (

        <InventorySimulator

          product={
            simulatorProduct
          }

          onClose={
            closeSimulator
          }

        />

      )}


    </div>

  );

}


export default App;