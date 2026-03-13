from aiogram import Router, F
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext  
from aiogram.fsm.state import State, StatesGroup

import random



from keyboards import (
    start_user_usage,
    manage_words,
    add_word_after,
    type_word_exercise,
    mode_exercise,
    language_exercise,
    prepare_exercise,
    absence_data_exercise,
    answer_task_quiz,
    show_answer_options,
    statistic_back,
    answer_task_spelling,
    type_word_watch,
    watch_words_after,
    generate_words_view_page,
    generate_words_edit_page,
    type_word_change,
    change_words_after,
    redact_words_menu
)

from database.db import (
    add_word,
    delete_word,
    get_words,
    save_word,
    create_statistic,
    check_words,
    data_statistic,
    update_statistic,
    get_words_by_type,
    update_word
)


user_router = Router()

class WordForm(StatesGroup):
    english_word = State()  # Ожидаем английское слово
    russian_word = State()  # Ожидаем русский перевод

class EditWord(StatesGroup):
    waiting_for_eng = State()
    waiting_for_rus = State()
    waiting_for_both = State()

class WordReception(StatesGroup):
    lang_word = State() # Ожидаем ответ пользователя

@user_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    keyboard = await start_user_usage()
    await create_statistic(message.from_user.id)

    await message.answer(
        "Привет! 👋 Я помогу тебе выучить английские слова! 📚\n\n"
        "Выбери, что ты хочешь сделать:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@user_router.callback_query(F.data == "back_to_main")
async def go_main(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    keyboard = await start_user_usage()

    await callback_query.message.edit_text(
        "Привет! 👋 Я помогу тебе выучить английские слова! 📚\n\n"
        "Выбери, что ты хочешь сделать:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()

@user_router.callback_query(F.data == "statistics")
async def view_statistic(callback_query: types.CallbackQuery):
    total_words, new_words, know_words = await check_words()
    total_answer, correct_answer, last_train = await data_statistic(callback_query.from_user.id)

    keyboard = await statistic_back()

    last_training_text = (
        f"⏰ Последняя тренировка: {last_train.strftime('%d-%m-%Y %H:%M')}"
        if last_train
        else "⏰ Последняя тренировка: пока нет данных"
    )
    percentage = round((correct_answer / total_answer * 100), 2) if total_answer > 0 else 0

    text = (
        "📊 Ваша статистика:\n\n"
        f"📚 Всего слов: {total_words}\n"
        f"🆕 Новых слов: {new_words}\n"
        f"✔️ Выучено слов: {know_words}\n\n"
        f"✅ Правильных ответов: {correct_answer}\n"
        f"❓ Всего ответов: {total_answer}\n"
        f"📈 Процент правильных ответов: {percentage}%\n\n"
        f"{last_training_text}"
    )

    await callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback_query.answer()

@user_router.callback_query(F.data == "no_action")
async def no_action_but(callback_query:types.CallbackQuery):

    await callback_query.answer()


@user_router.callback_query(F.data == "my_words")
async def words_manage(callback_query: types.CallbackQuery):

    keyboard = await manage_words()

    await callback_query.message.edit_text(
        "📚 Мои слова\n\n"
        "Здесь ты можешь работать со своими словами и улучшать знания. 🧠\n\n"
        "Выбери, что ты хочешь сделать:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()

@user_router.callback_query(F.data == "watch_words")
async def watch_words(callback_query: types.CallbackQuery):

    keyboard = await type_word_watch()

    await callback_query.message.edit_text(
        "📚 *Просмотр слов*\n\n"
        "Выберите категорию слов, которую хотите просмотреть. Это поможет вам лучше ориентироваться в своем словарном запасе! 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()

@user_router.callback_query(F.data.startswith("view_words"))
async def view_type_words(callback_query: types.CallbackQuery, state: FSMContext):
    type_word = callback_query.data.split('_')[-1]
    
    words_list = await get_words_by_type(type_word)
    
    if not words_list:
        keyboard = await watch_words_after()
        await callback_query.message.edit_text(
            "😕 Слов с таким статусом для просмотра пока нет.",
            reply_markup = keyboard 
        )
        await callback_query.answer()
        return
    
    page_size = 10
    

    await state.update_data(
        words_list = words_list,
        current_page = 1,

    )

    text, keyboard = await generate_words_view_page(words_list=words_list, current_page=1, page_size=page_size)
    
    await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup = keyboard 
        )
    
    await callback_query.answer()

@user_router.callback_query(F.data == "back_to_words")
@user_router.callback_query(F.data.startswith("page"))
async def switch_page(callback_query: types.CallbackQuery, state: FSMContext):
    
    state_data = await state.get_data()
    words_list = state_data.get("words_list")
    current_page = state_data.get("current_page")

    choice = callback_query.data.split("_")[-1]
    
    if choice == "edit":
        page_size = 3
    elif choice == "view": #view
        page_size = 10
    else:
        page_size = 3
    
    max_page = (len(words_list) - 1) // page_size + 1

    if current_page == max_page == 1:
        
        await callback_query.answer()
        return 
    action = callback_query.data.split("_")[-2]

    
    if action == "previous":
        current_page -= 1
        if current_page == 0:
            current_page = max_page

    elif action == "next":
        current_page += 1
        if current_page > max_page:
            current_page = 1
    
    
    await state.update_data(current_page=current_page)

    if choice == "edit" or choice == "words":
        text, keyboard = await generate_words_edit_page(words_list=words_list, current_page=current_page, page_size=page_size)
    else: #view
        text, keyboard = await generate_words_view_page(words_list=words_list, current_page=current_page, page_size=page_size)


    await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup = keyboard 
        )


    await callback_query.answer()


@user_router.callback_query(F.data == "edit_word")
async def edit_words(callback_query: types.CallbackQuery):

    keyboard = await type_word_change()

    await callback_query.message.edit_text(
        "✏️ *Редактирование слов*\n\n"
        "Какой тип слов вы хотите редактировать?\n"
        "Выберите категорию ниже, чтобы перейти к изменениям. 🔧",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback_query.answer()

@user_router.callback_query(F.data.startswith("change_words"))
async def change_type_words(callback_query: types.CallbackQuery, state:FSMContext):
    type_word = callback_query.data.split('_')[-1]
    
    words_list = await get_words_by_type(type_word)
    
    if not words_list:
        keyboard = await change_words_after()
        await callback_query.message.edit_text(
            "😕 Слов с таким статусом для редактирования пока нет.",
            reply_markup = keyboard 
        )
        await callback_query.answer()
        return
    
    page_size = 3
    

    await state.update_data(
        words_list = words_list,
        current_page = 1,

    )

    text, keyboard = await generate_words_edit_page(words_list=words_list, current_page=1, page_size=page_size)
    
    await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup = keyboard 
        )
    
    await callback_query.answer()

@user_router.callback_query(F.data.startswith("delete_word"))
async def word_delete(callback_query: types.CallbackQuery, state: FSMContext):
    _, ind = callback_query.data.split("::")
    state_data = await state.get_data()

    words_list = state_data.get("words_list")

    eng_word, rus_word = words_list[int(ind)]

    await delete_word(eng_word, rus_word)
    
    

    if (eng_word, rus_word) in words_list:
        words_list.remove((eng_word, rus_word))

    if not words_list:
        keyboard = await change_words_after()
        await callback_query.message.edit_text(
            "😕 Слов с таким статусом для редактирования пока нет.",
            reply_markup = keyboard 
        )
        await callback_query.answer()
        return
    
    page_size = 3
    max_page = (len(words_list) - 1) // page_size + 1
    
    current_page = state_data.get("current_page")
    if current_page > max_page:
        current_page -= 1
    

    text, keyboard = await generate_words_edit_page(words_list=words_list, current_page=current_page, page_size=page_size)
    
    await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup = keyboard 
        )
    
    await callback_query.answer()

@user_router.callback_query(F.data.startswith("redact_word"))
async def word_redact(callback_query: types.CallbackQuery, state: FSMContext):
    _, ind = callback_query.data.split("::")
    
    state_data = await state.get_data()
    words_list = state_data.get("words_list")

    eng_word, rus_word = words_list[int(ind)]
    
    await state.update_data(old_eng=eng_word, old_rus=rus_word)

    keyboard = await redact_words_menu()
    text = (
        f"📘 *Слово:* {eng_word}\n"
        f"📗 *Перевод:* {rus_word}\n\n"
        f"✏ Выберите, что вы хотите изменить:"
    )
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard 
    )
    await callback_query.answer()

@user_router.callback_query(F.data.startswith("edit_field"))
async def editing_words(callback_query: types.CallbackQuery, state: FSMContext):
    _, type_edit = callback_query.data.split("::")

    state_data = await state.get_data()

    eng_word = state_data.get("old_eng")
    rus_word = state_data.get("old_rus")

    if type_edit == "eng":
        text = (
            f"📘 *Слово:* {eng_word}\n"
            f"📗 *Перевод:* {rus_word}\n\n"
            f"📝 Укажите *новое английское слово* вместо: {eng_word}"
        )
        await state.set_state(EditWord.waiting_for_eng)

    elif type_edit == "rus":
        text = (
            f"📘 *Слово:* {eng_word}\n"
            f"📗 *Перевод:* {rus_word}\n\n"
            f"📝 Укажите *новый перевод* для слова: {eng_word}"
        )
        await state.set_state(EditWord.waiting_for_rus)

    else:  # both
        text = (
            f"📘 *Слово:* {eng_word}\n"
            f"📗 *Перевод:* {rus_word}\n\n"
            f"🔄 Укажите *новое английское слово и перевод* в формате:\n"
            f"английское::перевод\n\n"
            f"Пример: evolve::развиваться"
        )
        await state.set_state(EditWord.waiting_for_both)

    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown"
    )

    await callback_query.answer()

