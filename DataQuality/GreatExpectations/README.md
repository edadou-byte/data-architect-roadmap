# DataQuality / GreatExpectations

Pipeline de contrôle qualité de données basé sur [Great Expectations](https://greatexpectations.io/), supportant plusieurs sources de données (fichiers Parquet via Spark, tables Databricks, tables PostgreSQL) avec une même logique de validation, de génération de checkpoints et de Data Docs.

## Sommaire

- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Ajouter un dataset](#ajouter-un-dataset)
- [Ajouter une nouvelle source de données](#ajouter-une-nouvelle-source-de-données)
- [Data Docs](#data-docs)
- [Améliorations possibles](#améliorations-possibles)

## Architecture

Le projet lit une liste de datasets déclarés dans `config/datasets.yml`, résout chacun en une ou plusieurs unités de validation (un fichier Parquet = une unité, une table SQL = une unité), puis pour chacune :

1. crée (ou récupère) une **Expectation Suite** — les règles de qualité, définies en Python et enregistrées via un registre par décorateur
2. crée (ou récupère) une **Data Source / Data Asset / Batch Definition** GX, adaptée au type de source (`parquet`, `databricks`, `postgres`)
3. exécute un **Checkpoint** qui valide les données et met à jour les **Data Docs** (rapport HTML)

Trois types de sources sont supportés aujourd'hui :

| Type | Connexion | Lecture |
|---|---|---|
| `parquet` (défaut) | Spark local (`local[*]`) | `spark.read.parquet(...)` sur un glob de fichiers |
| `databricks` | SQL Warehouse Databricks via `databricks-sql-connector` / SQLAlchemy | table interrogée directement en SQL, pas de DataFrame |
| `postgres` | SQLAlchemy (`psycopg2`) | table interrogée directement en SQL, pas de DataFrame |

## Prérequis

- Python 3.11+
- Java 17 (requis par PySpark pour le type `parquet`)
- Accès réseau aux sources concernées (SQL Warehouse Databricks, instance PostgreSQL) si ces types sont utilisés

## Installation

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine (non commité) pour les credentials :

```env
# PySpark / Java (Windows uniquement, sinon laisser la valeur par défaut Linux du Dockerfile)
JAVA_HOME_OVERRIDE=C:\Talend\Java\zulu17.54.21-ca-jdk17.0.13-win_x64

# Databricks SQL Warehouse
DATABRICKS_HOST=adb-xxxxxxxx.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxxxxx
DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXX
DATABRICKS_CATALOG=main
DATABRICKS_SCHEMA=default

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb
```

`main.py` charge ce fichier automatiquement via `python-dotenv`.

### Déclaration des datasets — `config/datasets.yml`

```yaml
datasets:
  - name: ventes
    path: resources/ventes_*.parquet
    expectation_suite: ventes
    checkpoint_name: ventes_checkpoint

  - name: clients_databricks
    type: databricks
    table: demo_edadou.gold.bv_customer_order
    expectation_suite: bv_orders
    checkpoint_name: bv_orders_checkpoint

  - name: clients_postgres
    type: postgres
    table: esb_gbmref.tld_esb_bloomreach_routing
    expectation_suite: bloomreach_expectations
    checkpoint_name: bloomreach_checkpoint
```

- `type` : `parquet` (défaut si omis), `databricks` ou `postgres`
- `path` : glob de fichiers, uniquement pour `type: parquet`
- `table` : `catalog.schema.table` (Databricks) ou `schema.table` (PostgreSQL), pour les types SQL
- `expectation_suite` : nom de la suite enregistrée dans `src/expectations/`
- `checkpoint_name` : préfixe du checkpoint généré

## Utilisation

Lancer l'ensemble des datasets déclarés dans `config/datasets.yml` :

```bash
python main.py
```

Cela va, pour chaque dataset :
- résoudre les unités de validation (fichiers ou tables)
- exécuter les checkpoints associés
- régénérer les Data Docs

## Structure du projet

```
DataQuality/GreatExpectations/
├── config/
│   └── datasets.yml              # déclaration des datasets à valider
├── gx/gx/
│   ├── great_expectations.yml    # config GX (stores, data_docs_sites, datasources fluents)
│   └── uncommitted/
│       └── data_docs/local_site/ # rapport HTML généré
├── resources/                    # fichiers Parquet d'exemple
├── src/
│   ├── config.py                 # chemins, setup Java
│   ├── spark_session.py          # SparkSession locale (type parquet)
│   ├── databricks_config.py      # connection string SQLAlchemy Databricks
│   ├── postgresql_config.py      # connection string SQLAlchemy PostgreSQL
│   ├── gx_context.py             # contexte Great Expectations
│   ├── expectations/
│   │   ├── registry.py           # décorateur @register_suite
│   │   ├── ventes_expectations.py
│   │   ├── clients_expectations.py
│   │   ├── bv_orders_expectations.py
│   │   └── bloomreach_expectations.py
│   └── pipeline/
│       ├── resolve_dataset_files.py  # résout un dataset config -> liste d'unités à valider
│       ├── gx_pipeline.py            # suite / data source / batch / checkpoint génériques
│       └── run_all.py                # orchestration globale
└── main.py                       # point d'entrée
```

## Ajouter un dataset

1. Ajouter une entrée dans `config/datasets.yml` (voir [Configuration](#configuration))
2. Créer le fichier de suite correspondant dans `src/expectations/`, sur le modèle de `bv_orders_expectations.py` :

```python
import great_expectations as gx

from src.expectations.registry import register_suite


@register_suite("nom_de_la_suite")
def get_nom_de_la_suite_expectations():
    return [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="ma_colonne"),
    ]
```

3. Importer ce module dans `src/expectations/__init__.py` pour que le décorateur s'exécute au démarrage :

```python
from src.expectations import ventes_expectations, clients_expectations, bv_orders_expectations, bloomreach_expectations, nom_du_fichier  # noqa: F401
```

## Ajouter une nouvelle source de données

Le projet est conçu pour qu'ajouter un type (ex. MySQL, Snowflake) touche seulement :

- `src/<nom>_config.py` : construction de la connection string
- `src/pipeline/resolve_dataset_files.py` : une fonction `resolve_<nom>_table` + une branche dans `resolve_dataset_files`
- `src/pipeline/gx_pipeline.py` : une branche dans `get_or_create_batch_definition` (création de la data source) et dans `run_file_validation` (mode d'exécution du checkpoint)

Les types basés sur SQL (`databricks`, `postgres`) partagent déjà la même logique côté `add_table_asset` / `add_batch_definition_whole_table` — un nouveau type SQL peut réutiliser ce chemin.

## Data Docs

Chaque exécution de checkpoint met à jour automatiquement un site HTML de Data Docs (via l'action `UpdateDataDocsAction` définie dans `get_or_create_checkpoint`), disponible dans :

```
gx/gx/uncommitted/data_docs/local_site/index.html
```

Pour régénérer manuellement ou ouvrir le site sans relancer tout le pipeline :

```python
from src.gx_context import get_context

context = get_context()
context.build_data_docs()
context.open_data_docs()
```

## Améliorations possibles

- Ne créer la session Spark que si au moins un dataset de type `parquet` est présent dans l'exécution, pour éviter le coût inutile sur les runs 100% SQL
