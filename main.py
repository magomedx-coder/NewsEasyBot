# TG/NewsEasyBot.py
import os
import threading
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher

# Правильные импорты
from TG.NewsEasyBotHandlers import router
from update_news import periodic_update 
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
from TG import search


token = os.getenv("TOKEN")

def start_background_update():
    """Запуск фонового обновления новостей"""
    thread = threading.Thread(target=periodic_update, daemon=True)
    thread.start()

async def main():
    # Запускаем фоновое обновление
    start_background_update()
    
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(search.router)
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота.")