@user_router.message(EditWord.waiting_for_eng)
async def edit_eng_word(message: types.Message, state: FSMContext):
    new_word = " ".join(message.text.lower().split())

    state_data = await state.get_data()

    for letter in new_word:
        if (ord(letter) < 97 or ord(letter) > 122) and letter not in [" ", "-", ",", "/", "(", ")"]:
            await message.answer(
                "Пожалуйста, используйте только английские буквы (a-z), тире, запятые или пробелы. 🧐\n\n"
                "🔁 Введите *новое английское слово* ещё раз:",
                parse_mode="Markdown"
            )
            
            return
        
    old_eng = state_data.get("old_eng")
    old_rus = state_data.get("old_rus")

    answer = await update_word(old_eng, old_rus, new_word, old_rus)

    if answer:
        keyboard = await redact_words_menu()
        await message.answer(
            f"⚠️ Невозможно внести изменения.\n\n"
            f"Слово *{new_word}* уже существует в базе данных с тем же или другим переводом.\n\n"
            f"**Английское слово**: *{answer['english_word']}*\n"
            f"**Русский перевод**: *{answer['russian_word']}*\n\n"
            "Пожалуйста, выбери другое слово или сначала измени эту пару.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return  
    
    await state.update_data(old_eng=new_word)

    keyboard = await redact_words_menu()

    words_list = state_data.get("words_list")
    try:

        ind = words_list.index((old_eng, old_rus))
        words_list[ind] = ((new_word, old_rus))
        await state.update_data(words_list=words_list)
    except:
        pass

    await message.answer(
        f"✅ Изменения прошли успешно!\n\n"
        f"📘 *Слово:* {new_word}\n"
        f"📗 *Перевод:* {old_rus}\n\n"
        f"✏ Вы можете продолжить редактирование или выбрать другое действие.",
        parse_mode="Markdown",
        reply_markup=keyboard 
    )

@user_router.message(EditWord.waiting_for_rus)
async def edit_rus_word(message: types.Message, state: FSMContext):
    new_word = " ".join(message.text.lower().split())

    state_data = await state.get_data()

    for letter in new_word:
        if (ord(letter) < 1072 or ord(letter) > 1103) and letter not in [" ", "-", ",", "/", "(", ")"]:
            await message.answer(
                "Пожалуйста, используйте только русские буквы (а-я), тире, запятые или пробелы. 🧐\n\n"
                "🔁 Введите *новый перевод* ещё раз:",
                parse_mode="Markdown"
            )
            return
        
    old_eng = state_data.get("old_eng")
    old_rus = state_data.get("old_rus")

    answer = await update_word(old_eng, old_rus, old_eng, new_word)

    if answer:
        keyboard = await redact_words_menu()
        await message.answer(
            f"⚠️ Невозможно внести изменения.\n\n"
            f"Слово *{new_word}* уже существует в базе данных с тем же или другим переводом.\n\n"
            f"**Английское слово**: *{answer['english_word']}*\n"
            f"**Русский перевод**: *{answer['russian_word']}*\n\n"
            "Пожалуйста, выбери другое слово или сначала измени эту пару.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return  
    
    await state.update_data(old_rus=new_word)

    keyboard = await redact_words_menu()

    words_list = state_data.get("words_list")
    try:

        ind = words_list.index((old_eng, old_rus))
        words_list[ind] = ((old_eng, new_word))
        await state.update_data(words_list=words_list)
    except:
        pass
    
    await message.answer(
        f"✅ Изменения прошли успешно!\n\n"
        f"📘 *Слово:* {old_eng}\n"
        f"📗 *Перевод:* {new_word}\n\n"
        f"✏ Вы можете продолжить редактирование или выбрать другое действие.",
        parse_mode="Markdown",
        reply_markup=keyboard 
    )
    
@user_router.message(EditWord.waiting_for_both)
async def edit_both_word(message: types.Message, state: FSMContext):
    parts = message.text.lower().strip().split("::")

    if len(parts) != 2:
        await message.answer(
            "⚠️ Пожалуйста, введите слово и перевод в формате:\n"
            "*английское::перевод*\n\n"
            "Пример: evolve::развиваться",
            parse_mode="Markdown"
        )
        return
    
    eng_word, rus_word = parts

    state_data = await state.get_data()

    for letter in eng_word:
        if (ord(letter) < 97 or ord(letter) > 122) and letter not in [" ", "-", ",", "/", "(", ")"]:
            await message.answer(
                "Пожалуйста, используйте только английские буквы (a-z), тире, запятые или пробелы для английского слова. 🧐\n\n"
                "🔁 Введите снова в формате: *английское::перевод*",
                parse_mode="Markdown"
            )
            return
        
    for letter in rus_word:
        if (ord(letter) < 1072 or ord(letter) > 1103) and letter not in [" ", "-", ",", "/", "(", ")"]:
            await message.answer(
                "Пожалуйста, используйте только русские буквы (а-я), тире, запятые или пробелы для русского слова. 🧐\n\n"
                "🔁 Введите снова в формате: *английское::перевод*",
                parse_mode="Markdown"
            )
            return
        
    old_eng = state_data.get("old_eng")
    old_rus = state_data.get("old_rus")

    answer = await update_word(old_eng, old_rus, eng_word, rus_word)

    if answer:
        keyboard = await redact_words_menu()
        await message.answer(
            f"⚠️ Невозможно внести изменения.\n\n"
            f"Слово *{eng_word}* или *{rus_word}* уже существует в базе данных с тем же или другим переводом.\n\n"
            f"**Английское слово**: *{answer['english_word']}*\n"
            f"**Русский перевод**: *{answer['russian_word']}*\n\n"
            "Пожалуйста, выбери другое слово или сначала измени эту пару.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return  
    
    await state.update_data(old_eng=eng_word, old_rus=rus_word)

    keyboard = await redact_words_menu()

    words_list = state_data.get("words_list")
    try:

        ind = words_list.index((old_eng, old_rus))
        words_list[ind] = ((eng_word, rus_word))
        await state.update_data(words_list=words_list)
    except:
        pass
    
    await message.answer(
        f"✅ Изменения прошли успешно!\n\n"
        f"📘 *Слово:* {eng_word}\n"
        f"📗 *Перевод:* {rus_word}\n\n"
        f"✏ Вы можете продолжить редактирование или выбрать другое действие.",
        parse_mode="Markdown",
        reply_markup=keyboard 
    )

@user_router.callback_query(F.data == "add_word")
async def word_add(callback_query: types.CallbackQuery, state: FSMContext):

    await state.set_state(WordForm.english_word)

    await callback_query.message.answer(
        "Давай добавим новое слово! 📝\n\n"
        "Для начала, введи слово на английском языке. ✍️"
    )

    await callback_query.answer()

@user_router.message(WordForm.english_word)
async def word_eng_reception(message: types.Message, state: FSMContext):

    word = " ".join(message.text.lower().split())

    for letter in word:
        if (ord(letter) < 97 or ord(letter) > 122) and letter not in [" ", "-", ",", "/", "(", ")"]:
            await message.answer(
                "Пожалуйста, используйте только английские буквы (a-z), тире, запятые или пробелы. 🧐\n\n"
                "🔁 Введите *новое английское слово* ещё раз:",
                parse_mode="Markdown"
            )
            return
    
    await state.update_data(english_word=word)

    await state.set_state(WordForm.russian_word)

    await message.answer("Отлично! Теперь, напишите перевод этого слова на русском языке. 🤓")

@user_router.message(WordForm.russian_word)
async def word_ru_reception(message: types.Message, state: FSMContext):
    rus_word = " ".join(message.text.lower().split())

    for letter in rus_word:
        if (ord(letter) < 1072 or ord(letter) > 1103) and letter not in [" ", "-", ",", "/", "(", ")"]:
            await message.answer(
                "Пожалуйста, используйте только русские буквы (а-я), тире, запятые или пробелы. 🧐\n\n"
                "🔁 Введите *новый перевод* ещё раз:",
                parse_mode="Markdown"
            )
            return

    keyboard = await add_word_after()
    
    state_data = await state.get_data()
    eng_word = state_data.get("english_word")

    if not eng_word:
        await message.answer(
            "Не удалось найти английское слово. Пожалуйста, начни ввод слова заново. ✍️",
            parse_mode="Markdown",
            reply_markup=await keyboard  # Добавьте свою клавиатуру здесь
        )


    await state.clear()

    answer = await add_word(eng_word, rus_word)

    if not answer:
        await message.answer(
            f"Поздравляем! 🎉 Перевод успешно добавлен! Теперь у тебя есть новая пара:\n\n"
            f"**Английское слово:** *{eng_word}*\n"
            f"**Русский перевод:** *{rus_word}*\n\n",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    else:

        await message.answer(
            f"⚠️ Такое слово уже есть в базе данных.\n\n"
            f"**Найденная пара:**\n"
            f"**Английское слово:** *{answer['english_word']}*\n"
            f"**Русский перевод:** *{answer['russian_word']}*\n\n"
            f"Если ты хочешь изменить перевод или само слово — можешь редактировать слово.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

@user_router.callback_query(F.data == "exercise")
async def exercise_manage(callback_query: types.CallbackQuery):
    

    keyboard = await type_word_exercise()

    await callback_query.message.edit_text(
        "Готов к тренировке? 💪\n\n"
        "Выбери, какие слова ты хочешь тренировать, чтобы начать 🧠:\n\n",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()

@user_router.callback_query(F.data.startswith("training"))
async def exercise_type(callback_query: types.CallbackQuery, state: FSMContext):

    type_word_training = callback_query.data.split("_", 1)[1]

    if type_word_training == "new_words":
        type_word_training = "🆕 Новые слова"
    elif type_word_training == "know_words":
        type_word_training = "✅ Выученные слова"
    elif type_word_training == "all_words":
        type_word_training = "📜 Все слова"
    
    await state.update_data(type_word_training=type_word_training)

    keyboard = await mode_exercise()

    await callback_query.message.edit_text(
        "Выбери режим тренировки, который тебе подходит! 🚀",
        parse_mode="Markdown",
        reply_markup=keyboard

    )

    await callback_query.answer()

@user_router.callback_query(F.data.startswith("mode"))
async def exercise_mode(callback_query: types.CallbackQuery, state: FSMContext):

    mode_training = callback_query.data.split("_", 1)[1]

    if mode_training == "quiz":
        mode_training = "📊 Викторина"
    elif mode_training == "spelling":
        mode_training = "✍️ Проверка написания"

    await state.update_data(mode_training=mode_training)

    keyboard = await language_exercise()

    await callback_query.message.edit_text(
        "Теперь выбери, как ты хочешь тренировать слова! 📝\n\n"
        "Выбери режим тренировки: с английского на русский или наоборот. 🌟",
        parse_mode="Markdown",
        reply_markup=keyboard

    )

    await callback_query.answer()

@user_router.callback_query(F.data.startswith("lang"))
async def final_exercise(callback_query: types.CallbackQuery, state: FSMContext):

    state_data = await state.get_data()

    lang_training = callback_query.data.split("_", 1)[1]

    if lang_training == "rus_to_eng":
        lang_training = "🇷🇺 ➡️ 🇬🇧 Перевод с русского"
    elif lang_training == "eng_to_rus":
        lang_training = "🇬🇧 ➡️ 🇷🇺 Перевод с английского"

    await state.update_data(lang_training=lang_training)

    type_word_training = state_data.get("type_word_training")
    mode_training = state_data.get("mode_training")

    if not all([lang_training, type_word_training, mode_training]):
        keyboard = await absence_data_exercise()

        await callback_query.message.edit_text(
            "⚠️ Похоже, некоторые настройки тренировки не выбраны.\n\n"
            "Пожалуйста, вернитесь назад и заполните все параметры. 🔧",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return

    keyboard = await prepare_exercise()

    await callback_query.message.edit_text(
        f"🔹 **Ваши настройки тренировки:**\n\n"
        f"📝 Тип слов: **{type_word_training}**\n"
        f"🎯 Режим: **{mode_training}**\n"
        f"🌍 Язык: **{lang_training}**\n\n"
        f"Если всё верно — нажмите «Начать тренировку»! 🚀",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()


@user_router.callback_query(F.data == "start_training")
async def start_training(callback_query: types.CallbackQuery, state:FSMContext):
    state_data = await state.get_data()

    type_word_training = state_data.get("type_word_training")
    mode_training = state_data.get("mode_training")
    lang_training = state_data.get("lang_training")
    if not all([lang_training, type_word_training, mode_training]):
        keyboard = await absence_data_exercise()

        await callback_query.message.edit_text(
            "⚠️ Похоже, некоторые настройки тренировки не выбраны.\n\n"
            "Пожалуйста, вернитесь назад и заполните все параметры. 🔧",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    words = await get_words(type_word_training, lang_training)
    
    
    await state.update_data(
        words=words,
        correct_answers=0,
        total_answers=0,
        used_words=[]
    )

   
    if mode_training == "✍️ Проверка написания":
        if not words:
            keyboard = await add_word_after()
        
            await callback_query.message.edit_text(
                "❌ У вас еще нет слов для тренировки! \n\n"
                "Добавьте новые слова, чтобы продолжить тренировку. ✍️📚\n"
                "Нажмите кнопку ниже, чтобы добавить слова! ➕",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        await send_spelling_task(callback_query, state)

    elif mode_training == "📊 Викторина":
        if len(words) < 3:
            keyboard = await add_word_after()
        
            await callback_query.message.edit_text(
                "❌ Для викторины необходимо хотя бы 3 слова! \n\n"
                "Добавьте новые слова, чтобы продолжить тренировку. ✍️📚\n"
                "Нажмите кнопку ниже, чтобы добавить слова! ➕",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        await send_quiz_task(callback_query, state)
    
    await callback_query.answer()

async def send_quiz_task(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    type_word_training = state_data.get("type_word_training")
    lang_training = state_data.get("lang_training")
    words = state_data.get("words")
    correct_answers = state_data.get("correct_answers")
    total_answers = state_data.get("total_answers")
    used_words = state_data.get("used_words")

    if len(used_words) == len(words):
        used_words = []
    
    if not all([lang_training, type_word_training, words, correct_answers is not None, total_answers is not None, used_words is not None]):
        keyboard = await absence_data_exercise()

        await callback_query.message.edit_text(
            "⚠️ Похоже, некоторые настройки тренировки не выбраны.\n\n"
            "Пожалуйста, вернитесь назад и заполните все параметры. 🔧",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    unused_words = [word for word in words if word not in used_words]
    correct_word = random.choice(unused_words)

    remaining_words = [word for word in words if word != correct_word]
    incorrect_words = random.sample(remaining_words, 2)

    words_for_quiz = [correct_word] + incorrect_words
    random.shuffle(words_for_quiz)
    
    await state.update_data(used_words=used_words + [correct_word])
    await state.update_data(correct_word=correct_word)
    await state.update_data(correct_ind=words_for_quiz.index(correct_word))

    keyboard = await answer_task_quiz(words_for_quiz)

    await callback_query.message.edit_text(
        f"❓ Выберите правильный вариант для слова:\n*{correct_word[0]}*\n\n"
        "Выберите один из вариантов ниже и нажмите на кнопку! ✅❌",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()

@user_router.callback_query(F.data.startswith("word_answer"))
async def word_answer_quiz(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    correct_answers = state_data.get("correct_answers")
    total_answers = state_data.get("total_answers")
    correct_word = state_data.get("correct_word")
    correct_ind = state_data.get("correct_ind")

    ind = callback_query.data.split('_')[-1]
    
    total_answers += 1

    keyboard = await show_answer_options()
    
    if int(ind) == int(correct_ind):
        correct_answers += 1
        await update_statistic(callback_query.from_user.id, 1, 1)
        answer_text = (
            "✅ Правильно!\n\n"
            "Отличная работа — так держать! 🚀\n\n"
        )
        
    else:
        await update_statistic(callback_query.from_user.id, 0, 1)
        answer_text = (
            "❌ Неправильно.\n\n"
            "Не переживайте — продолжайте тренироваться, и всё получится! 💪\n\n"
        )
        

    answer_text += (
        f"📚 Правильный перевод: {correct_word[0]} - {correct_word[1]}\n\n"
        f"📊 Правильных ответов: {correct_answers} / {total_answers}\n"
        "Теперь выберите, что делать с этим словом:\n"
        "🔄 Если хотите продолжить учить его, выберите 'Учить'.\n"
        "✔️ Если вы хотите отметить, что знаете это слово, выберите 'Знаю'."
    )
    
    await callback_query.message.edit_text(
        answer_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.update_data(correct_answers=correct_answers)
    await state.update_data(total_answers=total_answers)


    await callback_query.answer()

@user_router.callback_query(F.data.startswith("option"))
async def option_transfer(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    option = callback_query.data.split('_')[1] #learn, know
    correct_word = state_data.get("correct_word")
    lang_training = state_data.get("lang_training")
    mode_training = state_data.get("mode_training")

    if correct_word:
        await save_word(list(correct_word), option, lang_training)
    
    
    
    if mode_training == "📊 Викторина":
        await send_quiz_task(callback_query, state)
    elif mode_training == "✍️ Проверка написания":
        await send_spelling_task(callback_query, state)
    
    await callback_query.answer()
    

async def send_spelling_task(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    type_word_training = state_data.get("type_word_training")
    lang_training = state_data.get("lang_training")
    words = state_data.get("words")
    correct_answers = state_data.get("correct_answers")
    total_answers = state_data.get("total_answers")
    used_words = state_data.get("used_words")
    if len(used_words) == len(words):
        used_words = []
    
    if not all([lang_training, type_word_training, words, correct_answers is not None, total_answers is not None, used_words is not None]):
        keyboard = await absence_data_exercise()

        await callback_query.message.edit_text(
            "⚠️ Похоже, некоторые настройки тренировки не выбраны.\n\n"
            "Пожалуйста, вернитесь назад и заполните все параметры. 🔧",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    unused_words = [word for word in words if word not in used_words]
    correct_word = random.choice(unused_words)
    
    await state.update_data(used_words=used_words + [correct_word])
    await state.update_data(correct_word=correct_word)

    await state.set_state(WordReception.lang_word)

    keyboard = await answer_task_spelling()
    
    await callback_query.message.edit_text(
        f"✍️ Напишите перевод для слова:\n\n"
        f"📘 *{correct_word[0]}*",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await callback_query.answer()

@user_router.message(WordReception.lang_word)
async def word_answer_spelling(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    correct_answers = state_data.get("correct_answers")
    total_answers = state_data.get("total_answers")
    correct_word = state_data.get("correct_word")
    word = message.text.lower()

    total_answers += 1
    
    keyboard = await show_answer_options()

    if correct_word[1] == word:
        correct_answers += 1
        await update_statistic(message.from_user.id, 1, 1)
        answer_text = (
            "✅ Правильно!\n\n"
            "Отличная работа — так держать! 🚀\n\n"
        )
        
    else:
        await update_statistic(message.from_user.id, 0, 1)
        answer_text = (
            "❌ Неправильно.\n\n"
            "Не переживайте — продолжайте тренироваться, и всё получится! 💪\n\n"
        )

    answer_text += (
        f"📚 Правильный перевод: {correct_word[0]} - {correct_word[1]}\n\n"
        f"📊 Правильных ответов: {correct_answers} / {total_answers}\n"
        "Теперь выберите, что делать с этим словом:\n"
        "🔄 Если хотите продолжить учить его, выберите 'Учить'.\n"
        "✔️ Если вы хотите отметить, что знаете это слово, выберите 'Знаю'."
    )

    await message.answer(
        answer_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.update_data(correct_answers=correct_answers)
    await state.update_data(total_answers=total_answers)