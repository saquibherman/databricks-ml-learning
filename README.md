# Machine Learning on Databricks

Databricks Academy ML courses, set up to be **edited in VS Code and executed on Azure Databricks
serverless compute**. Clone it, run one script, and the notebooks run in your own workspace.

| Week | Course | Notes |
|------|--------|-------|
| [week1](week1/) | *Data Preparation for Machine Learning* (v4.0.0): exploring data, imputation, encoding, feature engineering in Unity Catalog | [NOTES](week1/NOTES.md) |
| [week2](week2/) | *Machine Learning Model Development* (v3.0.2): MLflow tracking, Optuna, Genie Code | [NOTES](week2/NOTES.md) |
| [week3](week3/) | *Machine Learning Model Deployment* (v2.3.2): batch, pipeline, real-time | [NOTES](week3/NOTES.md) |
| [week4](week4/) | *Machine Learning Operations* (v2.4.2): Lakeflow Jobs, MLOps architectures, CLI/API pipelines, monitoring | [NOTES](week4/NOTES.md) |

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
  | Diabetes health indicators | `databricks_diabetes_health_indicators_dataset` | week1 2.6 / 3.2, week2 1.3 / 2.2, week3 4.5, week4 3.3 / 3.4 |
  | California housing | `databricks_california_housing_data` | week2 1.2a |
  | Bank loan modelling | `databricks_bank_loan_modelling_dataset` | week2 3.3, week4 M01 / M02 |
  | Inference Dataset for Machine Learning Operations Associate Course | `databricks_inference_dataset_for_machine_learning_operations_associate_course` | week4 3.3 / 3.4 |

**Setup**

```bash
git clone https://github.com/saquibherman/databricks-ml-learning.git
cd databricks-ml-learning
./setup.sh
```

`setup.sh` is safe to re-run. It:
1. installs the Databricks CLI and `uv` into `~/.local/bin` if missing (no sudo);
2. logs in to your workspace (OAuth, profile `azure-ml`), asking for the workspace URL once, and writes
   it to the git-ignored `databricks.local.yml` (the VS Code extension needs it in the bundle);
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
| week4 1.3 Demo Pipeline (1.3a–e) | ✅ (run as one Lakeflow job) |
| week4 2.3 Demo Pipeline (2.3a–d) + 2.3 Demo (Databricks API) | ✅ no token file needed (see adaptations) |
| week4 2.4 Demo Pipeline (2.4a–c), incl. Model Serving endpoint | ✅ |
| week4 3.3 Demo: Data Profiling Dashboard | ✅ (first monitor refresh takes ~15 min) |
| week4 2.4 Demo / 2.5 Lab (Databricks CLI) | ➖ Hands-on in a cluster web terminal; the course wants a DBR 17.3 ML cluster |
| week3 4.3 / 4.4 Demos: Model Serving | ✅ (with `env_pack`, see adaptations) |

Labs contain `<FILL_IN>` exercises and are not expected to run unmodified.

---

## Repository layout

```
.
├── setup.sh              # One-shot setup (tools, login, .venv, UC bootstrap, .env, sync)
├── databricks.yml        # Databricks Asset Bundle: syncs the repo to the workspace
├── databricks.local.yml  # (git-ignored, written by setup.sh) your workspace host
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
├── week3/                # Machine Learning Model Deployment
│   ├── NOTES.md, AGENDA.ipynb, Includes/
│   ├── M01_Model_Deployment_Fundamentals/
│   ├── M02_Batch_Deployment/
│   ├── M03_Pipeline_Deployment/
│   └── M04_Real-time_Deployment_and_Online_Stores/
└── week4/                # Machine Learning Operations
    ├── NOTES.md, AGENDA.ipynb, Includes/
    ├── M01_Modern_MLOps/                       # + 1.3 / 1.4 job pipeline folders
    ├── M02_Architecting_MLOps_Solutions/       # + 2.3 / 2.4 / 2.5 pipeline folders, 0_Generate_Tokens
    └── M03_Implementation_and_Monitoring_MLOps_Solution/
```

---

## How the course was adapted to a regular workspace

The Academy notebooks expect a prepared lab workspace. These changes make them run in your own:

