from bs4 import BeautifulSoup
import logging
from .base_parser import fetch_rss_sync

logger = logging.getLogger(__name__)

def parse_interfax_ru_sync():
    
    url = 'https://www.interfax.ru/rss.asp'
    content = fetch_rss_sync(url)
    
    if not content:
        return []
    
    try:
        soup = BeautifulSoup(content, 'xml')
        items = soup.find_all('item')
        
        news_list = []
        for item in items[:10]:
            title = item.title.text if item.title else 'Без заголовка'
            link = item.link.text if item.link else '#'
            description = item.description.text if item.description else 'Нет описания'
            pub_date = item.pubDate.text if item.pubDate else 'Дата неизвестна'
            
            news_list.append({
                'title': title.strip(),
                'link': link.strip(),
                'description': description.strip(),
                'pub_date': pub_date.strip(),
                'source': 'Interfax.ru'
            })
        
        return news_list
    except Exception as e:
        logger.error(f"Ошибка при парсинге Interfax.ru: {e}")
        return []
