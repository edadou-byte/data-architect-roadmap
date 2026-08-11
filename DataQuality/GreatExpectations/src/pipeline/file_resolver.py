import glob
from pathlib import Path


def resolve_dataset_files(dataset_config: dict, base_dir: Path) -> list[dict]:
    """Étend un pattern glob (ex: resources/ventes_*.parquet) en une liste
    de configs concrètes, une par fichier trouvé."""
    pattern = str(base_dir / dataset_config["path"])
    matched_files = sorted(glob.glob(pattern))

    if not matched_files:
        raise FileNotFoundError(f"Aucun fichier ne correspond à : {pattern}")

    resolved = []
    for file_path in matched_files:
        file_stem = Path(file_path).stem  # ex: ventes_2025_01

        resolved.append({
            **dataset_config,
            "file_name": file_stem,
            "path": file_path,
            # Checkpoint/validation/batch definitions nommés par fichier
            # pour garder une traçabilité individuelle
            "checkpoint_name": f"{dataset_config['checkpoint_name']}_{file_stem}",
        })
    return resolved