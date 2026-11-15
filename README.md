# Machine Learning on Databricks

Databricks Academy ML courses, set up to be **edited in VS Code and executed on Azure Databricks
serverless compute**. Clone it, run one script, and the notebooks run in your own workspace.

| Week | Course | Notes |
|------|--------|-------|
| [week1](week1/) | *Data Preparation for Machine Learning* (v4.0.0): exploring data, imputation, encoding, feature engineering in Unity Catalog | [NOTES](week1/NOTES.md) |
| [week2](week2/) | *Machine Learning Model Development* (v3.0.2): MLflow tracking, Optuna, Genie Code | [NOTES](week2/NOTES.md) |
| [week3](week3/) | *Machine Learning Model Deployment* (v2.3.2): batch, pipeline, real-time | [NOTES](week3/NOTES.md) |

---

## Quick start

**Prerequisites**
- Azure Databricks workspace with **Unity Catalog** and **serverless compute** (Premium tier)
- Linux, macOS or WSL with `bash`, `curl`, `unzip`, `python3`
- VS Code with the **Databricks** extension (on WSL: install it *in WSL*)
- These free **Databricks Marketplace** datasets added to the workspace (Marketplace → search → *Get instant access*):

  | Marketplace listing | Shared catalog name | Used by |
  |---|---|---|
  | Telco customer churn | `databricks_telco_customer_dataset` | week1 all, week2 1.4 / 2.3 / 3.2, week3 all |
  | Diabetes health indicators | `databricks_diabetes_health_indicators_dataset` | week1 2.6 / 3.2, week2 1.3 / 2.2, week3 4.5 |
  | California housing | `databricks_california_housing_data` | week2 1.2a |
  | Bank loan modelling | `databricks_bank_loan_modelling_dataset` | week2 3.3 |

**Setup**

```bash
git clone https://github.com/saquibherman/databricks-ml-learning.git
cd databricks-ml-learning
./setup.sh
```

`setup.sh` is safe to re-run. It:
1. installs the Databricks CLI and `uv` into `~/.local/bin` if missing (no sudo);
2. logs in to your workspace (OAuth, profile `azure-ml`), asking for the workspace URL once;
3. creates `.venv` (Python 3.12, matching serverless environment v5) with Databricks Connect and MLflow;
4. creates `<default catalog>.ops.meta`, schema `ml_deployment` and volume `working_dir`, filled with
   **your** username and the datasets it finds;
5. optionally creates a 90-day personal access token profile `azure-ml-pat` for local runs, and writes `.env`;
6. syncs the course to `/Workspace/Users/<you>/.bundle/ml-deployment-course/dev/files`.

**Run a notebook**
- Open the folder in VS Code → **Python: Select Interpreter** → `.venv`.
- Right-click a notebook → **Run File as Workflow**. It runs on serverless and streams cell output back.
- Or open the synced notebook in the Databricks UI and run cell by cell (pick **Environment version 5**
  if prompted).

---

## Status (tested as serverless jobs)

