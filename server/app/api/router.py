from fastapi import APIRouter


from app.api.routes import analyze, extract, tailor, health


router = APIRouter()

router.include_router(analyze.router)
router.include_router(extract.router)
router.include_router(tailor.router)
router.include_router(health.router)