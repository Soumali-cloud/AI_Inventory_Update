import {
  AlertTriangle,
  ArrowLeft,
  BrainCircuit,
  CalendarDays,
  CircleDollarSign,
  Package,
  ShoppingCart,
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


function ProductIntelligence({
  product,
  forecast = [],
  onBack,
  onSimulate,
}) {


  // ==========================================================
  // SAFE NUMBER
  // ==========================================================

  function num(value) {

    const result =
      Number(value);

    return Number.isFinite(result)
      ? result
      : 0;

  }


  // ==========================================================
  // PRODUCT VALUES
  // ==========================================================

  const inventory =
    num(
      product?.current_inventory
    );


  const forecast30 =
    num(
      product?.forecast_30_day
    );


  const reorderQuantity =
    num(
      product?.recommended_reorder_quantity ??
      product?.reorder_quantity
    );


  const purchaseValue =
    num(
      product?.recommended_purchase_value
    );


  const decisionScore =
    num(
      product?.decision_score
    );


  const daysInventory =
    num(
      product?.estimated_days_of_inventory ??
      product?.days_of_inventory
    );


  const surge =
    num(
      product?.demand_surge_percentage ??
      product?.demand_surge_percent
    );


  const risk =
    String(
      product?.stockout_risk ||
      "Unknown"
    );


  const decision =
    String(
      product?.ai_decision ||
      "Monitor"
    );


  // ==========================================================
  // FORECAST CHART DATA
  // ==========================================================

  const chartData =
    forecast.map(
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
            num(
              item.predicted_demand ??
              item.forecasted_demand ??
              item.demand
            ),

        };

      }
    );


  // ==========================================================
  // AI EXPLANATION
  // ==========================================================

  function generateExplanation() {

    if (
      risk.toLowerCase() ===
      "critical"
    ) {

      return (
        `The AI engine has classified ${product.product_name} `
        +
        `as a critical inventory risk. Current inventory is `
        +
        `${inventory.toLocaleString()} units compared with `
        +
        `an estimated 30-day demand of `
        +
        `${forecast30.toLocaleString()} units. `
        +
        `Immediate replenishment is recommended.`
      );

    }


    if (
      risk.toLowerCase() ===
      "high"
    ) {

      return (
        `${product.product_name} is showing elevated stockout risk. `
        +
        `Inventory should be monitored closely and replenishment `
        +
        `should be considered before demand increases further.`
      );

    }


    if (
      surge > 15
    ) {

      return (
        `The model detects a significant upcoming demand increase `
        +
        `of ${surge.toFixed(1)}%. `
        +
        `Inventory should be positioned ahead of the expected demand surge.`
      );

    }


    if (
      decision.toLowerCase()
        .includes("reduce")
    ) {

      return (
        `The AI engine indicates that inventory may be higher `
        +
        `than expected demand. Reducing replenishment can help `
        +
        `avoid unnecessary holding costs.`
      );

    }


    return (
      `${product.product_name} currently has a relatively stable `
      +
      `inventory position. Continue monitoring forecasted demand, `
      +
      `inventory coverage and future demand changes.`
    );

  }


  // ==========================================================
  // RISK CLASS
  // ==========================================================

  const riskClass =
    risk
      .toLowerCase()
      .replaceAll(
        " ",
        "-"
      );


  // ==========================================================
  // DECISION CLASS
  // ==========================================================

  const decisionClass =
    decision
      .toLowerCase()
      .replaceAll(
        " ",
        "-"
      );


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="product-intelligence">


      {/* ==================================================== */}
      {/* HEADER */}
      {/* ==================================================== */}

      <div className="product-intelligence-header">


        <button
          className="back-button"
          onClick={
            onBack
          }
        >

          <ArrowLeft
            size={17}
          />

          Back

        </button>


        <div className="product-heading">

          <div className="product-heading-icon">

            <Package
              size={25}
            />

          </div>


          <div>

            <h2>
              {product.product_name}
            </h2>

            <p>
              {product.category || "Inventory"}
              {" • "}
              AI Product Intelligence
            </p>

          </div>

        </div>


        <button
          className="product-simulate-button"
          onClick={() =>
            onSimulate(
              product
            )
          }
        >

          <BrainCircuit
            size={16}
          />

          Simulate

        </button>


      </div>


      {/* ==================================================== */}
      {/* STATUS */}
      {/* ==================================================== */}

      <div className="product-status-row">


        <span
          className={
            `product-risk-badge ${riskClass}`
          }
        >

          {risk}

        </span>


        <span
          className={
            `product-decision-badge ${decisionClass}`
          }
        >

          AI Decision:
          {" "}
          {decision}

        </span>


        <span className="product-score">

          Decision Score:

          <strong>
            {" "}
            {decisionScore.toFixed(0)}
          </strong>

          /100

        </span>


      </div>


      {/* ==================================================== */}
      {/* KPI CARDS */}
      {/* ==================================================== */}

      <div className="product-kpi-grid">


        {/* INVENTORY */}

        <div className="product-kpi-card">

          <div className="product-kpi-icon">

            <Package
              size={19}
            />

          </div>


          <span>
            Current Inventory
          </span>


          <strong>
            {inventory.toLocaleString()}
          </strong>


          <small>
            units available
          </small>

        </div>


        {/* FORECAST */}

        <div className="product-kpi-card">

          <div className="product-kpi-icon">

            <TrendingUp
              size={19}
            />

          </div>


          <span>
            30-Day Demand
          </span>


          <strong>
            {forecast30.toLocaleString()}
          </strong>


          <small>
            predicted units
          </small>

        </div>


        {/* DAYS INVENTORY */}

        <div className="product-kpi-card">

          <div className="product-kpi-icon">

            <CalendarDays
              size={19}
            />

          </div>


          <span>
            Days of Inventory
          </span>


          <strong>

            {daysInventory > 0
              ? daysInventory.toFixed(1)
              : "N/A"}

          </strong>


          <small>
            estimated coverage
          </small>

        </div>


        {/* SURGE */}

        <div className="product-kpi-card">

          <div className="product-kpi-icon surge">

            {surge > 0 ? (

              <TrendingUp
                size={19}
              />

            ) : (

              <TrendingDown
                size={19}
              />

            )}

          </div>


          <span>
            Demand Surge
          </span>


          <strong>

            {surge > 0
              ? `+${surge.toFixed(1)}%`
              : "Stable"}

          </strong>


          <small>
            predicted change
          </small>

        </div>

      </div>


      {/* ==================================================== */}
      {/* FORECAST + AI ANALYSIS */}
      {/* ==================================================== */}

      <div className="product-main-grid">


        {/* FORECAST CHART */}

        <section className="product-panel">

          <div className="product-panel-header">

            <div>

              <h3>
                30-Day Demand Forecast
              </h3>

              <p>
                Machine-learning prediction for upcoming demand
              </p>

            </div>


            <TrendingUp
              size={19}
            />

          </div>


          {chartData.length > 0 ? (

            <div className="product-chart">

              <ResponsiveContainer
                width="100%"
                height={350}
              >

                <AreaChart
                  data={chartData}
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

          ) : (

            <div className="product-empty">

              <TrendingUp
                size={40}
              />

              <p>
                Forecast data is not available for this product.
              </p>

            </div>

          )}

        </section>


        {/* AI ANALYSIS */}

        <section className="product-panel">

          <div className="product-panel-header">

            <div>

              <h3>
                AI Analysis
              </h3>

              <p>
                Why the system made this decision
              </p>

            </div>


            <BrainCircuit
              size={19}
            />

          </div>


          <div className="ai-analysis-content">


            <div
              className={
                `ai-analysis-alert ${riskClass}`
              }
            >

              <AlertTriangle
                size={18}
              />

              <div>

                <strong>
                  Inventory Risk: {risk}
                </strong>

                <span>
                  {generateExplanation()}
                </span>

              </div>

            </div>


            <div className="analysis-metrics">


              <div>

                <span>
                  AI Decision
                </span>

                <strong>
                  {decision}
                </strong>

              </div>


              <div>

                <span>
                  Decision Score
                </span>

                <strong>
                  {decisionScore.toFixed(0)}/100
                </strong>

              </div>


              <div>

                <span>
                  Demand Surge
                </span>

                <strong>

                  {surge > 0
                    ? `+${surge.toFixed(1)}%`
                    : "Stable"}

                </strong>

              </div>


            </div>


          </div>

        </section>

      </div>


      {/* ==================================================== */}
      {/* REPLENISHMENT */}
      {/* ==================================================== */}

      <section className="product-panel replenishment-panel">


        <div className="product-panel-header">

          <div>

            <h3>
              Replenishment Recommendation
            </h3>

            <p>
              AI-generated purchasing recommendation
            </p>

          </div>


          <ShoppingCart
            size={19}
          />

        </div>


        <div className="replenishment-grid">


          <div>

            <span>
              Recommended Order
            </span>

            <strong>
              {reorderQuantity.toLocaleString()}
            </strong>

            <small>
              units
            </small>

          </div>


          <div>

            <span>
              Estimated Purchase Value
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

            <small>
              estimated cost
            </small>

          </div>


          <div>

            <span>
              Current Inventory
            </span>

            <strong>
              {inventory.toLocaleString()}
            </strong>

            <small>
              units
            </small>

          </div>


          <div>

            <span>
              Forecast Demand
            </span>

            <strong>
              {forecast30.toLocaleString()}
            </strong>

            <small>
              next 30 days
            </small>

          </div>


        </div>


        <div className="replenishment-message">

          <CircleDollarSign
            size={18}
          />


          <span>

            {reorderQuantity > 0

              ? `The AI engine recommends replenishing approximately ${reorderQuantity.toLocaleString()} units based on predicted demand and current inventory.`

              : "The AI engine does not currently recommend additional replenishment for this product."}

          </span>

        </div>


      </section>


    </div>

  );

}


export default ProductIntelligence;