from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_faq_keyboard(faq_item: dict[str, str]) -> InlineKeyboardMarkup:
    keyboard_row_faq = []

    for item, question_text in faq_item.items():
        keyboard_row_faq.append(
            [InlineKeyboardButton(
                text=question_text,
                callback_data=f"faq_{item}"
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard_row_faq)




ask_gpt_button = InlineKeyboardButton(text="Спросить у GPT", callback_data="demo_ask_gpt")
ask_yandex_button = InlineKeyboardButton(text="Спросить у Yandex", callback_data="demo_ask_yandex")

keyboard_row = [
    [ask_gpt_button, ask_yandex_button]
]

demo_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_row)


