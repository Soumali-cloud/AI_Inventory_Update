import { useMemo, useState } from "react";

import {
  AlertTriangle,
  Calculator,
  CheckCircle2,
  Package,
  TrendingDown,
  TrendingUp,
  X,
} from "lucide-react";


function InventorySimulator({
  product,
  onClose,
}) {

  const [demandChange, setDemandChange] =
    useState(20);

  const [leadTime, setLeadTime] =
    useState(
      Number(
        product?.lead_time_days || 7
      )
    );

  const [safetyBuffer, setSafetyBuffer] =
    useState(10);


  // ==========================================================
  // SIMULATION
  // ==========================================================

  const simulation = useMemo(() => {

    if (!product) {
      return null;
    }


    const currentInventory =
      Number(
        product.current_inventory || 0
      );


    const baseDailyDemand =
      Number(
        product.forecast_30_day || 0
      ) / 30;


    const scenarioDailyDemand =
      baseDailyDemand *
      (1 + demandChange / 100);


    const leadTimeDemand =
      scenarioDailyDemand *
      leadTime;


    const baseSafetyStock =
      Math.max(
        scenarioDailyDemand * 3,
        Number(
          product.safety_stock || 0
        )
      );


    const scenarioSafetyStock =
      baseSafetyStock *
      (1 + safetyBuffer / 100);


    const requiredInventory =
      leadTimeDemand +
      scenarioSafetyStock;


    const inventoryGap =
      requiredInventory -
      currentInventory;


    const recommendedReorder =
      Math.max(
        0,
        Math.ceil(
          inventoryGap
        )
      );


    const projectedDays =
      scenarioDailyDemand > 0
        ? currentInventory /
          scenarioDailyDemand
        : 999;


    let stockoutRisk = "Low";

    if (
      projectedDays <= 3 ||
      currentInventory <= 0
    ) {

      stockoutRisk = "Critical";

    } else if (
      projectedDays <= 7
    ) {

      stockoutRisk = "High";

    } else if (
      projectedDays <= 14
    ) {

      stockoutRisk = "Medium";

    }


    let action = "HOLD";

    if (
      stockoutRisk === "Critical"
      ||
      stockoutRisk === "High"
    ) {

      action = "BUY NOW";

    } else if (
      recommendedReorder > 0
    ) {

      action = "BUY";

    } else if (
      currentInventory >
      requiredInventory * 1.5
    ) {

      action = "REDUCE";

    } else {

      action = "HOLD";

    }


    const unitPrice =
      Number(
        product.price || 0
      );


    const purchaseValue =
      recommendedReorder *
      unitPrice;


    return {

      currentInventory,

      baseDailyDemand,

      scenarioDailyDemand,

      leadTimeDemand,

      scenarioSafetyStock,

      requiredInventory,

      inventoryGap,

      recommendedReorder,

      projectedDays,

      stockoutRisk,

      action,

      purchaseValue,

    };

  }, [
    product,
    demandChange,
    leadTime,
    safetyBuffer,
  ]);


  if (!product || !simulation) {

    return null;

  }


  return (

    <div className="simulator-overlay">

      <div className="simulator-modal">

        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div className="simulator-header">

          <div>

            <div className="simulator-title">

              <div className="simulator-icon">

                <Calculator
                  size={20}
                />

              </div>

              <div>

                <h2>
                  What-If Inventory Simulator
                </h2>

                <p>
                  Simulate demand and supply scenarios
                </p>

              </div>

            </div>

          </div>


          <button
            className="close-button"
            onClick={onClose}
          >

            <X
              size={20}
            />

          </button>

        </div>


        {/* ================================================== */}
        {/* PRODUCT */}
        {/* ================================================== */}

        <div className="simulator-product">

          <div className="simulator-product-icon">

            <Package
              size={23}
            />

          </div>

          <div>

            <strong>
              {product.product_name}
            </strong>

            <span>
              {product.category}
            </span>

          </div>

        </div>


        {/* ================================================== */}
        {/* CONTROLS */}
        {/* ================================================== */}

        <div className="simulator-body">

          <div className="scenario-controls">

            <h3>
              Scenario Parameters
            </h3>


            {/* DEMAND */}

            <div className="control">

              <div className="control-label">

                <label>
                  Demand Change
                </label>

                <strong>
                  {demandChange > 0
                    ? "+"
                    : ""}
                  {demandChange}%
                </strong>

              </div>

              <input
                type="range"
                min="-50"
                max="100"
                step="5"
                value={demandChange}
                onChange={(event) =>
                  setDemandChange(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

              <div className="range-labels">

                <span>
                  -50%
                </span>

                <span>
                  0%
                </span>

                <span>
                  +100%
                </span>

              </div>

            </div>


            {/* LEAD TIME */}

            <div className="control">

              <div className="control-label">

                <label>
                  Supplier Lead Time
                </label>

                <strong>
                  {leadTime} days
                </strong>

              </div>

              <input
                type="range"
                min="1"
                max="30"
                step="1"
                value={leadTime}
                onChange={(event) =>
                  setLeadTime(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

              <div className="range-labels">

                <span>
                  1 day
                </span>

                <span>
                  15 days
                </span>

                <span>
                  30 days
                </span>

              </div>

            </div>


            {/* SAFETY BUFFER */}

            <div className="control">

              <div className="control-label">

                <label>
                  Safety Stock Buffer
                </label>

                <strong>
                  +{safetyBuffer}%
                </strong>

              </div>

              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={safetyBuffer}
                onChange={(event) =>
                  setSafetyBuffer(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

              <div className="range-labels">

                <span>
                  0%
                </span>

                <span>
                  50%
                </span>

                <span>
                  100%
                </span>

              </div>

            </div>


            {/* RESET */}

            <button
              className="reset-simulator"
              onClick={() => {

                setDemandChange(20);

                setLeadTime(
                  Number(
                    product.lead_time_days || 7
                  )
                );

                setSafetyBuffer(10);

              }}
            >
              Reset Scenario
            </button>

          </div>


          {/* ================================================= */}
          {/* RESULTS */}
          {/* ================================================= */}

          <div className="simulation-results">

            <h3>
              Simulated Result
            </h3>


            <div className="result-grid">


              {/* DAILY DEMAND */}

              <div className="result-card">

                <span>
                  Scenario Daily Demand
                </span>

                <strong>
                  {simulation.scenarioDailyDemand.toFixed(
                    1
                  )}
                </strong>

                <small>
                  units / day
                </small>

              </div>


              {/* LEAD TIME DEMAND */}

              <div className="result-card">

                <span>
                  Lead-Time Demand
                </span>

                <strong>
                  {Math.ceil(
                    simulation.leadTimeDemand
                  ).toLocaleString()}
                </strong>

                <small>
                  units
                </small>

              </div>


              {/* REQUIRED INVENTORY */}

              <div className="result-card">

                <span>
                  Required Inventory
                </span>

                <strong>
                  {Math.ceil(
                    simulation.requiredInventory
                  ).toLocaleString()}
                </strong>

                <small>
                  units
                </small>

              </div>


              {/* PROJECTED DAYS */}

              <div className="result-card">

                <span>
                  Inventory Coverage
                </span>

                <strong>
                  {simulation.projectedDays >= 999
                    ? "∞"
                    : simulation.projectedDays.toFixed(
                        1
                      )}
                </strong>

                <small>
                  days
                </small>

              </div>

            </div>


            {/* ================================================= */}
            {/* DECISION */}
            {/* ================================================= */}

            <div className="simulation-decision">

              <div className="decision-result">

                {simulation.action ===
                "BUY NOW" ? (

                  <div className="decision-icon critical">

                    <AlertTriangle
                      size={24}
                    />

                  </div>

                ) : simulation.action ===
                  "BUY" ? (

                  <div className="decision-icon buy">

                    <TrendingUp
                      size={24}
                    />

                  </div>

                ) : simulation.action ===
                  "REDUCE" ? (

                  <div className="decision-icon reduce">

                    <TrendingDown
                      size={24}
                    />

                  </div>

                ) : (

                  <div className="decision-icon hold">

                    <CheckCircle2
                      size={24}
                    />

                  </div>

                )}


                <div>

                  <span>
                    AI Scenario Recommendation
                  </span>

                  <strong>
                    {simulation.action}
                  </strong>

                </div>

              </div>


              <div className="decision-details">

                <div>

                  <span>
                    Stockout Risk
                  </span>

                  <strong
                    className={
                      "risk-" +
                      simulation.stockoutRisk.toLowerCase()
                    }
                  >
                    {simulation.stockoutRisk}
                  </strong>

                </div>


                <div>

                  <span>
                    Additional Units
                  </span>

                  <strong>
                    {simulation.recommendedReorder.toLocaleString()}
                  </strong>

                </div>


                <div>

                  <span>
                    Purchase Value
                  </span>

                  <strong>
                    ₹
                    {simulation.purchaseValue.toLocaleString(
                      "en-IN",
                      {
                        maximumFractionDigits: 0,
                      }
                    )}
                  </strong>

                </div>

              </div>

            </div>


            {/* ================================================= */}
            {/* EXPLANATION */}
            {/* ================================================= */}

            <div className="simulation-explanation">

              <strong>
                AI Explanation
              </strong>

              <p>

                With demand changing by{" "}

                <b>
                  {demandChange > 0
                    ? "+"
                    : ""}
                  {demandChange}%
                </b>

                and supplier lead time of{" "}

                <b>
                  {leadTime} days
                </b>

                , the system estimates{" "}

                <b>
                  {Math.ceil(
                    simulation.requiredInventory
                  ).toLocaleString()}
                </b>

                {" "}units of inventory are required.

                {" "}

                {simulation.recommendedReorder > 0

                  ? `The scenario creates an inventory gap of ${Math.ceil(
                      simulation.recommendedReorder
                    ).toLocaleString()} units, so additional replenishment is recommended.`

                  : "Current inventory is sufficient under this scenario."
                }

              </p>

            </div>

          </div>

        </div>

      </div>

    </div>

  );

}


export default InventorySimulator;