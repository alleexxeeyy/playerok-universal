from aiogram import Router

from .main_callback_handlers import router as main_callback_router

router = Router()
 
router.include_router(main_callback_router)