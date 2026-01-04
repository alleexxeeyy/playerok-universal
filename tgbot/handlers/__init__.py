from aiogram import Router

from .commands import router as commands_router

from .states_actions import router as states_actions_router
from .states_system import router as states_system_router
from .states_settings import router as states_settings_router
from .states_messages import router as states_messages_router
from .states_restore import router as states_restore_router
from .states_bump import router as states_bump_router
from .states_comms import router as states_comms_router
from .states_delivs import router as states_delivs_router


router = Router()
router.include_routers(
    commands_router,
    states_actions_router,
    states_system_router,
    states_settings_router,
    states_messages_router,
    states_restore_router,
    states_bump_router,
    states_comms_router,
    states_delivs_router
)