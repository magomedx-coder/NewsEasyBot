import sqlite3
from datetime import datetime
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'easynews.db')

def normalize_date(date_str):
    if not date_str:
        return datetime.now().strftime('%d:%m:%Y')

    date_str = str(date_str).lower().strip()

    if re.match(r'^\d{1,2}:\d{2}$', date_str):
        current_date = datetime.now()
        return current_date.strftime('%d:%m:%Y')

    try:
        if re.match(r'\d{2}:\d{2}:\d{4}', date_str):
            return date_str

        date_formats = [
            '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%Y.%m.%d', '%Y/%m/%d', '%d %b %Y', '%d %B %Y'
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%d:%m:%Y')
            except ValueError:
                continue

        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_part, fmt)
                    return dt.strftime('%d:%m:%Y')
                except ValueError:
                    continue

    except Exception as e:
        print(f"Ошибка при преобразовании даты '{date_str}': {e}")

    return datetime.now().strftime('%d:%m:%Y')


def get_db_connection():
    return sqlite3.connect(DB_PATH)

def save_to_database(news_item):
    category = news_item.get('category', '').lower().strip()
    date = normalize_date(news_item.get('date'))
    ist = news_item.get('ist', '').strip()
    link = news_item.get('link', '').strip()
    short_text = news_item.get('short_text', '').strip()
    content = news_item.get('content', '').strip()

    if not all([category, ist, link, short_text]):
        print("Отсутствуют обязательные поля")
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM EasyNews WHERE link = ?', (link,))
        if cursor.fetchone():
            print(f"Новость уже существует: {link}")
            conn.close()
            return False

        cursor.execute('''
        INSERT INTO EasyNews (category, date, ist, link, short_text, content)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, date, ist, link, short_text, content))

        conn.commit()
        conn.close()

        print(f"Новость сохранена: {short_text}")
        return True

    except sqlite3.Error as e:
        print(f"Ошибка при сохранении в базу данных: {e}")
        return False


# db_handler.py (дополнение)
def get_news(limit=10, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT category, date, ist, link, short_text, content 
    FROM EasyNews 
    ORDER BY created_at DESC 
    LIMIT ? OFFSET ?
    ''', (limit, offset))

    news = []
    for item in cursor.fetchall():
        news.append({
            'category': item[0],
            'date': item[1],
            'ist': item[2],
            'link': item[3],
            'short_text': item[4],
            'content': item[5]
        })

    conn.close()
    return news


def get_news_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM EasyNews')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# DB/manageDB.py
def get_news_by_source(source_name):
    """Получить новости по конкретному источнику"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, date, ist, link, short_text, content 
            FROM EasyNews 
            WHERE LOWER(ist) LIKE ? 
            ORDER BY created_at DESC
        ''', (f"%{source_name.lower()}%",))
        
        rows = cursor.fetchall()
        conn.close()
        
        news_list = []
        for item in rows:
            news_list.append({
                'category': item[0],
                'date': item[1],
                'ist': item[2],
                'link': item[3],
                'short_text': item[4],
                'content': item[5]
            })
        
        return news_list
        
    except sqlite3.Error as e:
        print(f"Ошибка при получении новостей по источнику: {e}")
        return []



def search_news_by_keyword(keyword, limit=10, offset=0):
    """Поиск новостей по ключевым словам (в short_text и content)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"""
            SELECT category, date, ist, link, short_text, content
            FROM EasyNews
            WHERE LOWER(short_text) LIKE ? OR LOWER(content) LIKE ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params = (f"%{keyword.lower()}%", f"%{keyword.lower()}%", limit, offset)
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        conn.close()
        
        news_list = []
        for item in rows:
            news_list.append({
                'category': item[0],
                'date': item[1],
                'ist': item[2],
                'link': item[3],
                'short_text': item[4],
                'content': item[5]
            })
        
        return news_list
    except sqlite3.Error as e:
        print(f"Ошибка при поиске новостей по ключевым словам: {e}")
        return []
