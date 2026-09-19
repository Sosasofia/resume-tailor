from fastapi import APIRouter


from app.api.routes.extract import router as extract_router
from app.api.routes.tailor import router as tailor_router
from app.api.routes.health import router as health_router


router = APIRouter()


router.include_router(extract_router)
router.include_router(tailor_router)
router.include_router(health_router)