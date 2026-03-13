
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def start_user_usage():
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Мои слова", callback_data="my_words")],
        [InlineKeyboardButton(text="🧠 Тренировка", callback_data="exercise")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")]
    ])

    return keyboard

async def statistic_back():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")],
    ])

    return keyboard

async def manage_words():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Просмотр слов", callback_data="watch_words")],
        [InlineKeyboardButton(text="✏️ Редактирование слов", callback_data="edit_word")],
        [InlineKeyboardButton(text="➕ Добавить новое слово", callback_data="add_word")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")],
    ])

    return keyboard 

async def watch_words_after():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Просмотр слов", callback_data="watch_words")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")],
    ])

    return keyboard 

async def change_words_after():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактирование слов", callback_data="edit_word")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")],
    ])

    return keyboard 

async def generate_words_view_page(words_list, current_page, page_size):
    
    text = "📚 Ваши слова:                                                 \n\n"

    start_index = (current_page - 1) * page_size
    end_index = min(len(words_list), current_page * page_size)

    for ind in range(start_index, end_index):
        eng, rus = words_list[ind]
        text += f"{ind+1}. 📘 *{eng}* — _{rus}_\n"

    max_page = (len(words_list) - 1) // page_size + 1

    buttons = [
        InlineKeyboardButton(text="◀️ Назад", callback_data="page_previous_view"),
        InlineKeyboardButton(text=f"📃 {current_page}/{max_page}", callback_data="no_action"),
        InlineKeyboardButton(text="▶️ Вперед", callback_data="page_next_view")
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            buttons,  # первая строка — все варианты ответа
            [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")] 
        ])

    return text, keyboard

async def generate_words_edit_page(words_list, current_page, page_size):
    text = "📚 Выберите слова для редактирования:                                   \n\n"

    start_index = (current_page - 1) * page_size
    end_index = min(len(words_list), current_page * page_size)

    buttons_choice = []

    for ind in range(start_index, end_index):
        eng, rus = words_list[ind]
        text += f"{ind+1}. 📘 *{eng}* — _{rus}_\n"
        buttons_choice.append([
            InlineKeyboardButton(text=f"✏️ Изменить №{ind + 1}", callback_data=f"redact_word::{ind}"),
            InlineKeyboardButton(text=f"🗑 Удалить №{ind + 1}", callback_data=f"delete_word::{ind}")
        ])

    max_page = (len(words_list) - 1) // page_size + 1

    

    buttons = [
        InlineKeyboardButton(text="◀️ Назад", callback_data="page_previous_edit"),
        InlineKeyboardButton(text=f"📃 {current_page}/{max_page}", callback_data="no_action"),
        InlineKeyboardButton(text="▶️ Вперед", callback_data="page_next_edit")
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons_choice + [
            buttons,  # строка с пагинацией
            [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
        ]
    )

    return text, keyboard

async def redact_words_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏ Английское слово", callback_data="edit_field::eng")],
        [InlineKeyboardButton(text="📝 Перевод", callback_data="edit_field::rus")],
        [InlineKeyboardButton(text="🔄 Оба варианта", callback_data="edit_field::both")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_words")]
    ])
    
    return keyboard

async def type_word_watch():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новые слова", callback_data="view_words_new")],
        [InlineKeyboardButton(text="✅ Выученные слова", callback_data="view_words_know")],
        [InlineKeyboardButton(text="📜 Все слова", callback_data="view_words_all")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])
    
    return keyboard 

async def type_word_change():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новые слова", callback_data="change_words_new")],
        [InlineKeyboardButton(text="✅ Выученные слова", callback_data="change_words_know")],
        [InlineKeyboardButton(text="📜 Все слова", callback_data="change_words_all")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])
    
    return keyboard 

async def add_word_after():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить новое слово", callback_data="add_word")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")],
    ])

    return keyboard 

async def type_word_exercise():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новые слова", callback_data="training_new_words")],
        [InlineKeyboardButton(text="✅ Выученные слова", callback_data="training_know_words")],
        [InlineKeyboardButton(text="📜 Все слова", callback_data="training_all_words")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])

    return keyboard 

async def mode_exercise():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Викторина", callback_data="mode_quiz")],
        [InlineKeyboardButton(text="✍️ Проверка написания", callback_data="mode_spelling")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])

    return keyboard 

async def language_exercise():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 ➡️ 🇷🇺 Перевод с английского", callback_data="lang_eng_to_rus")],
        [InlineKeyboardButton(text="🇷🇺 ➡️ 🇬🇧 Перевод с русского", callback_data="lang_rus_to_eng")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])

    return keyboard 

async def prepare_exercise():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать тренировку", callback_data="start_training")],
        [InlineKeyboardButton(text="⚙️ Настроить заново", callback_data="exercise")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])

    return keyboard 

async def absence_data_exercise():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Настроить заново", callback_data="exercise")],
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]
    ])

    return keyboard 

async def answer_task_quiz(words):

    
    
    buttons = []

    for ind, word in enumerate(words):
        buttons.append([InlineKeyboardButton(text=f"{word[1]}", callback_data=f"word_answer_{ind}")])


    buttons.append([InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard 

async def answer_task_spelling():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")],
    ])

    return keyboard

async def show_answer_options():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Учить", callback_data="option_new_word"),
             InlineKeyboardButton(text="✅ Знаю", callback_data="option_know_word")],  # первая строка — все варианты ответа
            [InlineKeyboardButton(text="🏠 Вернуться в начало", callback_data="back_to_main")]  # вторая строка — отдельная кнопка
        ])
    
    return keyboard