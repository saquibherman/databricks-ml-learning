# Databricks notebook source
# MAGIC %md
# MAGIC # Set Champion Alias
# MAGIC
# MAGIC This QC_Automation notebook ensures the `churn-prediction` model exists and has the **champion** alias.
# MAGIC
# MAGIC 1. If no model versions exist (upstream labs didn't register one), it creates a **minimal placeholder** model so `2.5a LAB check_status` doesn't crash on `max()`.
# MAGIC 2. If the model has the **baseline** alias, it changes it to **champion** (automating the manual UI step in Task 1 of the 2.5 LAB).
# MAGIC 3. If the model already has **champion**, no changes are made.

# COMMAND ----------

# MAGIC %run ../../Includes/Classroom-Setup-1.1a

# COMMAND ----------

# Ensure the churn-prediction model exists and has the "champion" alias.
# If the model wasn't created by upstream labs, register a minimal placeholder
# so the deploy-workflow-job's check_status task does not crash on max().

import mlflow
import mlflow.sklearn
from sklearn.dummy import DummyClassifier
import numpy as np

mlflow.set_registry_uri("databricks-uc")
client = mlflow.MlflowClient()

model_name = f"{DA.catalog_name}.{DA.schema_name}.churn-prediction"
print(f"Model: {model_name}")

# Step 1: Check if model has any versions
versions = []
try:
    versions = client.search_model_versions(f"name='{model_name}'")
except Exception:
    pass

# Step 2: If no versions exist, register a minimal placeholder model
if not versions:
    print(f"\n  No versions found — registering a placeholder model...")
    X_dummy = np.array([[0, 1], [1, 0], [1, 1], [0, 0]])
    y_dummy = np.array([0, 1, 1, 0])
    dummy_model = DummyClassifier(strategy="most_frequent").fit(X_dummy, y_dummy)

    with mlflow.start_run(run_name="QC_placeholder_model") as run:
        mlflow.sklearn.log_model(
            sk_model=dummy_model,
            artifact_path="model",
            registered_model_name=model_name,
        )
    print(f"  Registered placeholder model: {model_name} (run_id={run.info.run_id})")
    # Refresh versions list
    versions = client.search_model_versions(f"name='{model_name}'")

# Step 3: Ensure the "champion" alias is set
baseline_version = None
champion_version = None
for v in versions:
    # search_model_versions doesn't include aliases for UC models — fetch individually
    mv = client.get_model_version(model_name, v.version)
    v_aliases = mv.aliases or []
    print(f"  Version {v.version} — aliases: {v_aliases}")
    if "baseline" in v_aliases:
        baseline_version = v.version
    if "champion" in v_aliases:
        champion_version = v.version

if champion_version:
    print(f"\n  Model already has 'champion' alias on version {champion_version}. No change needed.")
elif baseline_version:
    client.delete_registered_model_alias(model_name, "baseline")
    client.set_registered_model_alias(model_name, "champion", baseline_version)
    print(f"\n  Changed alias: 'baseline' -> 'champion' on version {baseline_version}")
else:
    latest = max(versions, key=lambda x: int(x.version))
    client.set_registered_model_alias(model_name, "champion", latest.version)
    print(f"\n  Set 'champion' alias on latest version {latest.version}")

print("\n  Model is ready for the deploy-workflow-job!")