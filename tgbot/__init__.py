from aiogram import Router

from .handlers import router as handlers_router
from .callback_handlers import router as callback_handlers_router

router = Router()
router.include_routers(callback_handlers_router, handlers_router)