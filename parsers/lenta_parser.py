# parsers/lenta_parser.py
from bs4 import BeautifulSoup
import logging
from .base_parser import fetch_rss_sync

logger = logging.getLogger(__name__)

def parse_lenta_ru_sync():
    """Парсинг Lenta.ru с обработкой ошибок"""
    url = 'https://lenta.ru/rss/news'
    content = fetch_rss_sync(url)
    
    if not content:
        logger.error("Не удалось получить RSS Lenta.ru")
        return []
    
    try:
        soup = BeautifulSoup(content, 'xml')
        items = soup.find_all('item')
        
        news_list = []
        for item in items[:15]:  # Берем немного больше на случай ошибок
            try:
                title = item.title.text if item.title else 'Без заголовка'
                link = item.link.text if item.link else '#'
                description = item.description.text if item.description else 'Нет описания'
                pub_date = item.pubDate.text if item.pubDate else 'Дата неизвестна'
                
                try:
                    description_text = BeautifulSoup(description, 'html.parser').get_text()
                except:
                    description_text = description
                
                news_list.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'description': description_text.strip(),
                    'pub_date': pub_date.strip(),
                    'source': 'Lenta.ru'
                })
                
            except Exception as e:
                logger.warning(f"Ошибка при обработке элемента Lenta.ru: {e}")
                continue
        
        logger.info(f"Успешно обработано {len(news_list)} новостей Lenta.ru")
        return news_list
        
    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге Lenta.ru: {e}")
        return []
# parsers/lenta_parser.py
def parse_lenta_ru_sync():
    """Парсинг Lenta.ru с альтернативными источниками"""
    rss_urls = [
        'https://lenta.ru/rss/news',
        'https://lenta.ru/rss/latest',
        'https://lenta.ru/rss/top7'
    ]
    
    for url in rss_urls:
        content = fetch_rss_sync(url)
        if content:
            try:
                soup = BeautifulSoup(content, 'xml')
                items = soup.find_all('item')
                
                news_list = []
                for item in items[:10]:
                    try:
                        title = item.title.text if item.title else 'Без заголовка'
                        link = item.link.text if item.link else '#'
                        description = item.description.text if item.description else 'Нет описания'
                        pub_date = item.pubDate.text if item.pubDate else 'Дата неизвестна'
                        
                        try:
                            description_text = BeautifulSoup(description, 'html.parser').get_text()
                        except:
                            description_text = description
                        
                        news_list.append({
                            'title': title.strip(),
                            'link': link.strip(),
                            'description': description_text.strip(),
                            'pub_date': pub_date.strip(),
                            'source': 'Lenta.ru'
                        })
                        
                    except Exception as e:
                        continue
                
                if news_list:
                    return news_list
                    
            except Exception as e:
                continue
    
    logger.error("Не удалось получить новости Lenta.ru ни из одного источника")
    return []