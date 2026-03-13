from config import BOT_TOKEN
from aiogram import Bot, Dispatcher

import asyncio

from handlers.user import user_router
from database.db import init_db_pool

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(user_router)  




async def main():
    await init_db_pool()
    await dp.start_polling(bot,skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())