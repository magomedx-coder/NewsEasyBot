from aiogram import Router
from aiogram.types import Message
from DB.manageDB import search_news_by_keyword

router = Router()

@router.message()
async def search_news(message: Message):
    keyword = message.text.strip()
    if len(keyword) < 3:
        await message.answer("Введите хотя бы 3 символа для поиска 🔎")
        return
    
    results = search_news_by_keyword(keyword, limit=5)
    
    if not results:
        await message.answer(f"По запросу <b>{keyword}</b> новостей не найдено 😔", parse_mode="html")
        return
    
    text = "\n\n".join([
        f"<b>{n['short_text']}</b>\nИсточник: {n['ist']}\n{n['link']}" 
        for n in results
    ])
    
    await message.answer(text, parse_mode="html")
