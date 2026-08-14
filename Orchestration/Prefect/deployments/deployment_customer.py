# deployments/deployment.py
from prefect import serve
from flows.customer_flow import main

if __name__ == "__main__":
    deployment = main.to_deployment(
        name="main-deployment",
        tags=["clients"],
        cron="0 6 * * *",
        description="Traite les IDs clients"
    )
    serve(deployment)