# pars/TG/NewsEasyBotHandlers.py
import time
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from DB.manageDB import search_news_by_keyword
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from TG import NewsEasyBotKeyboards as kb
from DB.manageDB import get_news, get_news_count, get_news_by_source

router = Router()

# Храним message_id отправленных новостей для каждого пользователя
user_news_messages = {}

# ----------------
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f"<b>Добро пожаловать, @{message.from_user.username}!</b>", parse_mode="html",
                        reply_markup=kb.start)


# ----------------
# Обработчик ReplyKeyboard (Новости)
@router.message(F.text == "📰Новости📰")
async def info(message: Message):
    await message.reply("<b>🏡Выберите действие: </b>", parse_mode="html", reply_markup=kb.main)


# Обработчик ReplyKeyboard (О нас)
@router.message(F.text == "💡О нас💡")
async def onas(message: Message):
    await message.reply("Команда разработчиков Pythonists")


# ----------------
# Обработчик callback_data Inline-кнопок (main)
@router.callback_query(F.data == "smotr")
async def show_news(callback: CallbackQuery):
    await show_news_with_filter(callback, source=None)


@router.callback_query(F.data == "sort")
async def callback_sort(callback: CallbackQuery):
    await callback.message.edit_text("<b>🔎Сортировка</b>", parse_mode="html", reply_markup=kb.sort)


# Обработчики для источников
@router.callback_query(F.data == "ist")
async def callback_sources(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📰 Выберите источник новостей:</b>", 
        parse_mode="html", 
        reply_markup=kb.sources
    )


@router.callback_query(F.data == "source_lenta")
async def show_lenta_news(callback: CallbackQuery):
    await show_news_with_filter(callback, source="Lenta.ru")


@router.callback_query(F.data == "source_interfax")
async def show_interfax_news(callback: CallbackQuery):
    await show_news_with_filter(callback, source="Interfax.ru")


@router.callback_query(F.data == "source_rbk")
async def show_rbk_news(callback: CallbackQuery):
    await show_news_with_filter(callback, source="РБК Новости")



async def show_news_with_filter(callback: CallbackQuery, source=None):
    """Общая функция для показа новостей с фильтром по источнику"""
    if source:
        await callback.message.edit_text(f"<b>👀 Новости {source}</b>", parse_mode="html")
        message_text = f"Выполняю поиск новостей из {source}..."
    else:
        await callback.message.edit_text("<b>👀 Все новости</b>", parse_mode="html")
        message_text = "Выполняю поиск и отправляю Вам все свежие новости..."
    
    await callback.message.answer(message_text)

    # Получаем новости с фильтром по источнику
    if source:
        news = get_news_by_source(source)
        total_news = len(news)  # Для фильтрованных новостей получаем общее количество
    else:
        news = get_news()
        total_news = get_news_count()
    
    total_pages = (total_news + 9) // 10  # Округляем вверх

    if not news:
        await callback.message.answer("Новостей нет :(")
        return

    # Отправляем новости
    sent_messages = []
    for item in news:
        news_text = f"<b>{item['category'].capitalize()}</b>\n"
        news_text += f"<i>{item['date']}</i> | {item['ist']}\n"
        news_text += f"<b>{item['short_text']}</b>\n"
        news_text += f"{item['content'][:200]}...\n" if len(item['content']) > 200 else f"{item['content']}\n"
        news_text += f"<a href='{item['link']}'>Читать полностью</a>"

        msg = await callback.message.answer(news_text, parse_mode="HTML")
        sent_messages.append(msg.message_id)

    # Сохраняем ID сообщений для возможного удаления
    user_id = callback.from_user.id
    user_news_messages[user_id] = sent_messages

    # Отправляем кнопки пагинации (только если больше 1 страницы)
    if total_pages > 1:
        pagination_msg = await callback.message.answer(
            f"Страница 1 из {total_pages}",
            reply_markup=kb.get_pagination_keyboard(0, total_pages, source)
        )
        # Сохраняем ID сообщения с пагинацией
        user_news_messages[user_id].append(pagination_msg.message_id)


# Обработчики для пагинации с учетом источника
@router.callback_query(F.data.startswith("next_"))
async def next_page(callback: CallbackQuery):
    data_parts = callback.data.split("_")
    page = int(data_parts[1])
    source = data_parts[2] if len(data_parts) > 2 and data_parts[2] != "None" else None
    
    await handle_pagination(callback, page, "next", source)


