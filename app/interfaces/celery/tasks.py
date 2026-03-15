import asyncio

from app.config.dependencies import get_price_service
from app.interfaces.celery.celery_app import celery_app


@celery_app.task(name="app.interfaces.celery.tasks.collect_prices_task")
def collect_prices_task() -> list[dict[str, float | int | str]]:
    service = get_price_service()
    prices = asyncio.run(service.collect_and_store())
    return [price.model_dump() for price in prices]
