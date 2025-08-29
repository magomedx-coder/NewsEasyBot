# RBK_news.py

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
from DB.manageDB import save_to_database
from DB.categorizer import categorize_article

def parse_rbk_news():
    source_name = "РБК Новости"
    base_url = "https://www.rbc.ru/short_news"

    ua = UserAgent()
    headers = {'user-agent': ua.random}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status() #провека на соединение

        soup = BeautifulSoup(response.text, "lxml")
        news_items = soup.find_all("div", class_="js-news-feed-item js-yandex-counter")

        for news_item in news_items:
            try:
                news_link = news_item.find("a", class_="item__link rm-cm-item-link js-rm-central-column-item-link")
                if not news_link:
                    continue

                card_url = news_link.get("href")
                short_text = news_link.text.replace("\n", "").strip()

                date_elem = news_item.find("span", class_="item__category")
                date = date_elem.text.strip() if date_elem else ""

                content = get_article_content(card_url, headers)

                category = categorize_article(short_text, content)
                news_data = {
                    'date': date,
                    'ist': source_name,
                    'link': card_url,
                    'short_text': short_text,
                    'category': category,
                    'content': content
                }

                save_to_database(news_data)

                time.sleep(1)

            except Exception as e:
                print(f"Ошибка при обработке новости: {e}")
                continue

    except Exception as e:
        print(f"Ошибка при парсинге РБК: {e}")


#функция для получения полного текста статьи. ИИ написал
def get_article_content(article_url, headers):
    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        content_element = soup.find("div", class_="article__text article__text_free")

        if content_element:
            paragraphs = content_element.find_all("p")
            content = " ".join(p.text.replace("\xa0", " ") for p in paragraphs)
            return content.strip()

        return ""

    except Exception as e:
        print(f"Ошибка при получении контента статьи {article_url}: {e}")
        return ""


if __name__ == "__main__":
    parse_rbk_news()