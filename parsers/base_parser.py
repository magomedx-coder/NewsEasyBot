# parsers/base_parser.py
import requests
import logging
from time import sleep
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

def fetch_rss_sync(url: str, retries=3):
    """Синхронное получение RSS с повторными попытками"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/xml, text/xml, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Проверяем, что ответ не пустой
            if not response.content:
                raise RequestException("Empty response")
                
            return response.text
            
        except RequestException as e:
            logger.warning(f"Попытка {attempt + 1}/{retries} не удалась для {url}: {e}")
            if attempt < retries - 1:
                sleep(2)  # Ждем перед повторной попыткой
            else:
                logger.error(f"Все попытки не удались для {url}: {e}")
                return None