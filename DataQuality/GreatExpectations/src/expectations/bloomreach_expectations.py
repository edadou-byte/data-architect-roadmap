import great_expectations as gx

from src.expectations.registry import register_suite


@register_suite("bloomreach_expectations")
def get_bloomreach_expectations():
    return [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="flux"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="bu"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="lib_enseigne"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="language"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="template_id"),
        gx.expectations.ExpectColumnValueLengthsToBeBetween(column="template_id", min_value=1),
    ]