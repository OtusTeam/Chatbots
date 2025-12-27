from aiogram import Router

from .common import router as common_router
from .career_choice import router as career_choice_router
from .menu import router as menu_router
from .bot_message import router as bot_message_router


root_router = Router()
root_router.include_router(common_router)
root_router.include_router(career_choice_router)
root_router.include_router(menu_router)
root_router.include_router(bot_message_router)


__all__ = ["root_router"]