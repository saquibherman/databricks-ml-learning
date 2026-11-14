# Machine Learning on Databricks

My notes and working setup while learning ML on Databricks. Each week has its own folder.
Code is edited in **VS Code (WSL)** and executed on **Azure Databricks serverless compute**.

> **Course material is not included.** The Databricks Academy notebooks are copyrighted by
> Databricks, Inc., so this repo only publishes my notes, configuration and helper scripts.
> To follow along, get the course from [Databricks Academy](https://www.databricks.com/learn/training)
> and copy its files into the matching `weekN/` folder (they are git-ignored).

| Week | Topic | Notes | Status |
|------|-------|-------|--------|
| week1 | Databricks Academy: *Machine Learning Model Deployment* (batch, pipeline, real-time) | [week1/NOTES.md](week1/NOTES.md) | Environment set up; M02 batch demo runs end to end |

---

## Repository layout

```
Machine_Learning/
├── databricks.yml        # Databricks Asset Bundle: syncs this repo to the workspace
├── .env.example          # Template for local env vars (copy to .env)
├── .vscode/settings.json # Interpreter, notebook working dir, Databricks cell markers
├── scripts/
│   └── set_serverless_env.py  # Pin notebooks to serverless environment v5
└── week1/
    ├── NOTES.md                           # My notes (published)
    │   --- course files below: local only, git-ignored ---
    ├── AGENDA.ipynb                       # Course overview
    ├── Includes/                          # Classroom setup scripts (%run by every notebook)
    │   ├── _common.py                     # DBAcademyHelper (`DA` object), pip installs
    │   └── Classroom-Setup-*.py           # Per-lesson setup
    ├── M01_Model_Deployment_Fundamentals/ # Lectures: deployment strategies, MLflow
    ├── M02_Batch_Deployment/              # Lecture, demo, lab: batch inference + Feature Store
    ├── M03_Pipeline_Deployment/           # Lecture, demo: Lakeflow (DLT) inference pipeline
    └── M04_Real-time_Deployment_and_Online_Stores/  # Model Serving, online stores, custom models
```

---

## Week 1: Machine Learning Model Deployment

### Course modules

| # | Module | Content |
|---|--------|---------|
| 1 | Model Deployment Fundamentals | Batch vs. streaming vs. real-time; deploying with MLflow |
| 2 | Batch Deployment | Train and register a model in Unity Catalog, batch scoring with `spark_udf`, Feature Store tables, `fe.score_batch`, writing/optimizing an inference table |
| 3 | Pipeline Deployment | Inference as a Lakeflow Declarative Pipeline |
| 4 | Real-time Deployment and Online Stores | Model Serving endpoints, online feature stores, custom pyfunc models |

### Progress

- [x] Databricks CLI installed and authenticated against the Azure workspace
- [x] Unity Catalog objects created for the course (see [Workspace setup](#workspace-setup))
- [x] VS Code Databricks extension and local `.venv` (Databricks Connect) configured
- [x] **2.2 Demo: Batch Deployment** completed successfully as a serverless job
- [ ] 2.3 Lab: Batch Deployment
- [ ] 3.2 Demo: Pipeline Deployment
- [ ] 4.3 / 4.4 Demos and 4.5 Lab: Model Serving (4.5 needs the `cdc_diabetes` Marketplace dataset)

### What I learned this week

- **Batch inference** is the most common deployment pattern: load a registered model as a Spark UDF
  (`mlflow.pyfunc.spark_udf`) and score a whole table in parallel.
- **Unity Catalog model registry**: models use 3-level names (`catalog.schema.model`) and are
  promoted with aliases like `@champion` rather than the old stage names.
- **Feature Store**: `FeatureEngineeringClient.create_training_set` joins features by primary key
  at training time; `fe.log_model` packages the lookup logic with the model, so `fe.score_batch`
  only needs the keys at inference time.
- **Serverless environment versions matter**: notebooks without an explicit version fell back to
  environment v1 (Python 3.10), where pip dependency resolution for `mlflow==3.12.0` never finished.

---

## Setup

### 1. Prerequisites
- Azure Databricks workspace (Premium, Unity Catalog enabled, serverless compute)
- WSL Ubuntu + VS Code with the **Databricks** extension installed *in WSL*
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) and [uv](https://docs.astral.sh/uv/)

### 2. Authenticate

```bash
# OAuth login: used by the CLI, the bundle and the VS Code extension
databricks auth login --host https://<workspace>.azuredatabricks.net --profile azure-ml
```

For **local** notebook runs, also create a personal access token profile (the Feature
Engineering client cannot use OAuth, see [Troubleshooting](#troubleshooting)):

```bash
databricks tokens create --comment vscode-ml-course --lifetime-seconds 7776000 -p azure-ml
# add to ~/.databrickscfg:
# [azure-ml-pat]
# host  = https://<workspace>.azuredatabricks.net
# token = <token_value>
```

### 3. Local Python environment (editor support + Databricks Connect)

```bash
uv venv .venv --python 3.12          # 3.12 matches serverless environment v5
uv pip install --python .venv pip nbformat ipykernel \
    databricks-connect "mlflow==3.12.0" databricks-sdk databricks-feature-engineering \
    scikit-learn pandas
cp .env.example .env                 # then fill in your email
```

In VS Code: **Python: Select Interpreter** → `.venv`, then **Refresh** in the Databricks panel's
*Python environment* section.

### 4. Workspace setup

The course's `DBAcademyHelper` reads its configuration from a `<default_catalog>.ops.meta`
key/value table, which Databricks Academy lab environments provide. On a personal workspace it
has to be created once:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.ops;
CREATE SCHEMA IF NOT EXISTS workspace.ml_deployment;
CREATE VOLUME IF NOT EXISTS workspace.ml_deployment.working_dir;

CREATE OR REPLACE TABLE workspace.ops.meta (key STRING, value STRING);
INSERT INTO workspace.ops.meta VALUES
  ('username',             '<your-email>'),
  ('catalog_name',         'workspace'),
  ('schema_name',          'ml_deployment'),
  ('pseudonym',            '<first last>'),            -- used in serving endpoint names
  ('paths.working_dir',    '/Volumes/workspace/ml_deployment/working_dir'),
  ('paths.datasets.telco', '/Volumes/databricks_telco_customer_dataset/v01'),
  ('datasets.telco',       'databricks_telco_customer_dataset');
```

`workspace` is the workspace's default catalog (`SELECT current_catalog()`). The Telco churn
dataset comes from **Databricks Marketplace** as the shared catalog
`databricks_telco_customer_dataset` (volume `v01.telco`).

### 5. Sync and run

```bash
databricks bundle validate
databricks bundle sync            # uploads to /Workspace/Users/<you>/.bundle/ml-deployment-course/dev/files
```

Or let the VS Code extension sync automatically, then run a notebook with
**right-click → Run File as Workflow**.

---

## Where to run what

| Notebook content | Local (VS Code + Databricks Connect) | Databricks (Workflow / web UI) |
|---|:-:|:-:|
| Spark data prep, sklearn training | ✅ | ✅ |
| `mlflow.log_model` + register in Unity Catalog | ✅ | ✅ |
| `FeatureEngineeringClient.create_table` / lookups | ✅ (PAT profile) | ✅ |
| `fe.log_model` registration, `fe.score_batch` | ❌ | ✅ |
| Lakeflow pipelines (M03), Model Serving and online stores (M04) | ❌ | ✅ |

Rule of thumb: **edit and explore locally, run full demos and labs on Databricks.**

---

## Changes to apply to the course files

After copying the course into `week1/`, apply these two changes locally:

| File | Change | Why |
|------|--------|-----|
| All `week1/**/*.ipynb` | `python scripts/set_serverless_env.py week1` (sets `environmentMetadata.environment_version = "5"`) | Without it, serverless defaulted to environment v1 (Python 3.10) and `%pip install` hung for 25+ minutes |
| `week1/Includes/_common.py` | In the first cell, replace the `# MAGIC dbutils.library.restartPython()` line with a separate Python cell (below) | `dbutils.library` is unavailable over Databricks Connect; behaviour on Databricks is unchanged |

```python
# COMMAND ----------

import os
if "DATABRICKS_RUNTIME_VERSION" in os.environ:   # only on Databricks compute
    dbutils.library.restartPython()
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Setup cell runs forever, pip downloads many `urllib3` versions | Serverless environment v1 (Python 3.10) | Use environment version 5 (notebook metadata or Environment side panel) |
| `Metadata table workspace.ops.meta not found` | Not an Academy lab workspace | Create it, see [Workspace setup](#workspace-setup) |
| VS Code status bar: *Databricks Connect disabled* | uv-created venv has no `pip`; the extension runs `pip list` | `uv pip install --python .venv pip` |
| `ModuleNotFoundError: nbformat` on `%run` | Needed by the extension's `%run` support | `uv pip install --python .venv nbformat` |
| `%run ../Includes/...` path not found locally | Jupyter cwd was the repo root | `"jupyter.notebookFileRoot": "${fileDirname}"` in `.vscode/settings.json` |
| `ValueError: cluster_id is required` | `dbutils.library.restartPython()` over Databricks Connect | Guard added in `_common.py` |
| `Could not find experiment with ID None` | No notebook experiment for local runs | `MLFLOW_EXPERIMENT_NAME` in `.env` |
| Feature Engineering `401 Credential was not sent` | Library sends only static tokens; OAuth profiles have none | Use a PAT profile for local runs (`DATABRICKS_CONFIG_PROFILE` in `.env`) |
| `This model was packaged by Databricks Feature Store and can only be registered on a Databricks cluster` | Hard MLflow restriction | Run that notebook on Databricks |

---

## Credits

The course this repo follows is **Databricks Academy, *Machine Learning Model Deployment***
(v2.3.2), © 2026 Databricks, Inc. All rights reserved. Its notebooks and setup scripts are not
redistributed here. Notes, configuration and scripts in this repo are my own.
