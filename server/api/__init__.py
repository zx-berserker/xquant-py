from server.api.update import router as update_router
from fastapi import APIRouter

__all__ = ["router"]

router = APIRouter()
router.include_router(update_router, prefix="/xquant/update")