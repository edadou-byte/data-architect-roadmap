# Projet Prefect

Ce projet utilise [Prefect](https://www.prefect.io/) pour orchestrer des pipelines de données en Python.

## Qu'est-ce que Prefect ?

Prefect est un framework d'orchestration de workflows qui permet de définir, planifier, surveiller et déployer des pipelines de données sous forme de code Python.

- **`@flow`** : décore une fonction qui orchestre l'exécution globale d'un pipeline.
- **`@task`** : décore une fonction représentant une unité de travail unitaire (extraction, transformation, appel API, etc.), avec retries, logs et cache automatiques.
- **Deployment** : version "packagée" d'un flow, planifiable et déclenchable à distance (via CLI, UI ou API).
- **Work Pool / Worker** : infrastructure qui exécute les runs planifiés des déploiements.

## Structure du projet

```
mon_projet_prefect/
├── flows/
│   ├── __init__.py
│   ├── customer_flow.py      # Flow principal (orchestration)
│   └── ...
│
├── tasks/
│   ├── __init__.py
│   ├── customers_tasks.py    # Tasks réutilisables (@task)
│   └── ...
│
├── deployments/
│   └── deployment.py         # Déploiement via serve() ou script Python
│
├── blocks/
│   └── config_blocks.py      # Configuration des Blocks (secrets, connexions)
│
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Fonctions utilitaires non-Prefect
│
├── tests/
│   ├── __init__.py
│   ├── test_flows.py
│   └── test_tasks.py
│
├── prefect.yaml               # Config de déploiement (Prefect 2.x/3.x)
├── requirements.txt
├── pyproject.toml             # Rend le projet installable (imports fiables)
├── .env                        # Variables d'environnement (non versionné)
├── .gitignore
└── README.md
```

### Rôle de chaque dossier

| Dossier | Contenu |
|---|---|
| `flows/` | Fonctions `@flow`, orchestration du pipeline |
| `tasks/` | Fonctions `@task`, unités de travail réutilisables |
| `deployments/` | Scripts ou config de déploiement |
| `blocks/` | Configuration des Blocks Prefect (credentials, connexions) |
| `utils/` | Fonctions utilitaires indépendantes de Prefect |
| `tests/` | Tests unitaires des flows et tasks |

## Installation

```bash
pip install -r requirements.txt
```

Pour que les imports (`from tasks.customers_tasks import ...`) fonctionnent quel que soit l'endroit d'où le script est lancé, installer le projet en mode développement :

```bash
pip install -e .
```

Cela nécessite un `pyproject.toml` minimal à la racine :

```toml
[project]
name = "mon-projet-prefect"
version = "0.1.0"

[tool.setuptools.packages.find]
where = ["."]
```

## Exécution en local

Exécuter un flow directement, comme une fonction Python classique :

```bash
python -m flows.customer_flow
```

> ⚠️ La commande `prefect run script.py` n'existe plus depuis Prefect 2.x. On exécute simplement le script Python (`python flows/customer_flow.py` ou `python -m flows.customer_flow`).

### Voir les runs dans l'UI Prefect (optionnel)

```bash
# Terminal 1 : démarrer le serveur Prefect local
prefect server start

# Terminal 2 : exécuter le flow
python -m flows.customer_flow
```

L'UI est accessible sur `http://127.0.0.1:4200`.

## Déploiement

### Option 1 — `prefect.yaml` (recommandé pour la production)

```bash
prefect work-pool create mon-work-pool --type process
prefect worker start --pool mon-work-pool
prefect deploy --all
```

### Option 2 — `serve()` (pratique en développement)

```bash
python deployments/deployment.py
```

Le process reste actif et exécute le flow selon la planification définie, sans nécessiter de work pool.

## Tests

```bash
pytest tests/
```

## Ressources

- [Documentation officielle Prefect](https://docs.prefect.io/)
- [Prefect GitHub](https://github.com/PrefectHQ/prefect)