| Notebook | Result |
|---|---|
| week1 1.2 Demo: Load and Explore Data | ✅ |
| week1 2.5 Demo: Data Imputation and Transformation Pipeline | ✅ |
| week1 2.6 Demo: Build a Feature Engineering Pipeline | ✅ |
| week1 3.2 Demo: Using Feature Engineering in Unity Catalog | ✅ |
| week2 1.2a Demo: Supervised Learning | ✅ |
| week2 1.2b Demo: Unsupervised Learning | ✅ |
| week2 1.3 Demo: Model Tracking with MLflow | ✅ |
| week2 2.2 Demo: Hyperparameter Tuning with Optuna | ✅ |
| week2 3.2 Demo: Model Development with Genie Code | ✅ |
| week3 2.2 Demo: Batch Deployment | ✅ |
| week3 3.2 Demo: Pipeline Deployment | ✅ |
| week3 4.3 / 4.4 Demos: Model Serving | ⚠️ Blocked in the test workspace: endpoint container build could not download packages (see [Troubleshooting](#troubleshooting)) |

Labs contain `<FILL_IN>` exercises and are not expected to run unmodified.

---

## Repository layout

```
.
├── setup.sh              # One-shot setup (tools, login, .venv, UC bootstrap, .env, sync)
├── databricks.yml        # Databricks Asset Bundle: syncs the repo to the workspace
├── .env.example          # Template for .env (setup.sh fills it in)
├── .vscode/settings.json # .venv interpreter, notebook working dir, Databricks cell markers
├── scripts/
│   └── set_serverless_env.py   # Pin notebooks to serverless environment v5
├── week1/                # Data Preparation for Machine Learning
│   ├── NOTES.md
│   ├── AGENDA.ipynb
│   ├── Includes/         # Classroom setup scripts, %run by every notebook
│   ├── M01_Managing_and_Exploring_Data/
│   ├── M02_Data_Preparation_and_Feature_Engineering/
│   └── M03_Feature_Engineering_in_Unity_Catalog/
├── week2/                # Machine Learning Model Development
│   ├── NOTES.md, AGENDA.ipynb, Includes/
│   ├── M01_Model_Development_Workflow/
│   ├── M02_Hyperparameter_Tuning/
│   └── M03_Agentic_Machine_Learning/
└── week3/                # Machine Learning Model Deployment
    ├── NOTES.md, AGENDA.ipynb, Includes/
    ├── M01_Model_Deployment_Fundamentals/
    ├── M02_Batch_Deployment/
    ├── M03_Pipeline_Deployment/
    └── M04_Real-time_Deployment_and_Online_Stores/
```

---

## How the course was adapted to a regular workspace

The Academy notebooks expect a prepared lab workspace. These changes make them run in your own:

| Change | Where | Why |
|---|---|---|
| `ops.meta` settings table | created by `setup.sh` | `DBAcademyHelper` (`DA`) reads catalog, schema, username and dataset paths from it |
| Serverless environment in notebook metadata (week1: v6, week2/3: v5) | all `.ipynb` (`scripts/set_serverless_env.py`) | Without it, serverless used environment v1 (Python 3.10) and `%pip install mlflow==3.12.0` ran for 25+ minutes |
| `restartPython()` only on Databricks | `week*/Includes/_common.py` | `dbutils.library` does not exist over Databricks Connect |
| `dbacademy.` catalog → `DA.catalog_name` | week3 4.3 demo | The `dbacademy` catalog only exists in Academy labs |
| `/Volumes/dbacademy_*` → Marketplace share paths | week2 `Classroom-Setup-1.1a.py`, `-3.2.py` | Marketplace shares have different catalog names |
| `.py` source notebooks → `.ipynb`, underscores in names | week1, week2 | Same layout as week3; converted with the workspace's own exporter |

### Adding a new week

1. Unzip the Academy download into `weekN/` without its top-level folder.
2. Rename files and folders to underscores and update the `$./...` links in `AGENDA`.
   If the zip nests the course in a subfolder (as week1's does), copy that subfolder's contents.
3. Convert notebooks to `.ipynb` through the workspace:
   `databricks workspace import <tmp>/<nb> --file <nb>.py --format SOURCE --language PYTHON`, then
   `databricks workspace export <tmp>/<nb> --format JUPYTER --file <nb>.ipynb`.
   Keep `Includes/*.py` as `.py` (they are `%run` targets).
4. `python3 scripts/set_serverless_env.py weekN --version <V>` (the version the course's AGENDA asks for), add the `_common.py` guard, fix hard-coded paths,
   and add any new dataset rows to `setup.sh`.

---

## Where to run what

| Notebook content | Local (VS Code + Databricks Connect) | Databricks (Workflow / UI) |
|---|:-:|:-:|
| Spark data prep, sklearn training | ✅ | ✅ |
| `mlflow.log_model` + register in Unity Catalog | ✅ | ✅ |
| `FeatureEngineeringClient.create_table` / lookups | ✅ (PAT profile) | ✅ |
| `fe.log_model` registration, `fe.score_batch` | ❌ | ✅ |
| Lakeflow pipelines, Model Serving, online stores | ❌ | ✅ |

Rule of thumb: **edit and explore locally, run full demos and labs on Databricks.**

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Setup cell runs forever, pip downloads many `urllib3` versions | Serverless environment v1 | Environment version 5 (already set in notebook metadata) |
| `Metadata table <catalog>.ops.meta not found` | Workspace not bootstrapped | Run `./setup.sh` |
| `PATH_NOT_FOUND` on `/Volumes/databricks_...` | Marketplace dataset missing | Add it from Marketplace, re-run `./setup.sh` |
| Serving endpoint: `Container build failed. Cause: user_pip_resolution`, log shows `No matching distribution found for mlflow (from versions: none)` | The endpoint build cannot download packages: workspace serverless network policy / egress control or NCC | Ask an account admin to allow PyPI for serverless (Account Console → Security → Networking → Network policies), or contact Databricks support |
| VS Code: *Databricks Connect disabled* | venv has no `pip` | `uv pip install --python .venv pip` (setup.sh does this) |
| `ModuleNotFoundError: nbformat` on `%run` | Needed by the extension's `%run` support | `uv pip install --python .venv nbformat` (setup.sh does this) |
| `%run ../Includes/...` not found locally | Jupyter cwd was the repo root | `jupyter.notebookFileRoot` in `.vscode/settings.json` (included) |
| `ValueError: cluster_id is required` | `restartPython()` over Databricks Connect | Guard in `_common.py` (included) |
| `Could not find experiment with ID None` | No notebook experiment for local runs | `MLFLOW_EXPERIMENT_NAME` in `.env` (setup.sh writes it) |
| Feature Engineering `401 Credential was not sent` | Library sends only static tokens; OAuth profiles have none | Use the PAT profile for local runs (setup.sh offers to create it) |
| `This model was packaged by Databricks Feature Store and can only be registered on a Databricks cluster` | MLflow restriction | Run that notebook on Databricks |

---

## Credits

Course notebooks and setup scripts in `week1/`–`week3/` are from **Databricks Academy**
(© 2026 Databricks, Inc. All rights reserved), with the adaptations listed above. Notes, `setup.sh`,
configuration and scripts are my own.
