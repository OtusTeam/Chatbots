"""Корневой роутер: подключение всех обработчиков."""
from aiogram import Router

from app.handlers.rag import router as rag_router

root_router = Router()
root_router.include_router(rag_router)

__all__ = ["root_router"]
