# Databricks notebook source
# MAGIC %run ./_common

# COMMAND ----------

!pip install databricks-feature-engineering

# COMMAND ----------

from pyspark.sql.functions import col, monotonically_increasing_id

# COMMAND ----------

# Create a delta table for diet features
@DBAcademyHelper.add_init
def create_diet_features_table(self):
    
    spark.sql(f"USE CATALOG {DA.catalog_name}")
    spark.sql(f"USE SCHEMA {DA.schema_name}")

    # Set the path of the dataset
    shared_volume_name = 'cdc-diabetes' # From Marketplace
    csv_name = 'diabetes_binary_5050split_BRFSS2015' # CSV file name
    dataset_path = f"{DA.paths.datasets.cdc_diabetes}/{shared_volume_name}/{csv_name}.csv" # Full path


    # Drop tables from any previous run, so the lab can be rerun cleanly
    # (an overwrite keeps an old PRIMARY KEY constraint, and create_table fails if the table exists)
    for t in ["diabetes_features", "diet_features"]:
        spark.sql(f"DROP TABLE IF EXISTS {DA.catalog_name}.{DA.schema_name}.{t}")

    df = spark.read.csv(dataset_path, header="true", inferSchema="true", multiLine="true", escape='"')

    # Create the respondent key ONCE and persist it in a silver table.
    # Every feature table in the lab is built from this table, so they all share the same keys.
    df = df.withColumn("UID", monotonically_increasing_id())
    silver_table = f"{DA.catalog_name}.{DA.schema_name}.cdc_diabetes_silver"
    df.write.format("delta").mode("overwrite").option("overwriteSchema", True).saveAsTable(silver_table)

    diet_df = spark.table(silver_table).select("UID", "Fruits", "Veggies", "HvyAlcoholConsump", "Smoker")
    table_name = f"{DA.catalog_name}.{DA.schema_name}.diet_features"
    diet_df.write.format("delta").mode("overwrite").saveAsTable(table_name)

# COMMAND ----------

# Initialize DBAcademyHelper
DA = DBAcademyHelper() 
DA.init()