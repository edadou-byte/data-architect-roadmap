import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def setup_java_env():
    """Surcharge JAVA_HOME uniquement si JAVA_HOME_OVERRIDE est défini dans l'environnement
    (.env) — utile en dev local Windows. Sur les environnements où JAVA_HOME est déjà
    correctement configuré (Docker/Linux), cette fonction ne fait rien."""
    java_home_override = os.getenv("JAVA_HOME_OVERRIDE")
    if not java_home_override:
        return

    os.environ["JAVA_HOME"] = java_home_override
    os.environ["PATH"] = os.path.join(java_home_override, "bin") + os.pathsep + os.environ["PATH"]