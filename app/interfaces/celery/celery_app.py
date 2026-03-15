from celery import Celery

from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "crypto_price_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.interfaces.celery.tasks"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-index-prices-every-minute": {
            "task": "app.interfaces.celery.tasks.collect_prices_task",
            "schedule": 60.0,
        }
    },
)
