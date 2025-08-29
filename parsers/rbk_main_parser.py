import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import lxml
from links import get_content
url = "https://www.rbc.ru/"
ua = UserAgent()
fake_ua = {'user-agent': ua.random}


response = requests.get(url, headers=fake_ua)

soup = BeautifulSoup(response.text, 'lxml')

topline_container = soup.find('nav', class_='topline__items-container')

theme_items = topline_container.find_all('li', class_='topline__item-block')

themes = []

for item in theme_items:
    link_tag = item.find('a', class_='topline__item')
    if link_tag:
        theme_name = link_tag.text.strip()
        theme_url = link_tag.get('href')
        theme_name = ' '.join(theme_name.split())

        themes.append({
            'name': theme_name,
            'url': theme_url
        })


themes.pop(0)

print(themes)

for theme_link in themes:
    get_content(theme_link.get('url'), theme_link.get('name'))
    print(theme_link.get('url'), theme_link.get('name'))

