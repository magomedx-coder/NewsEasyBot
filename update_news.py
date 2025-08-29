import time
from DB.manageDB import save_to_database
from parsers.aggregator import get_all_news_sync
from parsers.rbk_news import parse_rbk_news
from DB.categorizer import categorize_article

def save_aggregated_news():
    """Сохраняет новости из всех источников"""
    print("Начинаю сбор новостей...")
    
    # Получаем новости из агрегатора
    aggregated_news = get_all_news_sync()
    
   
    parse_rbk_news()
    
    # Сохраняем агрегированные новости
    for news_item in aggregated_news:
        # Определяем категорию
        category = categorize_article(news_item['short_text'], news_item['content'])
        news_item['category'] = category
        
        # Сохраняем в базу
        save_to_database(news_item)
    
    print(f"Сохранено {len(aggregated_news)} новостей")

def periodic_update():
    """Периодическое обновление новостей"""
    while True:
        try:
            save_aggregated_news()
            print(f"Новости обновлены: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Ошибка при обновлении новостей: {e}")
        
        # Обновляем каждые 30 минут
        time.sleep(1800)

if __name__ == "__main__":
    periodic_update()