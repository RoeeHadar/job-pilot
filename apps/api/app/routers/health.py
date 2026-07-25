from fastapi import APIRouter

from app.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "market_scope": "israel",
        "has_apify_token": bool(settings.apify_token),
        "has_llm_key": bool(settings.openai_api_key or settings.anthropic_api_key),
    }
