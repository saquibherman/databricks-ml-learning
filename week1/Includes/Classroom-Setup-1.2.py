# Databricks notebook source
# MAGIC %run ./_common

# COMMAND ----------

import warnings
warnings.filterwarnings("ignore")

import numpy as np
np.set_printoptions(precision=2)

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# COMMAND ----------

@DBAcademyHelper.add_init
def initialize_uc(self):

    table_name = 'telco_table'
    spark.sql(f"USE CATALOG {DA.catalog_name}")
    spark.sql(f"USE SCHEMA {DA.schema_name}")
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    # Academy labs start with an empty schema; in a reused workspace schema the demo's
    # saveAsTable (no mode) fails on rerun with TABLE_OR_VIEW_ALREADY_EXISTS.
    spark.sql("DROP TABLE IF EXISTS telco_missing_bronze")

    print(f'Using catalog {DA.catalog_name} and schema {DA.schema_name}.')

# COMMAND ----------

# Initialize DBAcademyHelper
DA = DBAcademyHelper() 
DA.init()