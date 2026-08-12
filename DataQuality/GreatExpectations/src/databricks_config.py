import os


def build_databricks_connection_string() -> str:
    """Construit la connection string SQLAlchemy pour un SQL Warehouse Databricks.
    Ne jamais committer host/token en dur : utiliser des variables d'environnement."""
    host = os.environ["DATABRICKS_HOST"]            # ex: adb-xxxxxxxx.azuredatabricks.net
    http_path = os.environ["DATABRICKS_HTTP_PATH"]  # ex: /sql/1.0/warehouses/xxxxxxxx
    token = os.environ["DATABRICKS_TOKEN"]
    catalog = os.environ.get("DATABRICKS_CATALOG", "main")
    schema = os.environ.get("DATABRICKS_SCHEMA", "default")

    return (
        f"databricks://token:{token}@{host}:443/{schema}"
        f"?http_path={http_path}&catalog={catalog}"
    )