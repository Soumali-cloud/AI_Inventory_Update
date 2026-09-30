import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BrainCircuit,
  CheckCircle2,
  CircleDollarSign,
  Eye,
  Loader2,
  Package,
  Search,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
  XCircle,
} from "lucide-react";

import "./AIDecisionCenter.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function AIDecisionCenter() {
  const [decisions, setDecisions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [decisionFilter, setDecisionFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDecisionData();
  }, []);

  async function loadDecisionData() {
    try {
      setLoading(true);
      setError(null);

      const [decisionsResponse, summaryResponse] =
        await Promise.all([
          fetch(`${API_BASE_URL}/decisions/all`),
          fetch(`${API_BASE_URL}/decisions/summary`),
        ]);

      if (!decisionsResponse.ok) {
        throw new Error(
          "Unable to load AI decision data."
        );
      }

      if (!summaryResponse.ok) {
        throw new Error(
          "Unable to load AI decision summary."
        );
      }

      const decisionsData =
        await decisionsResponse.json();

      const summaryData =
        await summaryResponse.json();

      setDecisions(
        decisionsData.decisions || []
      );

      setSummary(summaryData);
    } catch (err) {
      console.error(
        "AI Decision Center error:",
        err
      );

      setError(
        err.message ||
          "Unable to load AI decisions."
      );
    } finally {
      setLoading(false);
    }
  }

  const decisionTypes = useMemo(() => {
    return [
      ...new Set(
        decisions
          .map((item) => item.ai_decision)
          .filter(Boolean)
      ),
    ].sort();
  }, [decisions]);

  const filteredDecisions = useMemo(() => {
    const query = search
      .trim()
      .toLowerCase();

    return decisions
      .filter((item) => {
        if (
          priorityFilter !== "ALL" &&
          String(
            item.decision_priority
          ).toUpperCase() !==
            priorityFilter
        ) {
          return false;
        }

        if (
          decisionFilter !== "ALL" &&
          String(
            item.ai_decision
          ) !== decisionFilter
        ) {
          return false;
        }

        if (!query) {
          return true;
        }

        const productId = String(
          item.product_id || ""
        ).toLowerCase();

        const productName = String(
          item.product_name || ""
        ).toLowerCase();

        const category = String(
          item.category || ""
        ).toLowerCase();

        const decision = String(
          item.ai_decision || ""
        ).toLowerCase();

        return (
          productId.includes(query) ||
          productName.includes(query) ||
          category.includes(query) ||
          decision.includes(query)
        );
      })
      .sort(
        (a, b) =>
          Number(
            b.ai_confidence_score || 0
          ) -
          Number(
            a.ai_confidence_score || 0
          )
      );
  }, [
    decisions,
    search,
    priorityFilter,
    decisionFilter,
  ]);

  const criticalCount =
    Number(summary?.critical || 0);

  const highCount =
    Number(summary?.high || 0);

  const mediumCount =
    Number(summary?.medium || 0);

  const lowCount =
    Number(summary?.low || 0);

  const totalProducts =
    Number(
      summary?.total_products ||
        decisions.length
    );

  const urgentCount =
    decisions.filter((item) => {
      const decision = String(
        item.ai_decision || ""
      ).toUpperCase();

      return (
        decision === "URGENTLY REPLENISH" ||
        decision === "REPLENISH SOON"
      );
    }).length;

  const stockIncreaseCount =
    decisions.filter(
      (item) =>
        String(
          item.ai_decision || ""
        ).toUpperCase() ===
        "INCREASE STOCK"
    ).length;

  const reduceInventoryCount =
    decisions.filter(
      (item) =>
        String(
          item.ai_decision || ""
        ).toUpperCase() ===
        "REDUCE INVENTORY"
    ).length;

  function formatPrice(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "N/A";
    }

    return `₹${number.toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 2,
      }
    )}`;
  }

  function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "0";
    }

    return number.toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 1,
      }
    );
  }

  function getPriorityClass(priority) {
    return String(
      priority || "LOW"
    ).toLowerCase();
  }

  function getDecisionIcon(decision) {
    const normalized = String(
      decision || ""
    ).toUpperCase();

    if (
      normalized.includes(
        "URGENTLY"
      )
    ) {
      return (
        <ShieldAlert size={17} />
      );
    }

    if (
      normalized.includes(
        "REPLENISH"
      )
    ) {
      return (
        <Package size={17} />
      );
    }

    if (
      normalized.includes(
        "INCREASE"
      )
    ) {
      return (
        <TrendingUp size={17} />
      );
    }

    if (
      normalized.includes(
        "REDUCE"
      )
    ) {
      return (
        <TrendingDown size={17} />
      );
    }

    if (
      normalized.includes(
        "PRICE"
      )
    ) {
      return (
        <CircleDollarSign
          size={17}
        />
      );
    }

    if (
      normalized.includes(
        "PROMOTION"
      )
    ) {
      return (
        <ArrowDown size={17} />
      );
    }

    if (
      normalized.includes(
        "MAINTAIN"
      )
    ) {
      return (
        <CheckCircle2
          size={17}
        />
      );
    }

    return <Eye size={17} />;
  }

  if (loading) {
    return (
      <div className="ai-decision-loading">
        <Loader2
          size={34}
          className="ai-decision-spinner"
        />

        <h3>
          Loading AI Decision Center
        </h3>

        <p>
          Combining inventory, demand
          and price intelligence...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-decision-error">
        <XCircle size={28} />

        <div>
          <h3>
            AI Decision Center unavailable
          </h3>

          <p>{error}</p>

          <button
            onClick={loadDecisionData}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-decision-page">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <div className="ai-decision-header">
        <div>
          <div className="ai-decision-title">
            <BrainCircuit size={31} />

            <h1>
              AI Decision Center
            </h1>
          </div>

          <p>
            Unified AI recommendations combining
            demand, inventory, stockout risk and
            price intelligence.
          </p>
        </div>

        <div className="ai-engine-badge">
          <BrainCircuit size={17} />
          AI Business Intelligence
        </div>
      </div>


      {/* =====================================================
          KPI CARDS
      ====================================================== */}

      <div className="ai-decision-kpis">

        <div className="ai-decision-kpi">
          <div className="ai-kpi-icon total">
            <BrainCircuit size={23} />
          </div>

          <div>
            <span>
              PRODUCTS ANALYZED
            </span>

            <strong>
              {totalProducts}
            </strong>
          </div>
        </div>


        <div className="ai-decision-kpi critical">
          <div className="ai-kpi-icon">
            <ShieldAlert size={23} />
          </div>

          <div>
            <span>
              CRITICAL
            </span>

            <strong>
              {criticalCount}
            </strong>
          </div>
        </div>


        <div className="ai-decision-kpi high">
          <div className="ai-kpi-icon">
            <AlertTriangle size={23} />
          </div>

          <div>
            <span>
              HIGH PRIORITY
            </span>

            <strong>
              {highCount}
            </strong>
          </div>
        </div>


        <div className="ai-decision-kpi medium">
          <div className="ai-kpi-icon">
            <TrendingUp size={23} />
          </div>

          <div>
            <span>
              MEDIUM
            </span>

            <strong>
              {mediumCount}
            </strong>
          </div>
        </div>


        <div className="ai-decision-kpi low">
          <div className="ai-kpi-icon">
            <CheckCircle2 size={23} />
          </div>

          <div>
            <span>
              LOW
            </span>

            <strong>
              {lowCount}
            </strong>
          </div>
        </div>

      </div>


      {/* =====================================================
          ACTION SUMMARY
      ====================================================== */}

      <div className="ai-action-summary">

        <div className="ai-action-card urgent">
          <ShieldAlert size={21} />

          <div>
            <span>
              REPLENISHMENT ALERTS
            </span>

            <strong>
              {urgentCount}
            </strong>

            <small>
              Products need stock attention
            </small>
          </div>
        </div>


        <div className="ai-action-card increase">
          <ArrowUp size={21} />

          <div>
            <span>
              INCREASE STOCK
            </span>

            <strong>
              {stockIncreaseCount}
            </strong>

            <small>
              Demand indicates higher inventory
            </small>
          </div>
        </div>


        <div className="ai-action-card reduce">
          <ArrowDown size={21} />

          <div>
            <span>
              REDUCE INVENTORY
            </span>

            <strong>
              {reduceInventoryCount}
            </strong>

            <small>
              Potential overstock detected
            </small>
          </div>
        </div>

      </div>


      {/* =====================================================
          FILTERS
      ====================================================== */}

      <div className="ai-decision-filters">

        <div className="ai-search">
          <Search size={18} />

          <input
            type="text"
            placeholder="Search product, category or decision..."
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
          />
        </div>


        <select
          value={priorityFilter}
          onChange={(event) =>
            setPriorityFilter(
              event.target.value
            )
          }
        >
          <option value="ALL">
            All Priorities
          </option>

          <option value="CRITICAL">
            Critical
          </option>

          <option value="HIGH">
            High
          </option>

          <option value="MEDIUM">
            Medium
          </option>

          <option value="LOW">
            Low
          </option>
        </select>


        <select
          value={decisionFilter}
          onChange={(event) =>
            setDecisionFilter(
              event.target.value
            )
          }
        >
          <option value="ALL">
            All AI Decisions
          </option>

          {decisionTypes.map(
            (decision) => (
              <option
                key={decision}
                value={decision}
              >
                {decision}
              </option>
            )
          )}
        </select>

      </div>


      {/* =====================================================
          TABLE
      ====================================================== */}

      <div className="ai-decision-table-card">

        <div className="ai-table-header">
          <div>
            <h2>
              AI Recommended Actions
            </h2>

            <p>
              {filteredDecisions.length} products
              matching current filters
            </p>
          </div>

          <div className="ai-confidence-label">
            <BrainCircuit size={16} />
            AI Confidence
          </div>
        </div>


        <div className="ai-table-wrapper">

          <table className="ai-decision-table">

            <thead>
              <tr>
                <th>
                  PRODUCT
                </th>

                <th>
                  INVENTORY
                </th>

                <th>
                  DEMAND
                </th>

                <th>
                  DAYS OF INVENTORY
                </th>

                <th>
                  STOCKOUT RISK
                </th>

                <th>
                  PRICE
                </th>

                <th>
                  AI DECISION
                </th>

                <th>
                  CONFIDENCE
                </th>
              </tr>
            </thead>


            <tbody>

              {filteredDecisions.map(
                (item, index) => {

                  const confidence =
                    Number(
                      item.ai_confidence_score ||
                        0
                    );

                  const priceChange =
                    Number(
                      item.expected_price_change_percent
                    );

                  return (
                    <tr
                      key={`${item.product_id}-${index}`}
                    >

                      {/* PRODUCT */}

                      <td>
                        <div className="ai-product-cell">

                          <div className="ai-product-icon">
                            <Package
                              size={17}
                            />
                          </div>

                          <div>
                            <strong>
                              {item.product_name ||
                                item.product_id}
                            </strong>

                            <span>
                              {item.product_id}
                            </span>

                            {item.category && (
                              <small>
                                {item.category}
                              </small>
                            )}
                          </div>

                        </div>
                      </td>


                      {/* INVENTORY */}

                      <td>
                        <strong>
                          {formatNumber(
                            item.current_inventory
                          )}
                        </strong>
                      </td>


                      {/* DEMAND */}

                      <td>
                        <strong>
                          {formatNumber(
                            item.average_daily_demand
                          )}
                        </strong>

                        <span className="ai-unit">
                          / day
                        </span>
                      </td>


                      {/* DAYS */}

                      <td>
                        <strong>
                          {formatNumber(
                            item.estimated_days_of_inventory
                          )}
                        </strong>

                        <span className="ai-unit">
                          days
                        </span>
                      </td>


                      {/* STOCKOUT */}

                      <td>
                        <span
                          className={`ai-risk-badge ${String(
                            item.stockout_risk ||
                              "Low"
                          ).toLowerCase()}`}
                        >
                          {item.stockout_risk ||
                            "Low"}
                        </span>
                      </td>


                      {/* PRICE */}

                      <td>
                        <div className="ai-price-cell">

                          <strong>
                            {formatPrice(
                              item.current_price
                            )}
                          </strong>

                          {Number.isFinite(
                            priceChange
                          ) && (
                            <span
                              className={
                                priceChange >=
                                0
                                  ? "price-up"
                                  : "price-down"
                              }
                            >
                              {priceChange >=
                              0 ? (
                                <ArrowUp
                                  size={12}
                                />
                              ) : (
                                <ArrowDown
                                  size={12}
                                />
                              )}

                              {Math.abs(
                                priceChange
                              ).toFixed(1)}
                              %
                            </span>
                          )}

                        </div>
                      </td>


                      {/* DECISION */}

                      <td>

                        <div
                          className={`ai-decision-badge ${getPriorityClass(
                            item.decision_priority
                          )}`}
                        >
                          {getDecisionIcon(
                            item.ai_decision
                          )}

                          <span>
                            {item.ai_decision}
                          </span>
                        </div>

                        {item.ai_explanation && (
                          <div className="ai-explanation">
                            {item.ai_explanation}
                          </div>
                        )}

                      </td>


                      {/* CONFIDENCE */}

                      <td>

                        <div className="confidence-cell">

                          <div className="confidence-number">
                            {confidence}%
                          </div>

                          <div className="confidence-bar">
                            <div
                              className="confidence-fill"
                              style={{
                                width: `${Math.min(
                                  confidence,
                                  100
                                )}%`,
                              }}
                            />
                          </div>

                        </div>

                      </td>

                    </tr>
                  );
                }
              )}

            </tbody>

          </table>


          {filteredDecisions.length ===
            0 && (
            <div className="ai-no-results">
              <Search size={32} />

              <h3>
                No matching products
              </h3>

              <p>
                Try changing the search or
                filter settings.
              </p>
            </div>
          )}

        </div>

      </div>


      {/* =====================================================
          AI EXPLANATION
      ====================================================== */}

      <div className="ai-decision-footer">

        <div className="ai-footer-icon">
          <BrainCircuit size={27} />
        </div>

        <div>
          <h3>
            How the AI Decision Engine works
          </h3>

          <p>
            The decision engine combines current
            inventory, demand velocity, demand
            growth, days of inventory, stockout
            risk and predicted price movement to
            prioritize the most appropriate business
            action for each product.
          </p>
        </div>

      </div>

    </div>
  );
}

export default AIDecisionCenter;