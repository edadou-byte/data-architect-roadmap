import argparse
import sys

from dotenv import load_dotenv

from src.pipeline.run_all import run

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Lance les validations Great Expectations")
    parser.add_argument(
        "--datasets",
        nargs="+",
        help="Nom(s) de dataset à exécuter (ex: --datasets clients_databricks). "
             "Si absent, exécute tous les datasets de config/datasets.yml.",
    )
    args = parser.parse_args()

    success = run(dataset_names=args.datasets)
    sys.exit(0 if success else 1)