import asyncpg
from config import DATABASE_URL

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

pool = None

async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

async def create_statistic(tg_id):
    async with pool.acquire() as conn:
        conn = await connect_to_db()

        result = await conn.fetchrow("""
            SELECT * FROM statistics WHERE user_id = $1
        """, tg_id)

        if not result:
            # Если записи нет, создаем новую запись для пользователя
            await conn.execute("""
                INSERT INTO statistics (user_id, correct_answers, total_answers, last_training_date)
                VALUES ($1, 0, 0, NULL)
            """, tg_id)

    

async def check_words():
    async with pool.acquire() as conn:

        status = await conn.fetch("""
                SELECT status
                FROM words
            """)

        total_words = len(status)
        new_words = 0
        know_words = 0

        for elem in status:
            if elem['status'] == "new":
                new_words += 1
            elif elem['status'] == "know":
                know_words += 1


        return total_words, new_words, know_words

async def get_words_by_type(type_word):
    async with pool.acquire() as conn:
        if type_word == "all":
            type_word = None
        
        if type_word:
            words = await conn.fetch("""
                SELECT english_word, russian_word
                FROM words
                WHERE status = $1
                ORDER BY created_at DESC
            """, type_word)
        else:
            words = await conn.fetch("""
                SELECT english_word, russian_word
                FROM words
                ORDER BY created_at DESC
            """)

        words_list = [(word['english_word'], word['russian_word']) for word in words]

        return words_list

async def data_statistic(tg_id):
    async with pool.acquire() as conn:

        data = await conn.fetchrow("""
                SELECT * FROM statistics
                WHERE user_id = $1
            """, tg_id)

        return data['total_answers'], data['correct_answers'], data['last_training_date']

async def update_statistic(tg_id, correct_answers, total_answers):
    async with pool.acquire() as conn:

        await conn.execute("""
            UPDATE statistics
            SET correct_answers = correct_answers + $1,
                total_answers = total_answers + $2,
                last_training_date = NOW()
            WHERE user_id = $3
        """, correct_answers, total_answers, tg_id)


async def add_word(eng_word, rus_word):
    async with pool.acquire() as conn:

        existing = await conn.fetchrow("""
            SELECT * FROM words
            WHERE english_word = $1 OR russian_word = $2
        """, eng_word, rus_word)

        if existing:
            return existing

        await conn.execute("""
            INSERT INTO words (english_word, russian_word)
            VALUES ($1, $2)
        """, eng_word, rus_word)

        return False


async def delete_word(eng_word, rus_word):
    async with pool.acquire() as conn:

        await conn.execute("""
            DELETE FROM words 
            WHERE english_word = $1 AND russian_word = $2
        """, eng_word, rus_word)

        

async def get_words(type_word, lang_training):
    async with pool.acquire() as conn:
        if type_word == "✅ Выученные слова":
            type_word = "know"
        elif type_word == "🆕 Новые слова":
            type_word = "new"
        elif type_word == "📜 Все слова":
            type_word = None
        
        if type_word:
            words = await conn.fetch("""
                SELECT english_word, russian_word
                FROM words
                WHERE status = $1
                ORDER BY created_at DESC
            """, type_word)
        else:
            words = await conn.fetch("""
                SELECT english_word, russian_word
                FROM words
                ORDER BY created_at DESC
            """)

    
        words_list = [(word['english_word'], word['russian_word']) for word in words]
        
        # В зависимости от направления тренировки, меняем порядок слов
        if lang_training == "🇬🇧 ➡️ 🇷🇺 Перевод с английского":  # тренировка с английского на русский
            return words_list
        elif lang_training == "🇷🇺 ➡️ 🇬🇧 Перевод с русского":  # тренировка с русского на английский
            return [(russian, english) for english, russian in words_list]

        return words_list

async def update_word(eng_word, rus_word, new_eng_word, new_rus_word):
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("""
            SELECT * FROM words
            WHERE (english_word = $1 OR russian_word = $2)
              AND NOT (english_word = $3 AND russian_word = $4)
        """, new_eng_word, new_rus_word, eng_word, rus_word)

        if existing:
            return existing
        
        await conn.execute("""
            UPDATE words
            SET english_word = $1, russian_word = $2
            WHERE english_word = $3 AND russian_word = $4
        """, new_eng_word, new_rus_word, eng_word, rus_word)

        
        return False

async def save_word(correct_word, option, lang_training):
    async with pool.acquire() as conn:
        if lang_training == "🇷🇺 ➡️ 🇬🇧 Перевод с русского":
            correct_word[0], correct_word[1] = correct_word[1], correct_word[0]

        await conn.execute("""
            UPDATE words 
            SET status = $1
            WHERE english_word = $2 AND russian_word = $3
        """, option, correct_word[0], correct_word[1])

        