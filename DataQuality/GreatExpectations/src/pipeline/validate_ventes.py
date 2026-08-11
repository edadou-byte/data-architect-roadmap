import json

from src.config import VENTES_PARQUET_PATH, VALIDATION_RESULTS_PATH
from src.spark_session import get_spark_session
from src.gx_context import get_or_create_dataframe_batch_definition
from src.expectations.ventes_expectations import get_ventes_expectations


def run():
    spark = get_spark_session()

    try:
        context, batch_definition = get_or_create_dataframe_batch_definition()

        df = spark.read.parquet(str(VENTES_PARQUET_PATH))
        df.show()
        df.printSchema()

        batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

        results = []
        for expectation in get_ventes_expectations():
            validation_result = batch.validate(expectation)
            results.append(validation_result.to_json_dict())

        VALIDATION_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(VALIDATION_RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

    finally:
        spark.stop()