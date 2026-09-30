import {
  AlertTriangle,
  BrainCircuit,
  CircleDollarSign,
  Download,
  FileText,
  Package,
  RefreshCw,
  TrendingUp,
} from "lucide-react";

import { useMemo, useState } from "react";


function AIReport({
  products = [],
  summary = null,
}) {

  const [generating, setGenerating] =
    useState(false);

  const [generated, setGenerated] =
    useState(false);


  // ==========================================================
  // SAFE NUMBER
  // ==========================================================

  function num(value) {

    const result = Number(value);

    return Number.isFinite(result)
      ? result
      : 0;
  }


  // ==========================================================
  // ANALYZE INVENTORY DATA
  // ==========================================================

  const analysis = useMemo(() => {

    const totalProducts =
      products.length;


    const totalInventory =
      products.reduce(
        (total, product) =>
          total +
          num(
            product.current_inventory
          ),
        0
      );


    const totalForecast =
      products.reduce(
        (total, product) =>
          total +
          num(
            product.forecast_30_day
          ),
        0
      );


    const purchaseValue =
      products.reduce(
        (total, product) =>
          total +
          num(
            product.recommended_purchase_value
          ),
        0
      );


    const critical =
      products.filter(
        (product) =>
          String(
            product.stockout_risk || ""
          ).toLowerCase() === "critical"
      );


    const highRisk =
      products.filter(
        (product) =>
          String(
            product.stockout_risk || ""
          ).toLowerCase() === "high"
      );


    const overstock =
      products.filter(
        (product) => {

          const decision =
            String(
              product.ai_decision || ""
            ).toLowerCase();


          return (
            decision.includes("reduce") ||
            decision.includes("overstock")
          );
        }
      );


    const surgeProducts =
      [...products]
        .map((product) => ({
          ...product,

          surge: num(
            product.demand_surge_percentage ??
            product.demand_surge_percent
          ),
        }))
        .filter(
          (product) =>
            product.surge > 0
        )
        .sort(
          (a, b) =>
            b.surge - a.surge
        );


    const priorityProducts =
      [...products]
        .sort(
          (a, b) =>
            num(
              b.decision_score
            ) -
            num(
              a.decision_score
            )
        )
        .slice(0, 5);


    const buyNow =
      products.filter(
        (product) =>
          String(
            product.ai_decision || ""
          ).toLowerCase() === "buy now"
      );


    const buyProducts =
      products.filter(
        (product) =>
          String(
            product.ai_decision || ""
          ).toLowerCase() === "buy"
      );


    return {

      totalProducts,

      totalInventory,

      totalForecast,

      purchaseValue,

      critical,

      highRisk,

      overstock,

      surgeProducts,

      priorityProducts,

      buyNow,

      buyProducts,

    };

  }, [products]);


  // ==========================================================
  // GENERATE REPORT
  // ==========================================================

  function generateReport() {

    setGenerating(true);

    setGenerated(false);


    setTimeout(() => {

      setGenerating(false);

      setGenerated(true);

    }, 900);
  }


  // ==========================================================
  // EXPORT / PRINT
  // ==========================================================

  function downloadReport() {

    window.print();
  }


  // ==========================================================
  // EXECUTIVE SUMMARY
  // ==========================================================

  const executiveSummary =
    useMemo(() => {

      if (
        analysis.critical.length > 0
      ) {

        return (
          `The AI inventory engine has identified `
          +
          `${analysis.critical.length} `
          +
          `critical stockout-risk product(s). `
          +
          `Immediate replenishment should be prioritized `
          +
          `to reduce the risk of inventory shortages.`
        );
      }


      if (
        analysis.highRisk.length > 0
      ) {

        return (
          `The inventory position is generally stable, `
          +
          `but ${analysis.highRisk.length} product(s) `
          +
          `are showing high stockout risk and should be monitored closely.`
        );
      }


      if (
        analysis.surgeProducts.length > 0
      ) {

        const product =
          analysis.surgeProducts[0];


        return (
          `Demand analysis indicates upcoming growth. `
          +
          `${product.product_name} has the strongest `
          +
          `projected demand surge of `
          +
          `${product.surge.toFixed(1)}%.`
        );
      }


      return (
        "The AI inventory engine currently indicates a relatively stable inventory position. "
        +
        "Continued monitoring of demand forecasts and inventory coverage is recommended."
      );

    }, [analysis]);


  // ==========================================================
  // DEMAND OUTLOOK
  // ==========================================================

  const demandOutlook =
    analysis.totalInventory >
    analysis.totalForecast

      ? "Current inventory is higher than the aggregate 30-day demand forecast."

      : "Aggregate 30-day forecasted demand exceeds current inventory, indicating potential replenishment pressure.";


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="ai-report-page">


      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div className="report-header">

        <div className="report-title">

          <div className="report-title-icon">

            <BrainCircuit
              size={24}
            />

          </div>


          <div>

            <h2>
              AI Inventory Report
            </h2>

            <p>
              Automated management analysis from the inventory intelligence engine
            </p>

          </div>

        </div>


        <div className="report-actions">

          <button
            className="generate-report-button"
            onClick={
              generateReport
            }
            disabled={
              generating
            }
          >

            {generating ? (

              <>

                <RefreshCw
                  size={16}
                  className="spin"
                />

                Analyzing...

              </>

            ) : (

              <>

                <BrainCircuit
                  size={16}
                />

                Generate AI Report

              </>

            )}

          </button>


          {generated && (

            <button
              className="download-report-button"
              onClick={
                downloadReport
              }
            >

              <Download
                size={16}
              />

              Export / Print

            </button>

          )}

        </div>

      </div>


      {/* ================================================== */}
      {/* GENERATED MESSAGE */}
      {/* ================================================== */}

      {generated && (

        <div className="report-generated">

          <span>
            ✓
          </span>

          AI analysis completed successfully using the current inventory dataset.

        </div>

      )}


      {/* ================================================== */}
      {/* EXECUTIVE SUMMARY */}
      {/* ================================================== */}

      <section className="report-section executive-section">

        <div className="section-heading">

          <div className="section-heading-icon">

            <FileText
              size={18}
            />

          </div>


          <div>

            <h3>
              Executive Summary
            </h3>

            <p>
              High-level inventory intelligence
            </p>

          </div>

        </div>


        <div className="executive-content">

          <p>
            {executiveSummary}
          </p>

        </div>

      </section>


      {/* ================================================== */}
      {/* KPI CARDS */}
      {/* ================================================== */}

      <section className="report-kpis">


        <div className="report-kpi">

          <div className="report-kpi-icon">

            <Package
              size={19}
            />

          </div>

          <span>
            Products Analyzed
          </span>

          <strong>
            {analysis.totalProducts}
          </strong>

        </div>


        <div className="report-kpi">

          <div className="report-kpi-icon">

            <TrendingUp
              size={19}
            />

          </div>

          <span>
            30-Day Forecast
          </span>

          <strong>
            {analysis.totalForecast.toLocaleString()}
          </strong>

        </div>


        <div className="report-kpi">

          <div className="report-kpi-icon danger">

            <AlertTriangle
              size={19}
            />

          </div>

          <span>
            Critical Risks
          </span>

          <strong>
            {analysis.critical.length}
          </strong>

        </div>


        <div className="report-kpi">

          <div className="report-kpi-icon money">

            <CircleDollarSign
              size={19}
            />

          </div>

          <span>
            Replenishment Value
          </span>

          <strong>

            ₹
            {analysis.purchaseValue.toLocaleString(
              "en-IN",
              {
                maximumFractionDigits: 0,
              }
            )}

          </strong>

        </div>

      </section>


      {/* ================================================== */}
      {/* DEMAND + RISK */}
      {/* ================================================== */}

      <div className="report-two-column">


        {/* DEMAND OUTLOOK */}

        <section className="report-section">

          <div className="section-heading">

            <div className="section-heading-icon">

              <TrendingUp
                size={18}
              />

            </div>


            <div>

              <h3>
                Demand Outlook
              </h3>

              <p>
                Forecast interpretation
              </p>

            </div>

          </div>


          <div className="report-text">

            <p>
              {demandOutlook}
            </p>


            {analysis.surgeProducts.length > 0 && (

              <div className="highlight-box">

                <strong>
                  Highest Demand Surge
                </strong>

                <span>
                  {
                    analysis.surgeProducts[0]
                      .product_name
                  }
                </span>

                <b>
                  +
                  {
                    analysis.surgeProducts[0]
                      .surge
                      .toFixed(1)
                  }%
                </b>

              </div>

            )}

          </div>

        </section>


        {/* INVENTORY RISK */}

        <section className="report-section">

          <div className="section-heading">

            <div className="section-heading-icon danger">

              <AlertTriangle
                size={18}
              />

            </div>


            <div>

              <h3>
                Inventory Risk
              </h3>

              <p>
                Products requiring attention
              </p>

            </div>

          </div>


          <div className="risk-summary">


            <div className="risk-line critical">

              <span>
                Critical
              </span>

              <strong>
                {analysis.critical.length}
              </strong>

            </div>


            <div className="risk-line high">

              <span>
                High
              </span>

              <strong>
                {analysis.highRisk.length}
              </strong>

            </div>


            <div className="risk-line overstock">

              <span>
                Overstock / Reduce
              </span>

              <strong>
                {analysis.overstock.length}
              </strong>

            </div>


          </div>

        </section>

      </div>


      {/* ================================================== */}
      {/* AI PRIORITY ACTIONS */}
      {/* ================================================== */}

      <section className="report-section">

        <div className="section-heading">

          <div className="section-heading-icon">

            <BrainCircuit
              size={18}
            />

          </div>


          <div>

            <h3>
              AI Priority Actions
            </h3>

            <p>
              Products ranked by the decision engine
            </p>

          </div>

        </div>


        <div className="priority-table">


          <div className="priority-header">

            <span>
              Product
            </span>

            <span>
              Risk
            </span>

            <span>
              AI Decision
            </span>

            <span>
              Score
            </span>

          </div>


          {analysis.priorityProducts.map(
            (
              product,
              index
            ) => (

              <div
                className="priority-row"
                key={
                  product.product_id ||
                  index
                }
              >


                <div className="priority-product">

                  <span className="priority-number">
                    {index + 1}
                  </span>


                  <div>

                    <strong>
                      {product.product_name}
                    </strong>

                    <small>
                      {product.category}
                    </small>

                  </div>

                </div>


                <span
                  className={
                    `report-badge ${
                      String(
                        product.stockout_risk ||
                        "Unknown"
                      ).toLowerCase()
                    }`
                  }
                >

                  {
                    product.stockout_risk ||
                    "Unknown"
                  }

                </span>


                <strong>
                  {
                    product.ai_decision ||
                    "Monitor"
                  }
                </strong>


                <strong>
                  {num(
                    product.decision_score
                  ).toFixed(0)}
                </strong>


              </div>

            )
          )}


        </div>

      </section>


      {/* ================================================== */}
      {/* AI RECOMMENDATION */}
      {/* ================================================== */}

      <section className="report-section recommendation-section">

        <div className="recommendation-icon">

          <BrainCircuit
            size={22}
          />

        </div>


        <div>

          <h3>
            AI Recommended Action
          </h3>


          <p>

            {analysis.buyNow.length > 0

              ? `${analysis.buyNow.length} product(s) are classified as BUY NOW. Prioritize these products for immediate replenishment.`

              : analysis.buyProducts.length > 0

              ? `${analysis.buyProducts.length} product(s) are recommended for replenishment based on current demand and inventory conditions.`

              : "No immediate BUY NOW recommendation has been generated. Continue monitoring demand and inventory coverage."
            }

          </p>

        </div>

      </section>


      {/* ================================================== */}
      {/* FOOTER */}
      {/* ================================================== */}

      <div className="report-footer">

        <span>
          AI Inventory Intelligence
        </span>

        <span>
          •
        </span>

        <span>
          Machine Learning + Inventory Analytics
        </span>

      </div>


    </div>

  );
}


// ============================================================
// IMPORTANT: DEFAULT EXPORT
// ============================================================

export default AIReport;