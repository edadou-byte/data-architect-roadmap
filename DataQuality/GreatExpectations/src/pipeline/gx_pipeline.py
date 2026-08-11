from datetime import datetime, timezone

import great_expectations as gx
from great_expectations import RunIdentifier

from src.expectations.registry import get_expectations_for_suite


def get_or_create_suite(context, suite_name: str):
    """Une suite par TYPE de dataset (ventes, clients...), partagée entre
    tous les fichiers correspondants — c'est la logique métier qui ne change pas
    d'un fichier à l'autre."""
    try:
        suite = context.suites.get(name=suite_name)
    except Exception:
        suite = context.suites.add(gx.ExpectationSuite(name=suite_name))
        for expectation in get_expectations_for_suite(suite_name):
            suite.add_expectation(expectation)
    return suite


def get_or_create_batch_definition(context, file_name: str):
    """Un Batch Definition par FICHIER concret (ventes_2025_01, ventes_2025_02...)."""
    data_source_name = f"{file_name}_source"
    data_asset_name = f"{file_name}_asset"
    batch_definition_name = f"{file_name}_batch_def"

    try:
        data_source = context.data_sources.get(data_source_name)
    except Exception:
        data_source = context.data_sources.add_spark(name=data_source_name)

    try:
        data_asset = data_source.get_asset(data_asset_name)
    except Exception:
        data_asset = data_source.add_dataframe_asset(name=data_asset_name)

    try:
        batch_definition = data_asset.get_batch_definition(batch_definition_name)
    except Exception:
        batch_definition = data_asset.add_batch_definition_whole_dataframe(
            batch_definition_name
        )

    return batch_definition


def get_or_create_validation_definition(context, file_name, batch_definition, suite):
    name = f"{file_name}_validation_def"
    try:
        return context.validation_definitions.get(name)
    except Exception:
        return context.validation_definitions.add(
            gx.ValidationDefinition(name=name, data=batch_definition, suite=suite)
        )


def get_or_create_checkpoint(context, checkpoint_name, validation_definition):
    try:
        return context.checkpoints.get(checkpoint_name)
    except Exception:
        return context.checkpoints.add(
            gx.Checkpoint(
                name=checkpoint_name,
                validation_definitions=[validation_definition],
                actions=[gx.checkpoint.UpdateDataDocsAction(name="update_data_docs")],
            )
        )


def run_file_validation(context, spark, file_config: dict):
    file_name = file_config["file_name"]
    path = file_config["path"]
    suite_name = file_config["expectation_suite"]
    checkpoint_name = file_config["checkpoint_name"]

    df = spark.read.parquet(path)

    suite = get_or_create_suite(context, suite_name)
    batch_definition = get_or_create_batch_definition(context, file_name)
    validation_definition = get_or_create_validation_definition(
        context, file_name, batch_definition, suite
    )
    checkpoint = get_or_create_checkpoint(context, checkpoint_name, validation_definition)

    run_id = RunIdentifier(
        run_name=file_name,  # ex: "ventes_2025_01"
        run_time=datetime.now(timezone.utc),
    )

    result = checkpoint.run(
        batch_parameters={"dataframe": df},
        run_id=run_id,
    )

    print(f"[{file_name}] Succès : {result.success}")
    return result