from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
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
    price = State()
    grade = State()



@router.message(Command('prof'))
async def prof_start(message: types.Message, state: FSMContext):
    await state.clear()

    await state.set_state(CareerChoice.job)

    job_keyboard = make_row_keyboard(available_jobs)
    await message.answer("Выберите профессию:", reply_markup=job_keyboard)


@router.message(CareerChoice.job, F.text.in_(available_jobs))
async def job_selected(message: types.Message, state: FSMContext):
    selected_job = message.text
    await message.answer(f"Ты выбрал {selected_job}")

    await state.update_data(proffesion=selected_job)
    await state.set_state(CareerChoice.grade)

    grade_keyboard = make_row_keyboard(available_grades)
    await message.answer("Выберите уровень:", reply_markup=grade_keyboard)


@router.message(CareerChoice.job)
async def job_invalid_input(message: types.Message):
    job_keyboard = make_row_keyboard(available_jobs)
    await message.answer("Пожалуйста, выберите профессию кнопкой ниже:", reply_markup=job_keyboard)


@router.message(CareerChoice.grade, F.text.in_(available_grades))
async def grade_selected(message: types.Message, state: FSMContext):
    selected_grade = message.text
    await message.answer(f"Ты выбрал {selected_grade}")

    await state.update_data(grade=selected_grade)
    await state.set_state(CareerChoice.price)

    # grade_keyboard = make_row_keyboard(available_grades)
    await message.answer("Введите желаемую зарплату:", reply_markup=types.ReplyKeyboardRemove())


@router.message(CareerChoice.grade)
async def grade_invalid_input(message: types.Message):
    grade_keyboard = make_row_keyboard(available_grades)
    await message.answer("Пожалуйста, выберите уровень кнопкой ниже:", reply_markup=grade_keyboard)


@router.message(CareerChoice.price)
async def price_selected(message: types.Message, state: FSMContext):
    input_price = message.text
    await message.answer(f"Ты хочешь {input_price} рублей")

    data = await state.get_data()

    job = data.get('proffesion')
    grade = data.get('grade')

    result_text = f"""
    Итого  ты выбрал:
    Профессия - {job}
    Уровень - {grade}
    Оплата - {input_price}
"""

    await message.answer(result_text)

    await state.clear()

    await message.answer(
        "Напишите, зачем вам эта профессия",
        reply_markup=types.ForceReply(selective=True)
    )


@router.message(F.text, F.reply_to_message.text == "Напишите, зачем вам эта профессия")
async def reply_to_message_prof(message: types.Message):
    user_goal = message.text
    await message.answer(f"Спасибо, Мы записали ваш интерес {user_goal}")


# @router.message(StateFilter(None))
# async def echo_message_filter(message: types.Message):
#     user_text = message.text
#     if user_text is None:
#         await message.answer("Отправьте акое-то сообщение")
#         return
#
#     await message.answer(user_text)