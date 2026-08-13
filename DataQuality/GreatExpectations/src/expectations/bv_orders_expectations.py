import great_expectations as gx

from src.expectations.registry import register_suite


@register_suite("bv_orders")
def get_bv_orders_expectations():
    return [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"),
        gx.expectations.ExpectColumnValuesToMatchRegex(
        column="order_date", regex = r"^\d{4}-\d{2}-\d{2}$"
        ),
        gx.expectations.ExpectColumnValuesToBeBetween(column="total_price", min_value=1),
    ]