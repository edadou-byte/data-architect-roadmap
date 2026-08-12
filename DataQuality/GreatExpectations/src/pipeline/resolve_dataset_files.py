import glob
from pathlib import Path

def resolve_parquet_files(dataset_config: dict, base_dir: Path) -> list[dict]:
    pattern = str(base_dir / dataset_config["path"])
    matched_files = sorted(glob.glob(pattern))
    if not matched_files:
        raise FileNotFoundError(f"Aucun fichier ne correspond à : {pattern}")

    resolved = []
    for file_path in matched_files:
        file_stem = Path(file_path).stem
        resolved.append({
            **dataset_config,
            "file_name": file_stem,
            "path": file_path,
            "checkpoint_name": f"{dataset_config['checkpoint_name']}_{file_stem}",
        })
    return resolved

def resolve_databricks_table(dataset_config: dict) -> list[dict]:
    """Une seule unité de validation par table (pas de glob, pas de notion de fichier)."""
    table = dataset_config["table"]
    file_name = table.replace(".", "_")  # ex: main_sales_clients
    return [{
        **dataset_config,
        "file_name": file_name,
        "checkpoint_name": f"{dataset_config['checkpoint_name']}_{file_name}",
    }]

def resolve_dataset_files(dataset_config: dict, base_dir: Path) -> list[dict]:
    dataset_type = dataset_config.get("type", "parquet")
    if dataset_type == "parquet":
        return resolve_parquet_files(dataset_config, base_dir)
    if dataset_type == "databricks":
        return resolve_databricks_table(dataset_config)
    raise ValueError(f"Type de dataset inconnu : {dataset_type}")