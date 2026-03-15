from aiogram import Router

from .common import router as common_router
from .response_mode import router as response_mode_router
from .bot_message import router as bot_message_router


root_router = Router()
root_router.include_router(common_router)
root_router.include_router(response_mode_router)
root_router.include_router(bot_message_router)


__all__ = ["root_router"]