| Change | Where | Why |
|---|---|---|
| `ops.meta` settings table | created by `setup.sh` | `DBAcademyHelper` (`DA`) reads catalog, schema, username and dataset paths from it |
| Serverless environment in notebook metadata (week1: v6, weeks 2–4: v5) | all `.ipynb` (`scripts/set_serverless_env.py`) | Without it, serverless used environment v1 (Python 3.10) and `%pip install mlflow==3.12.0` ran for 25+ minutes |
| `restartPython()` / `%restart_python` only on Databricks | `week*/Includes/_common.py` | `dbutils.library` does not exist over Databricks Connect |
| `dbacademy.` catalog → `DA.catalog_name` | week3 4.3 demo | The `dbacademy` catalog only exists in Academy labs |
| Models for Model Serving registered with `env_pack="databricks_model_serving"` | week3 `Classroom-Setup-4.1.py`, 4.4 demo; week4 2.4a | Packs the notebook's Python environment into the model, so the endpoint build doesn't download packages (fails in workspaces whose serverless egress blocks PyPI) |
| Token file optional: falls back to the notebook's own credentials | week4 `Classroom-Setup-*.py` (`Token` class) | 2.3 / 2.4 pipelines ran only after pasting a PAT into `0_Generate_Tokens`; now they run unattended. A `var/credentials.cfg` is still used if present |
| `/dbfs/tmp/...` output → course volume (`DA.paths.working_dir`) | week4 2.4b Task 1 | `/dbfs` is not mounted on serverless compute |
| Access token printed in full → only last 4 characters | week4 `Classroom-Setup-*.py` | The token setup cells echoed the PAT into notebook output; `var/credentials.cfg` is git-ignored |
| `/Volumes/dbacademy_*` → Marketplace share paths | week2 `Classroom-Setup-1.1a.py`, `-3.2.py` | Marketplace shares have different catalog names |
| `.py` source notebooks → `.ipynb`, underscores in names | week1, week2, week4 | Same layout as week3; converted with the workspace's own exporter |

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
| Serving endpoint: `Container build failed. Cause: user_pip_resolution`, log shows `No matching distribution found for mlflow (from versions: none)` | The endpoint build cannot download packages: workspace serverless network policy / egress control or NCC | Register the model with `mlflow.register_model(..., env_pack="databricks_model_serving")` (done in this repo's serving demos), or ask an account admin to allow PyPI for serverless (Account Console → Security → Networking → Network policies) |
| VS Code: Databricks sidebar never logs in, setup cell fails with `NameError`; extension log shows `UrlError: Invalid host name` | No `workspace.host` in the bundle | Run `./setup.sh` (writes `databricks.local.yml`), then **Developer: Reload Window** |
| Local run: `default auth: metadata-service ... 127.0.0.1:<port> ... Connection refused` | The VS Code extension's local auth helper restarted on a new port; the running kernel still points at the old one | `DATABRICKS_AUTH_TYPE=pat` in `.env` (setup.sh writes it) so local runs use the token profile directly; restart the kernel |
| VS Code: *Databricks Connect disabled* | venv has no `pip` | `uv pip install --python .venv pip` (setup.sh does this) |
| `ModuleNotFoundError: nbformat` on `%run` | Needed by the extension's `%run` support | `uv pip install --python .venv nbformat` (setup.sh does this) |
| `%run ../Includes/...` not found locally | Jupyter cwd was the repo root | `jupyter.notebookFileRoot` in `.vscode/settings.json` (included) |
| `ValueError: cluster_id is required` | `restartPython()` over Databricks Connect | Guard in `_common.py` (included) |
| `Could not find experiment with ID None` | No notebook experiment for local runs | `MLFLOW_EXPERIMENT_NAME` in `.env` (setup.sh writes it) |
| Feature Engineering `401 Credential was not sent` | Library sends only static tokens; OAuth profiles have none | Use the PAT profile for local runs (setup.sh offers to create it) |
| `This model was packaged by Databricks Feature Store and can only be registered on a Databricks cluster` | MLflow restriction | Run that notebook on Databricks |

---

## Credits

Course notebooks and setup scripts in `week1/`–`week4/` are from **Databricks Academy**
(© 2026 Databricks, Inc. All rights reserved), with the adaptations listed above. Notes, `setup.sh`,
configuration and scripts are my own.
