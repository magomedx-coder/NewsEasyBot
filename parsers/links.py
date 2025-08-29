import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from fake_useragent import UserAgent
import time

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

ua = UserAgent()
fake_ua = {'user-agent': ua.random}

def get_content(url, theme):
    try:
        response = requests.get(url, headers=fake_ua)
        response.raise_for_status()
        print(f"Загружен HTML для {url}")
    except requests.RequestException as e:
        print(f"Ошибка загрузки {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'lxml')
    news_items = []

    # Универсальный поиск(ИИ)
    news_blocks = soup.find_all(lambda tag: tag.name == 'div' and (
        ('q-item' in tag.get('class', []) and 'js-rm-central-column-item' in tag.get('class', [])) or
        'news-feed__item' in tag.get('class', []) or
        'item' in tag.get('class', [])
    ))

    for item in news_blocks:
        #ссылка
        link_tag = item.find('a', class_=['q-item__link', 'news-feed__item__link', 'item__link'])
        link = link_tag.get('href') if link_tag else None

        #заголовок
        title_tag = item.find('span', class_=['q-item__title', 'news-feed__item__title', 'item__title'])
        title = title_tag.text.strip() if title_tag else ''

        #дата
        date_tag = item.find('span', class_=['q-item__date__text', 'news-feed__item__date-text', 'item__date'])
        date = date_tag.text.strip() if date_tag else ''

        if link and title and date:
            news_items.append({
                'link': link,
                'title': title,
                'date': date,
                'theme': theme
            })

    print(f"Найдено новостей для {url}: {len(news_items)}")
    print(news_items)
    time.sleep(1)
    return news_items
