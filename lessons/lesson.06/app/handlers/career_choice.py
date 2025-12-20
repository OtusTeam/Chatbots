import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.keyboards.builders import make_row_keyboard


router = Router()

available_jobs = [
    'Программист',
    'Менеджер',
    'Дизайнер',
    'Маркетолог',
]

available_grades = [
    'Junior',
    'Middle',
    'Senior',
]


class CareerChoice(StatesGroup):
    job = State()
    grade = State()


@router.message(Command('prof'))
async def prof_start(message: types.Message, state: FSMContext):
    await state.clear()

    await state.set_state(CareerChoice.job)

    job_keyboard = make_row_keyboard(available_jobs)
    await message.answer('Выберите профессию: ', reply_markup=job_keyboard)


@router.message(CareerChoice.job, F.text.in_(available_jobs))
async def job_selected(message: types.Message, state: FSMContext):
    selected_job = message.text

    await state.update_data(profession=selected_job)
    await state.set_state(CareerChoice.grade)

    grade_keyboard = make_row_keyboard(available_grades)

    await message.answer(f'Теперь выберите уровень', reply_markup=grade_keyboard)


@router.message(CareerChoice.job)
async def job_invalid_input(message: types.Message, state: FSMContext):
    job_keyboard = make_row_keyboard(available_jobs)
    await message.answer('Пожалуйста, выберите профессию кнопкой ниже: ', reply_markup=job_keyboard)


@router.message(CareerChoice.grade, F.text.in_(available_grades))
async def grade_selected(message: types.Message, state: FSMContext):
    selected_grade = message.text
    data = await state.get_data()
    selected_job = data.get('profession')

    result_text = f'Итого: профессия {selected_job}, уровень - {selected_grade}'

    await message.answer(result_text)
    await state.clear()


@router.message(CareerChoice.grade)
async def grade_invalid_input(message: types.Message, state: FSMContext):
    grade_keyboard = make_row_keyboard(available_grades)
    await message.answer('Пожалуйста, выберите уровень кнопкой ниже: ', reply_markup=grade_keyboard)
