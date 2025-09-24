from aiogram import Router

from .navigation import router as navigation_router
from .actions import router as actions_router

router = Router()
 
router.include_routers(navigation_router, actions_router)