@router.callback_query(F.data.startswith("prev_"))
async def prev_page(callback: CallbackQuery):
    data_parts = callback.data.split("_")
    page = int(data_parts[1])
    source = data_parts[2] if len(data_parts) > 2 and data_parts[2] != "None" else None
    
    await handle_pagination(callback, page, "prev", source)


async def handle_pagination(callback: CallbackQuery, page: int, direction: str, source: str = None):
    """Обработчик пагинации с учетом источника"""
    user_id = callback.from_user.id

    # Удаляем предыдущие сообщения
    if user_id in user_news_messages:
        for msg_id in user_news_messages[user_id]:
            try:
                await callback.bot.delete_message(callback.message.chat.id, msg_id)
            except:
                pass  # Игнорируем ошибки удаления
        del user_news_messages[user_id]

    # Определяем новую страницу
    if direction == "next":
        new_page = page + 1
        offset = new_page * 10
    else:
        new_page = page - 1
        offset = new_page * 10

    # Получаем новые новости с учетом источника
    if source:
        all_news = get_news_by_source(source)
        total_news = len(all_news)
        # Для фильтрованных новостей делаем ручную пагинацию
        news = all_news[offset:offset + 10]
    else:
        news = get_news(offset=offset)
        total_news = get_news_count()
    
    total_pages = (total_news + 9) // 10

    if not news:
        await callback.answer("Больше новостей нет")
        return

    # Отправляем новые новости
    sent_messages = []
    for item in news:
        news_text = f"<b>{item['category'].capitalize()}</b>\n"
        news_text += f"<i>{item['date']}</i> | {item['ist']}\n"
        news_text += f"<b>{item['short_text']}</b>\n"
        news_text += f"{item['content'][:200]}...\n" if len(item['content']) > 200 else f"{item['content']}\n"
        news_text += f"<a href='{item['link']}'>Читать полностью</a>"

        msg = await callback.message.answer(news_text, parse_mode="HTML")
        sent_messages.append(msg.message_id)

    # Сохраняем ID новых сообщений
    user_news_messages[user_id] = sent_messages

    # Отправляем новые кнопки пагинации
    if total_pages > 1:
        pagination_msg = await callback.message.answer(
            f"Страница {new_page + 1} из {total_pages}",
            reply_markup=kb.get_pagination_keyboard(new_page, total_pages, source)
        )
        user_news_messages[user_id].append(pagination_msg.message_id)
    
    await callback.answer()


# Остальные обработчики...
@router.callback_query(F.data == "news")
async def callback_data(callback: CallbackQuery):
    await callback.message.edit_text("В разработке(все новости)", parse_mode="html", reply_markup=kb.back2)




@router.callback_query(F.data == "oba")
async def callback_data(callback: CallbackQuery):
    await callback.message.edit_text("В разработке(сортировка по ключевым словам и источникам)", parse_mode="html",
                                     reply_markup=kb.back1)


@router.callback_query(F.data == "back")
async def callback_data(callback: CallbackQuery):
    await callback.message.edit_text("<b>🏡Выберите действие: </b>", parse_mode="html", reply_markup=kb.main)


@router.callback_query(F.data == "back1")
async def callback_data(callback: CallbackQuery):
    await callback.message.edit_text("<b>🔎Сортировка</b>", parse_mode="html", reply_markup=kb.sort)


@router.callback_query(F.data == "back2")
async def callback_data(callback: CallbackQuery):
    await callback.message.edit_text("<b>🔎Сортировка</b>", parse_mode="html", reply_markup=kb.main)


@router.callback_query(F.data == "kluch")
async def search_by_keyword(callback: CallbackQuery):
    await callback.message.edit_text(
        "Введите ключевое слово для поиска 🔎",
        parse_mode="html",
        reply_markup=kb.back1
    )

# шаг 2 — ждём ввод текста от пользователя
@router.message()
async def keyword_input(message: Message):
    keyword = message.text.strip()

    # проверка на длину запроса
    if len(keyword) < 3:
        await message.answer("Введите хотя бы 3 символа для поиска 🔎")
        return

    # ищем в БД
    results = search_news_by_keyword(keyword, limit=5)

    if not results:
        await message.answer(
            f"По запросу <b>{keyword}</b> новостей не найдено 😔",
            parse_mode="html",
            reply_markup=kb.back1
        )
        return

    # собираем выдачу
    text = "\n\n".join([
        f"<b>{n['short_text']}</b>\nИсточник: {n['ist']}\n{n['link']}"
        for n in results
    ])

    await message.answer(
        text,
        parse_mode="html",
        reply_markup=kb.back1
    )