from aiogram import Router

from app.handlers.common import router as command_router
from app.handlers.bot_message import router as message_router
from app.handlers.bot_photo import router as photo_router
from app.handlers.call_back_handlers import router as callback_router
from app.handlers.career_choice import router as prof_router


root_router = Router()

root_router.include_router(command_router)
root_router.include_router(prof_router)
root_router.include_router(photo_router)
root_router.include_router(message_router)
root_router.include_router(callback_router)

__all__ = ["root_router"]