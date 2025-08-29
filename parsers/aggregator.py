# parsers/aggregator.py
from .lenta_parser import parse_lenta_ru_sync
from .interfax_parser import parse_interfax_ru_sync
from .rbk_news import parse_rbk_news
import logging

logger = logging.getLogger(__name__)

def get_all_news_sync():
    """Собирает все новости"""
    all_news = []
    
    # Lenta.ru
    try:
        lenta_news = parse_lenta_ru_sync()
        for item in lenta_news:
            all_news.append({
                'date': item['pub_date'],
                'ist': item['source'],
                'link': item['link'],
                'short_text': item['title'],
                'content': item['description'],
                'category': 'general'
            })
    except Exception as e:
        logger.error(f"Ошибка Lenta.ru: {e}")
    
    # Interfax.ru
    try:
        interfax_news = parse_interfax_ru_sync()
        for item in interfax_news:
            all_news.append({
                'date': item['pub_date'],
                'ist': item['source'],
                'link': item['link'],
                'short_text': item['title'],
                'content': item['description'],
                'category': 'general'
            })
    except Exception as e:
        logger.error(f"Ошибка Interfax.ru: {e}")
    
    # Сортируем по дате
    all_news.sort(key=lambda x: x['date'], reverse=True)
    return all_news

def search_news_sync(keyword: str):
    """Поиск новостей по ключевому слову"""
    all_news = get_all_news_sync()
    keyword_lower = keyword.lower()

    results = []
    for item in all_news:
        if (keyword_lower in item['short_text'].lower() or 
            keyword_lower in item['content'].lower()):
            results.append(item)

    return results