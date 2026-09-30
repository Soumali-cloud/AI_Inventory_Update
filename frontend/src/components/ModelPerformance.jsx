import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  Loader2,
  Target,
  TrendingUp,
} from "lucide-react";

import "./ModelPerformance.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function ModelPerformance() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadEvaluation();
  }, []);

  async function loadEvaluation() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_BASE_URL}/evaluation/all`
      );

      if (!response.ok) {
        const message = await response.text();

        throw new Error(
          message ||
            "Unable to load model evaluation."
        );
      }

      const data = await response.json();

      setModels(data.models || []);
    } catch (err) {
      console.error(
        "Model evaluation error:",
        err
      );

      setError(
        err.message ||
          "Unable to load model performance."
      );
    } finally {
      setLoading(false);
    }
  }

  const demandModel = useMemo(
    () =>
      models.find(
        (model) =>
          String(model.model)
            .toLowerCase()
            .includes("demand")
      ),
    [models]
  );

  const priceModel = useMemo(
    () =>
      models.find(
        (model) =>
          String(model.model)
            .toLowerCase()
            .includes("price")
      ),
    [models]
  );

  function number(value, decimals = 3) {
    const parsed = Number(value);

    if (!Number.isFinite(parsed)) {
      return "N/A";
    }

    return parsed.toFixed(decimals);
  }

  function percentage(value) {
    const parsed = Number(value);

    if (!Number.isFinite(parsed)) {
      return "N/A";
    }

    return `${parsed.toFixed(2)}%`;
  }

  function r2Quality(value) {
    const parsed = Number(value);

    if (!Number.isFinite(parsed)) {
      return "Unknown";
    }

    if (parsed >= 0.9) {
      return "Excellent";
    }

    if (parsed >= 0.75) {
      return "Strong";
    }

    if (parsed >= 0.6) {
      return "Moderate";
    }

    if (parsed >= 0.4) {
      return "Needs improvement";
    }

    return "Low";
  }

  function modelCard(model, type) {
    if (!model) {
      return (
        <div className="model-empty-card">
          <BrainCircuit size={28} />

          <h3>
            {type} Model
          </h3>

          <p>
            Evaluation data is not available.
          </p>
        </div>
      );
    }

    const r2 = Number(model.R2);

    return (
      <div className="model-card">

        <div className="model-card-header">

          <div className="model-icon">
            <BrainCircuit size={22} />
          </div>

          <div>
            <span>
              MACHINE LEARNING MODEL
            </span>

            <h2>
              {model.model}
            </h2>
          </div>

        </div>


        <div className="model-status">

          <CheckCircle2 size={16} />

          <span>
            Evaluation completed
          </span>

        </div>


        <div className="metric-grid">

          <div className="metric-card">
            <span>
              MAE
            </span>

            <strong>
              {number(model.MAE)}
            </strong>

            <small>
              Mean Absolute Error
            </small>
          </div>


          <div className="metric-card">
            <span>
              RMSE
            </span>

            <strong>
              {number(model.RMSE)}
            </strong>

            <small>
              Root Mean Square Error
            </small>
          </div>


          <div className="metric-card">
            <span>
              R² SCORE
            </span>

            <strong>
              {number(model.R2)}
            </strong>

            <small>
              {r2Quality(model.R2)}
            </small>
          </div>


          <div className="metric-card">
            <span>
              MAE %
            </span>

            <strong>
              {percentage(
                model.MAE_Percent
              )}
            </strong>

            <small>
              Relative error
            </small>
          </div>

        </div>


        <div className="model-details">

          <div>
            <span>
              Evaluation samples
            </span>

            <strong>
              {model.samples || "N/A"}
            </strong>
          </div>


          <div>
            <span>
              Features
            </span>

            <strong>
              {model.features || "N/A"}
            </strong>
          </div>


          <div>
            <span>
              Target
            </span>

            <strong>
              {model.target || "N/A"}
            </strong>
          </div>

        </div>


        <div className="r2-section">

          <div className="r2-header">

            <span>
              Model Fit
            </span>

            <strong>
              {number(model.R2, 2)}
            </strong>

          </div>

          <div className="r2-bar">

            <div
              className="r2-fill"
              style={{
                width: `${Math.max(
                  0,
                  Math.min(
                    Number.isFinite(r2)
                      ? r2 * 100
                      : 0,
                    100
                  )
                )}%`,
              }}
            />

          </div>

        </div>

      </div>
    );
  }


  if (loading) {
    return (
      <div className="model-loading">

        <Loader2
          size={34}
          className="model-spinner"
        />

        <h3>
          Loading Model Performance
        </h3>

        <p>
          Reading AI evaluation metrics...
        </p>

      </div>
    );
  }


  if (error) {
    return (
      <div className="model-error">

        <Activity size={28} />

        <div>

          <h3>
            Model Performance unavailable
          </h3>

          <p>
            {error}
          </p>

          <button
            onClick={loadEvaluation}
          >
            Retry
          </button>

        </div>

      </div>
    );
  }


  return (
    <div className="model-performance-page">

      <div className="model-page-header">

        <div>

          <div className="model-title">

            <Target size={30} />

            <h1>
              Model Performance
            </h1>

          </div>

          <p>
            Evaluation of the machine-learning
            models powering demand and price
            intelligence.
          </p>

        </div>


        <div className="evaluation-badge">

          <CheckCircle2 size={17} />

          Models Evaluated

        </div>

      </div>


      <div className="model-overview">

        <div className="overview-card">

          <div className="overview-icon">
            <BrainCircuit size={22} />
          </div>

          <div>

            <span>
              MODELS EVALUATED
            </span>

            <strong>
              {models.length}
            </strong>

          </div>

        </div>


        <div className="overview-card">

          <div className="overview-icon">
            <Activity size={22} />
          </div>

          <div>

            <span>
              DEMAND R²
            </span>

            <strong>
              {demandModel
                ? number(
                    demandModel.R2,
                    2
                  )
                : "N/A"}
            </strong>

          </div>

        </div>


        <div className="overview-card">

          <div className="overview-icon">
            <TrendingUp size={22} />
          </div>

          <div>

            <span>
              PRICE R²
            </span>

            <strong>
              {priceModel
                ? number(
                    priceModel.R2,
                    2
                  )
                : "N/A"}
            </strong>

          </div>

        </div>

      </div>


      <div className="model-cards">

        {modelCard(
          demandModel,
          "Demand"
        )}

        {modelCard(
          priceModel,
          "Price"
        )}

      </div>


      <div className="evaluation-explanation">

        <div className="explanation-icon">
          <BrainCircuit size={25} />
        </div>

        <div>

          <h3>
            Understanding the metrics
          </h3>

          <p>
            MAE measures the average prediction
            error, RMSE gives greater weight to
            larger errors, and R² indicates how
            well the model explains variation in
            the target. Lower MAE and RMSE are
            generally better, while a higher R²
            indicates stronger model fit.
          </p>

        </div>

      </div>

    </div>
  );
}

export default ModelPerformance;