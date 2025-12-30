from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb():
    buttons = [
        [InlineKeyboardButton(text="Generate User", callback_data="gen_user")],
        [InlineKeyboardButton(text="Home", callback_data="back_home")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# questions = {
#     1: {"qst": "Capital of Italy?", "answer": "Rome"},
#     2: {"qst": "How many continents are there on Earth?", "answer": "Seven"},
#     3: {"qst": "Longest river in the world?", "answer": "Nile"},
#     4: {"qst": 'Which element is denoted by the symbol "O"?', "answer": "Oxygen"},
#     5: {
#         "qst": 'What is the name of the main character in the book "Harry Potter"?',
#         "answer": "Harry Potter",
#     },
#     6: {"qst": "How many colors are in a rainbow?", "answer": "Seven"},
#     7: {"qst": "Which planet is third from the Sun?", "answer": "Earth"},
#     8: {"qst": 'Who wrote "War and Peace"?', "answer": "Leo Tolstoy"},
#     9: {"qst": "What is H2O?", "answer": "Water"},
#     10: {"qst": "Which ocean is the largest?", "answer": "Pacific Ocean"},
# }


# def create_qst_kb():
#     builder = InlineKeyboardBuilder()

#     for qst_id, qst_data in questions.items():
#         builder.row(
#             InlineKeyboardButton(text=qst_data["qst"], callback_data=f"qst_{qst_id}")
#         )

#     builder.row(InlineKeyboardButton(text="Home", callback_data="back_home"))

#     builder.adjust(1)

#     return builder.as_markup()
