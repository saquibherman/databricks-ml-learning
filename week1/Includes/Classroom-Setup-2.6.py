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

import gc
from pyspark.ml.feature import StringIndexerModel


def clear_ml_cache(globals_dict, model_vars=None):
    """Release Spark Connect ML model references to stay within the Serverless ML V6
    session cache limit (1 GB). Pass globals() from the calling notebook.
    Optionally pass a list of variable names to release; defaults to the standard
    pipeline variables used in this course."""
    if model_vars is None:
        model_vars = ["pipeline_model", "loaded_pipeline", "pipeline"]
    released = [v for v in model_vars if v in globals_dict]
    for v in released:
        del globals_dict[v]
    if released:
        gc.collect()
        print(f"ML cache cleanup: released {len(released)} model reference(s): {released}")
    else:
        print("ML cache cleanup: no prior model references found.")


def build_string_indexer_model(spark, categorical_cols, telco_labels):
    """Return a StringIndexerModel built directly from a fixed label vocabulary.

    Uses StringIndexerModel.from_arrays_of_labels(), so no data is scanned and the
    serialized model stores only the vocabulary (label -> index mapping). Each label
    list is sorted, which gives the same indices as
    StringIndexer(stringOrderType="alphabetAsc"). handleInvalid="keep" assigns null
    and unseen values to one extra index. The spark argument is not needed and is
    kept so existing calls still work."""
    categorical_cols_indexed = [c + "_index" for c in categorical_cols]
    return StringIndexerModel.from_arrays_of_labels(
        [sorted(telco_labels[c]) for c in categorical_cols],
        inputCols=categorical_cols,
        outputCols=categorical_cols_indexed,
        handleInvalid="keep",
    )


def check_model_size(model, temp_path, size_limit=268_435_456):
    """Verify a fitted model's serialized size is within the Serverless ML V6 256 MB
    per-model limit. Saves the model to temp_path, recursively sums file sizes, and
    raises AssertionError with a clear message if the limit is exceeded."""
    def _dir_size(path):
        total = 0
        try:
            for item in dbutils.fs.ls(path):
                if item.name.endswith("/"):
                    total += _dir_size(item.path)
                else:
                    total += item.size
        except Exception:
            pass
        return total

    model.write().overwrite().save(temp_path)
    size = _dir_size(temp_path)
    print(f"Model size : {size:>15,} bytes  ({size / 1024**2:.1f} MB)")
    print(f"Limit      : {size_limit:>15,} bytes  ({size_limit // 1024**2} MB)")
    assert size <= size_limit, (
        f"Model ({size / 1024**2:.1f} MB) exceeds the Serverless ML V6 "
        f"{size_limit // 1024**2} MB per-model limit. Simplify the pipeline to reduce model size."
    )
    print(f"✅ Model size is within the Serverless ML V6 limit.")
    return size

# COMMAND ----------

@DBAcademyHelper.add_init
def initialize_uc(self):

    table_name = 'telco_table'
    spark.sql(f"USE CATALOG {DA.catalog_name}")
    spark.sql(f"USE SCHEMA {DA.schema_name}")
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")

    print(f'Using catalog {DA.catalog_name} and schema {DA.schema_name}.')

# COMMAND ----------

# Initialize DBAcademyHelper
DA = DBAcademyHelper() 
DA.init()