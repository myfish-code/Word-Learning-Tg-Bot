import asyncpg
import asyncio
from config import DATABASE_URL

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

async def create_tables():
    conn = await connect_to_db()

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            english_word TEXT NOT NULL,  -- английское слово
            russian_word TEXT NOT NULL,  -- перевод на русский
            status TEXT DEFAULT 'new',  -- статус: 'new' или 'learned'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            last_training_date TIMESTAMP DEFAULT NULL
        );
    """)
    await conn.close()

async def main():
    await create_tables()

if __name__ == '__main__':
    asyncio.run(main())