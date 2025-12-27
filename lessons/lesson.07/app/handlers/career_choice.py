import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.keyboards.builders import make_row_keyboard
from app.states.career_choice import CareerChoice
from app.models.career_profile import CareerProfile
from app.services.career_catalog import get_jobs, get_grades

router = Router()

available_jobs = get_jobs()

available_grades = get_grades()


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
    selected_job = data.get('profession') or 'Не выбрано'

    # id  пользователя
    user = message.from_user
    user_id = user.id if user else 0

    profile = CareerProfile(
        user_id=user_id,
        profession=selected_job,
        grade=selected_grade,
    )

    result_text = profile.to_message()

    await message.answer(result_text)
    await state.clear()


@router.message(CareerChoice.grade)
async def grade_invalid_input(message: types.Message, state: FSMContext):
    grade_keyboard = make_row_keyboard(available_grades)
    await message.answer('Пожалуйста, выберите уровень кнопкой ниже: ', reply_markup=grade_keyboard)
