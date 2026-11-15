# Week 3 Notes: Machine Learning Model Deployment

My own notes from the Databricks Academy course *Machine Learning Model Deployment*.

## Deployment strategies

| Strategy | Latency | Typical use | On Databricks |
|---|---|---|---|
| Batch | minutes–hours | Nightly churn scores, reports | Jobs + `spark_udf` / `fe.score_batch` |
| Streaming / pipeline | seconds–minutes | Continuous scoring of new rows | Lakeflow Declarative Pipelines |
| Real-time | milliseconds | Per-request predictions in apps | Model Serving endpoints + online stores |

Batch is the most common and cheapest; pick real-time only when a caller needs an answer now.

## Batch deployment (M02)

- Register models in **Unity Catalog** with 3-level names: `catalog.schema.model`.
  Point MLflow at it with `mlflow.set_registry_uri("databricks-uc")`.
- Promote with **aliases** (`@champion`, `@challenger`) instead of the old stages;
  load with `models:/catalog.schema.model@champion`.
- Score a whole table in parallel by wrapping the model as a Spark UDF:
  `mlflow.pyfunc.spark_udf(spark, model_uri)`.
- **Feature Store** (`FeatureEngineeringClient`):
  - `create_table` with a primary key (`customerID`) stores features once for reuse.
  - `create_training_set` + `FeatureLookup` joins features at training time.
  - `fe.log_model` packages the lookup logic with the model, so `fe.score_batch`
    only needs the keys at inference time; no training/serving skew.
- Writing results: append predictions to a Delta inference table, then
  `OPTIMIZE` / `ANALYZE TABLE ... COMPUTE STATISTICS`, or enable predictive optimization.

## Platform lessons from setting this up

- **Serverless environment version matters.** With no version set, notebooks ran on
  environment v1 (Python 3.10) and `%pip install` backtracked for 25+ minutes.
  Environment v5 (Python 3.12) finished the whole demo in about 4 minutes.
  Fix: [`scripts/set_serverless_env.py`](../scripts/set_serverless_env.py).
- **Databricks Connect is not a full notebook runtime.** `dbutils.library`, notebook
  experiments and Feature Store model registration only exist on Databricks compute.
- **OAuth vs. tokens.** The Feature Engineering client sends only static tokens, so local
  runs need a personal access token profile; the CLI and bundles are fine with OAuth.
