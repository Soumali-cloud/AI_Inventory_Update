import { useMemo, useState } from "react";

import {
  AlertTriangle,
  BarChart3,
  Boxes,
  Package,
  Search,
  TrendingUp,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./AnalyticsDashboard.css";


function AnalyticsDashboard({
  products = [],
  summary = {},
}) {

  const [search, setSearch] = useState("");

  const [category, setCategory] =
    useState("All");


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
  // CATEGORIES
  // ==========================================================

  const categories =
    useMemo(() => {

      const values =
        products
          .map(
            (product) =>
              product.category
          )
          .filter(Boolean);


      return [
        "All",
        ...Array.from(
          new Set(values)
        ).sort(),
      ];

    }, [products]);


  // ==========================================================
  // FILTER PRODUCTS
  // ==========================================================

  const filteredProducts =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();


      return products.filter(
        (product) => {

          const name =
            String(
              product.product_name ||
              ""
            ).toLowerCase();


          const productCategory =
            String(
              product.category ||
              ""
            );


          const matchesSearch =
            !query ||
            name.includes(query);


          const matchesCategory =
            category === "All" ||
            productCategory === category;


          return (
            matchesSearch &&
            matchesCategory
          );

        }
      );

    }, [
      products,
      search,
      category,
    ]);


  // ==========================================================
  // DEMAND DATA
  // ==========================================================

  const demandData =
    useMemo(() => {

      return [...filteredProducts]

        .sort(
          (a, b) =>
            num(
              b.forecast_30_day
            ) -
            num(
              a.forecast_30_day
            )
        )

        .slice(0, 10)

        .map(
          (product) => ({

            product:
              product.product_name,

            demand:
              Number(
                num(
                  product.forecast_30_day
                ).toFixed(0)
              ),

          })
        );

    }, [
      filteredProducts,
    ]);


  // ==========================================================
  // INVENTORY VS DEMAND
  // ==========================================================

  const inventoryDemandData =
    useMemo(() => {

      return [...filteredProducts]

        .sort(
          (a, b) =>
            num(
              b.forecast_30_day
            ) -
            num(
              a.forecast_30_day
            )
        )

        .slice(0, 10)

        .map(
          (product) => ({

            product:
              product.product_name,

            inventory:
              num(
                product.current_inventory
              ),

            demand:
              num(
                product.forecast_30_day
              ),

          })
        );

    }, [
      filteredProducts,
    ]);


  // ==========================================================
  // STOCKOUT RISK
  // ==========================================================

  const stockoutData =
    useMemo(() => {

      const counts = {

        Critical: 0,

        High: 0,

        Medium: 0,

        Low: 0,

      };


      filteredProducts.forEach(
        (product) => {

          const risk =
            String(
              product.stockout_risk ||
              ""
            ).toLowerCase();


          if (
            risk === "critical"
          ) {

            counts.Critical += 1;

          } else if (
            risk === "high"
          ) {

            counts.High += 1;

          } else if (
            risk === "medium"
          ) {

            counts.Medium += 1;

          } else {

            counts.Low += 1;

          }

        }
      );


      return Object.entries(
        counts
      ).map(
        ([name, value]) => ({

          name,

          value,

        })
      );

    }, [
      filteredProducts,
    ]);


  // ==========================================================
  // AI DECISION DISTRIBUTION
  // ==========================================================

  const decisionData =
    useMemo(() => {

      const counts = {};


      filteredProducts.forEach(
        (product) => {

          const decision =
            product.ai_decision ||
            "Monitor";


          counts[decision] =
            (counts[decision] || 0) +
            1;

        }
      );


      return Object.entries(
        counts
      )

        .sort(
          (a, b) =>
            b[1] - a[1]
        )

        .map(
          ([name, value]) => ({

            name,

            value,

          })
        );

    }, [
      filteredProducts,
    ]);


  // ==========================================================
  // TOP PRODUCTS
  // ==========================================================

  const topProducts =
    useMemo(() => {

      return [...filteredProducts]

        .sort(
          (a, b) =>
            num(
              b.forecast_30_day
            ) -
            num(
              a.forecast_30_day
            )
        )

        .slice(0, 5);

    }, [
      filteredProducts,
    ]);


  // ==========================================================
  // METRICS
  // ==========================================================

  const totalInventory =
    filteredProducts.reduce(
      (sum, product) =>
        sum +
        num(
          product.current_inventory
        ),
      0
    );


  const totalDemand =
    filteredProducts.reduce(
      (sum, product) =>
        sum +
        num(
          product.forecast_30_day
        ),
      0
    );


  const criticalCount =
    filteredProducts.filter(
      (product) =>
        String(
          product.stockout_risk ||
          ""
        ).toLowerCase() ===
        "critical"
    ).length;


  const highRiskCount =
    filteredProducts.filter(
      (product) =>
        String(
          product.stockout_risk ||
          ""
        ).toLowerCase() ===
        "high"
    ).length;


  // ==========================================================
  // PIE COLORS
  // ==========================================================

  const riskColors = {

    Critical:
      "#ef4444",

    High:
      "#f97316",

    Medium:
      "#eab308",

    Low:
      "#22c55e",

  };


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="analytics-dashboard">


      {/* ==================================================== */}
      {/* HEADER */}
      {/* ==================================================== */}

      <div className="analytics-header">

        <div>

          <h2>
            Analytics & Reports
          </h2>

          <p>
            AI-powered inventory analytics and demand intelligence
          </p>

        </div>


        <div className="analytics-controls">


          {/* SEARCH */}

          <div className="analytics-search">

            <Search
              size={15}
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


          {/* CATEGORY */}

          <select
            value={
              category
            }
            onChange={
              (event) =>
                setCategory(
                  event.target.value
                )
            }
          >

            {categories.map(
              (item) => (

                <option
                  key={item}
                  value={item}
                >

                  {item}

                </option>

              )
            )}

          </select>


        </div>

      </div>


      {/* ==================================================== */}
      {/* KPI CARDS */}
      {/* ==================================================== */}

      <div className="analytics-kpis">


        <div className="analytics-kpi">

          <div className="analytics-kpi-icon">

            <Package
              size={20}
            />

          </div>


          <div>

            <span>
              Products Analyzed
            </span>

            <strong>
              {filteredProducts.length}
            </strong>

          </div>

        </div>


        <div className="analytics-kpi">

          <div className="analytics-kpi-icon">

            <Boxes
              size={20}
            />

          </div>


          <div>

            <span>
              Current Inventory
            </span>

            <strong>
              {totalInventory.toLocaleString()}
            </strong>

          </div>

        </div>


        <div className="analytics-kpi">

          <div className="analytics-kpi-icon">

            <TrendingUp
              size={20}
            />

          </div>


          <div>

            <span>
              Predicted 30-Day Demand
            </span>

            <strong>
              {totalDemand.toLocaleString()}
            </strong>

          </div>

        </div>


        <div className="analytics-kpi">

          <div className="analytics-kpi-icon warning">

            <AlertTriangle
              size={20}
            />

          </div>


          <div>

            <span>
              High/Critical Risk
            </span>

            <strong>
              {criticalCount + highRiskCount}
            </strong>

          </div>

        </div>


      </div>


      {/* ==================================================== */}
      {/* CHART ROW 1 */}
      {/* ==================================================== */}

      <div className="analytics-chart-grid">


        {/* TOP DEMAND */}

        <section className="analytics-card large">

          <div className="analytics-card-header">

            <div>

              <h3>
                Top Products by Predicted Demand
              </h3>

              <p>
                Highest expected demand over the next 30 days
              </p>

            </div>


            <BarChart3
              size={18}
            />

          </div>


          <div className="analytics-chart">

            <ResponsiveContainer
              width="100%"
              height={330}
            >

              <BarChart
                data={
                  demandData
                }
                layout="vertical"
                margin={{
                  top: 5,
                  right: 25,
                  left: 25,
                  bottom: 5,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  type="number"
                />

                <YAxis
                  type="category"
                  dataKey="product"
                  width={100}
                  tick={{
                    fontSize: 9,
                  }}
                />

                <Tooltip />

                <Bar
                  dataKey="demand"
                  name="Predicted Demand"
                  fill="#2563eb"
                  radius={[
                    0,
                    5,
                    5,
                    0,
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </section>


        {/* STOCKOUT PIE */}

        <section className="analytics-card">

          <div className="analytics-card-header">

            <div>

              <h3>
                Stockout Risk
              </h3>

              <p>
                Inventory risk distribution
              </p>

            </div>


            <AlertTriangle
              size={18}
            />

          </div>


          <div className="analytics-pie">

            <ResponsiveContainer
              width="100%"
              height={250}
            >

              <PieChart>

                <Pie
                  data={
                    stockoutData
                  }
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={85}
                  innerRadius={48}
                  paddingAngle={3}
                >

                  {stockoutData.map(
                    (entry) => (

                      <Cell
                        key={
                          entry.name
                        }
                        fill={
                          riskColors[
                            entry.name
                          ]
                        }
                      />

                    )
                  )}

                </Pie>

                <Tooltip />

                <Legend
                  wrapperStyle={{
                    fontSize: "9px",
                  }}
                />

              </PieChart>

            </ResponsiveContainer>

          </div>

        </section>


      </div>


      {/* ==================================================== */}
      {/* CHART ROW 2 */}
      {/* ==================================================== */}

      <div className="analytics-chart-grid">


        {/* INVENTORY VS DEMAND */}

        <section className="analytics-card large">

          <div className="analytics-card-header">

            <div>

              <h3>
                Inventory vs Predicted Demand
              </h3>

              <p>
                Identify products where demand may exceed available stock
              </p>

            </div>


            <TrendingUp
              size={18}
            />

          </div>


          <div className="analytics-chart">

            <ResponsiveContainer
              width="100%"
              height={330}
            >

              <BarChart
                data={
                  inventoryDemandData
                }
                margin={{
                  top: 10,
                  right: 20,
                  left: 0,
                  bottom: 60,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="product"
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  height={75}
                  tick={{
                    fontSize: 8,
                  }}
                />

                <YAxis />

                <Tooltip />

                <Legend
                  wrapperStyle={{
                    fontSize: "9px",
                  }}
                />

                <Bar
                  dataKey="inventory"
                  name="Current Inventory"
                  fill="#64748b"
                  radius={[
                    4,
                    4,
                    0,
                    0,
                  ]}
                />

                <Bar
                  dataKey="demand"
                  name="30-Day Demand"
                  fill="#2563eb"
                  radius={[
                    4,
                    4,
                    0,
                    0,
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </section>


        {/* AI DECISIONS */}

        <section className="analytics-card">

          <div className="analytics-card-header">

            <div>

              <h3>
                AI Decisions
              </h3>

              <p>
                Recommended inventory actions
              </p>

            </div>


            <Boxes
              size={18}
            />

          </div>


          <div className="decision-chart">

            <ResponsiveContainer
              width="100%"
              height={260}
            >

              <PieChart>

                <Pie
                  data={
                    decisionData
                  }
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={88}
                >

                  {decisionData.map(
                    (
                      entry,
                      index
                    ) => (

                      <Cell
                        key={
                          entry.name
                        }
                        fill={
                          [
                            "#2563eb",
                            "#f97316",
                            "#22c55e",
                            "#ef4444",
                            "#8b5cf6",
                          ][
                            index %
                            5
                          ]
                        }
                      />

                    )
                  )}

                </Pie>

                <Tooltip />

                <Legend
                  wrapperStyle={{
                    fontSize: "9px",
                  }}
                />

              </PieChart>

            </ResponsiveContainer>

          </div>

        </section>


      </div>


      {/* ==================================================== */}
      {/* TOP PRODUCTS TABLE */}
      {/* ==================================================== */}

      <section className="analytics-card">

        <div className="analytics-card-header">

          <div>

            <h3>
              Highest-Demand Products
            </h3>

            <p>
              Products requiring the closest attention
            </p>

          </div>

        </div>


        <div className="analytics-table-wrapper">

          <table>

            <thead>

              <tr>

                <th>
                  Rank
                </th>

                <th>
                  Product
                </th>

                <th>
                  Category
                </th>

                <th>
                  Inventory
                </th>

                <th>
                  30-Day Demand
                </th>

                <th>
                  Stockout Risk
                </th>

                <th>
                  AI Decision
                </th>

              </tr>

            </thead>


            <tbody>

              {topProducts.map(
                (
                  product,
                  index
                ) => (

                  <tr
                    key={
                      product.product_id ??
                      product.product_name
                    }
                  >

                    <td>

                      <span className="rank">

                        #
                        {index + 1}

                      </span>

                    </td>


                    <td>

                      <strong>
                        {
                          product.product_name
                        }
                      </strong>

                    </td>


                    <td>
                      {
                        product.category ||
                        "—"
                      }
                    </td>


                    <td>

                      {num(
                        product.current_inventory
                      ).toLocaleString()}

                    </td>


                    <td>

                      <strong>

                        {num(
                          product.forecast_30_day
                        ).toLocaleString()}

                      </strong>

                    </td>


                    <td>

                      <span
                        className={
                          `analytics-risk ${
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

                      <span className="analytics-decision">

                        {
                          product.ai_decision ||
                          "Monitor"
                        }

                      </span>

                    </td>

                  </tr>

                )
              )}


              {topProducts.length === 0 && (

                <tr>

                  <td
                    colSpan="7"
                    className="empty-row"
                  >

                    No products match the current filters.

                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </section>


    </div>

  );

}


export default AnalyticsDashboard;