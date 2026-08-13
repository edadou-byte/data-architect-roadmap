import yaml

from src.config import BASE_DIR
from src.spark_session import get_spark_session
from src.gx_context import get_context
from src.pipeline.gx_pipeline import run_file_validation
from src.pipeline.resolve_dataset_files import resolve_dataset_files
import src.expectations  # déclenche les @register_suite


def load_datasets_config():
    config_path = BASE_DIR / "config" / "datasets.yml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)["datasets"]


def run(dataset_names: list[str] | None = None):
    """dataset_names : liste de noms (ex: ["ventes"]) pour ne lancer que ceux-là.
    None ou liste vide = tout exécuter (comportement actuel)."""
    all_datasets = load_datasets_config()

    if dataset_names:
        unknown = set(dataset_names) - {d["name"] for d in all_datasets}
        if unknown:
            raise ValueError(f"Dataset(s) inconnu(s) : {unknown}")
        all_datasets = [d for d in all_datasets if d["name"] in dataset_names]

    spark = get_spark_session()
    context = get_context()
    overall_success = True

    try:
        for dataset_config in all_datasets:
            resolved_files = resolve_dataset_files(dataset_config, BASE_DIR)

            for file_config in resolved_files:
                result = run_file_validation(context, spark, file_config)
                overall_success = overall_success and result.success

        context.build_data_docs()

    finally:
        spark.stop()

    return overall_success