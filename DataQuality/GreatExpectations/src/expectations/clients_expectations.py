import great_expectations as gx

from src.expectations.registry import register_suite


@register_suite("clients")
def get_clients_expectations():
    return [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="id_client"),
        gx.expectations.ExpectColumnValuesToMatchRegex(
            column="email", regex=r"^[^@]+@[^@]+\.[^@]+$"
        ),
    ]