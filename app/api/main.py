from .routes import strings

from fastapi import APIRouter

router = APIRouter()
router.include_router(strings.router)