# Week 4 Notes: Machine Learning Operations

My own notes from the Databricks Academy course *Machine Learning Operations* (v2.4.2).

## Modules

| # | Module | Lessons |
|---|--------|---------|
| 1 | Modern MLOps | Defining MLOps, MLOps on Databricks, building Lakeflow Jobs in the UI (demo pipeline 1.3a–e, lab pipeline 1.4a–b) |
| 2 | Architecting MLOps Solutions | MLOps principles and architectures, ML pipelines with the Databricks API (2.3) and the Databricks CLI (2.4, lab 2.5) |
| 3 | Implementation and Monitoring | Types of model monitoring, data profiling dashboards (3.3), model monitoring lab (3.4) |

## Setup notes

- Serverless **environment version 5** for everything except **2.4 Demo** and **2.5 LAB**, which the
  course wants on a classic **DBR 17.3 ML** cluster (they use the Databricks CLI in the web terminal).
- **2.3 / 2.4 pipelines** used to need a personal access token in `var/credentials.cfg` (from
  **`M02_Architecting_MLOps_Solutions/0_Generate_Tokens`**). They now fall back to the notebook's own
  credentials, so that step is optional. If you do create the file, it is git-ignored; never commit it.
  The setup code prints only the last 4 characters of the token.
- **2.4a deploys a Model Serving endpoint.** The model is registered with
  `env_pack="databricks_model_serving"` so the endpoint build doesn't need to download packages.
- The 1.3 and 2.4 "Demo Pipeline" folders are meant to be wired into a Lakeflow Job (tasks pass values
  with `dbutils.jobs.taskValues`), not run one notebook at a time.
- Datasets: `databricks_bank_loan_modelling_dataset` (banking) and
  `databricks_diabetes_health_indicators_dataset` (3.3 / 3.4).

## Notes

<!-- Add what you learn as you go through each module -->
