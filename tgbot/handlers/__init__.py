from aiogram import Router

from .commands import router as commands_router
from .entering import router as entering_router

router = Router()
 
router.include_routers(commands_router, entering_router)