import json
from pathlib import Path

from src.gx_context import get_or_create_dataframe_batch_definition
from src.expectations.registry import get_expectations_for_suite


def validate_dataset(spark, name: str, path: str, expectation_suite: str, outputs_dir: Path):
    context, batch_definition = get_or_create_dataframe_batch_definition(
        data_source_name=f"{name}_source",
        data_asset_name=f"{name}_asset",
        batch_definition_name=f"{name}_batch_def",
    )

    df = spark.read.parquet(path)
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    expectations = get_expectations_for_suite(expectation_suite)

    results = [
        expectation_result.to_json_dict()
        for expectation_result in (batch.validate(exp) for exp in expectations)
    ]

    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_path = outputs_dir / f"{name}_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"[{name}] Résultats écrits dans {output_path}")
    return results