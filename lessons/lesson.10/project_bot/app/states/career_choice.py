from aiogram.fsm.state import State, StatesGroup


class CareerChoice(StatesGroup):
    job = State()
    price = State()
    grade = State()


__all__ = ["CareerChoice"]
