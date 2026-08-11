from pyspark.sql import SparkSession

from src.config import setup_java_env


def get_spark_session(app_name: str = "MonApplication") -> SparkSession:
    setup_java_env()
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .getOrCreate()
    )