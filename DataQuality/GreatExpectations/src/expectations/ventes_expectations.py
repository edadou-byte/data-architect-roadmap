import great_expectations as gx

from src.expectations.registry import register_suite


@register_suite("ventes")
def get_ventes_expectations():
    return [
        gx.expectations.ExpectColumnValuesToBeBetween(column="quantite", min_value=1),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="client_email"),
        gx.expectations.ExpectColumnValuesToMatchRegex(column="client_email", regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"),
    ]