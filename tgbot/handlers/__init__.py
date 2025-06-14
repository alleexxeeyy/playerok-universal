from aiogram import Router

from .user_handlers import router as user_handlers_router

router = Router()
 
router.include_router(user_handlers_router)