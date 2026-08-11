import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

JAVA_17_HOME = os.getenv("JAVA_HOME_OVERRIDE", r"C:\Talend\Java\zulu17.54.21-ca-jdk17.0.13-win_x64")

RESOURCES_DIR = BASE_DIR / "resources"
OUTPUTS_DIR = BASE_DIR / "outputs"

VENTES_PARQUET_PATH = RESOURCES_DIR / "ventes_2025_01.parquet"
VALIDATION_RESULTS_PATH = OUTPUTS_DIR / "validation_results.json"


def setup_java_env():
    os.environ["JAVA_HOME"] = JAVA_17_HOME
    os.environ["PATH"] = os.path.join(JAVA_17_HOME, "bin") + os.pathsep + os.environ["PATH"]