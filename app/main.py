from fastapi import FastAPI

from app.config.settings import get_settings
from app.interfaces.api.routes import router as price_router

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(price_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
