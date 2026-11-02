from aiogram import Router

from .handlers import router as handlers_router
from .handlers.setup import router as setup_router
from .callback_handlers import router as callback_handlers_router


router = Router()
router.include_routers(setup_router, callback_handlers_router, handlers_router) # настройка первой — в режиме настройки перехватывает остальное