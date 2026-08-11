from typing import Callable

_REGISTRY: dict[str, Callable] = {}


def register_suite(name: str):
    """Décorateur pour enregistrer une fonction d'expectations sous un nom de suite."""
    def wrapper(func: Callable):
        _REGISTRY[name] = func
        return func
    return wrapper


def get_expectations_for_suite(suite_name: str):
    if suite_name not in _REGISTRY:
        raise ValueError(
            f"Aucune suite d'expectations enregistrée sous le nom '{suite_name}'. "
            f"Suites disponibles : {list(_REGISTRY.keys())}"
        )
    return _REGISTRY[suite_name]()