import yaml

from src.config import BASE_DIR
from src.spark_session import get_spark_session
from src.gx_context import get_context
from src.pipeline.gx_pipeline import run_file_validation
from src.pipeline.file_resolver import resolve_dataset_files
import src.expectations  # déclenche les @register_suite


def load_datasets_config():
    config_path = BASE_DIR / "config" / "datasets.yml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)["datasets"]


def run():
    spark = get_spark_session()
    context = get_context()

    try:
        for dataset_config in load_datasets_config():
            resolved_files = resolve_dataset_files(dataset_config, BASE_DIR)

            for file_config in resolved_files:
                run_file_validation(context, spark, file_config)

        context.build_data_docs()

    finally:
        spark.stop()