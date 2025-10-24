from aiogram import Router

from .actions import router as actions_router
from .navigation import router as navigation_router

router = Router()
router.include_routers(actions_router, navigation_router)