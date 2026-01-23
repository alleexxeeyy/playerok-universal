from aiogram import Router

from .navigation import router as navigation_router
from .pagination import router as pagination_router
from .page import router as page_router

from .actions_enter import router as actions_enter_router
from .actions_switch import router as actions_switch_router
from .actions_other import router as actions_other_router
from .actions_confirm import router as actions_confirm_router


router = Router()
router.include_routers(
    navigation_router,
    pagination_router,
    page_router,
    actions_enter_router,
    actions_switch_router,
    actions_other_router,
    actions_confirm_router
)