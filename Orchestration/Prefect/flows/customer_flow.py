from prefect import flow
from tasks.customers_tasks import get_customer_ids, process_customer

@flow
def main() -> list[str]:
    customer_ids = get_customer_ids()
    # Map the process_customer task across all customer IDs
    results = process_customer.map(customer_ids)
    return results

if __name__ == "__main__":
    main()