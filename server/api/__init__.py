from server.api.update import router as update_router
from fastapi import APIRouter
from server.api.query import router as query_router
__all__ = ["router"]

router = APIRouter()
router.include_router(update_router, prefix="/xquant/update")
router.include_router(query_router, prefix="/xquant/query")