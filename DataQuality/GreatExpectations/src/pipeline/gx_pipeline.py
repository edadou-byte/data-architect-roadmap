from datetime import datetime, timezone

import great_expectations as gx
from great_expectations import RunIdentifier

from src.expectations.registry import get_expectations_for_suite
from src.databricks_config import build_databricks_connection_string


def get_or_create_suite(context, suite_name: str):
    try:
        suite = context.suites.get(name=suite_name)
    except Exception:
        suite = context.suites.add(gx.ExpectationSuite(name=suite_name))
        for expectation in get_expectations_for_suite(suite_name):
            suite.add_expectation(expectation)
    return suite


def get_or_create_batch_definition(context, file_config: dict):
    file_name = file_config["file_name"]
    dataset_type = file_config.get("type", "parquet")
    data_source_name = f"{file_name}_source"
    data_asset_name = f"{file_name}_asset"
    batch_definition_name = f"{file_name}_batch_def"

    try:
        data_source = context.data_sources.get(data_source_name)
    except Exception:
        if dataset_type == "databricks":
            data_source = context.data_sources.add_databricks_sql(
                name=data_source_name,
                connection_string=build_databricks_connection_string(),
            )
        else:
            data_source = context.data_sources.add_spark(name=data_source_name)

    try:
        data_asset = data_source.get_asset(data_asset_name)
    except Exception:
        if dataset_type == "databricks":
            data_asset = data_source.add_table_asset(
                name=data_asset_name,
                table_name=file_config["table"],
            )
        else:
            data_asset = data_source.add_dataframe_asset(name=data_asset_name)

    try:
        batch_definition = data_asset.get_batch_definition(batch_definition_name)
    except Exception:
        if dataset_type == "databricks":
            batch_definition = data_asset.add_batch_definition_whole_table(
                batch_definition_name
            )
        else:
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
    dataset_type = file_config.get("type", "parquet")
    suite_name = file_config["expectation_suite"]
    checkpoint_name = file_config["checkpoint_name"]

    suite = get_or_create_suite(context, suite_name)
    batch_definition = get_or_create_batch_definition(context, file_config)
    validation_definition = get_or_create_validation_definition(
        context, file_name, batch_definition, suite
    )
    checkpoint = get_or_create_checkpoint(context, checkpoint_name, validation_definition)

    run_id = RunIdentifier(run_name=file_name, run_time=datetime.now(timezone.utc))

    if dataset_type == "databricks":
        # Pas besoin de DataFrame : GX interroge directement le SQL Warehouse
        result = checkpoint.run(run_id=run_id)
    else:
        df = spark.read.parquet(file_config["path"])
        result = checkpoint.run(batch_parameters={"dataframe": df}, run_id=run_id)

    print(f"[{file_name}] Succès : {result.success}")
    return result