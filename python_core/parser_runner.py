from email_parser import fetch_emails_from_imap, parse_appeal_from_email
from db_utils import save_appeals
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()   

def main():
    # Настройки почты (берём из переменных окружения)
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    
    if not EMAIL or not PASSWORD:
        print("Ошибка: EMAIL и PASSWORD должны быть заданы в .env файле")
        return
    
    # Забираем письма за последние 30 дней
    since = datetime.now() - timedelta(days=7)
    
    print(f"Подключаюсь к почте {EMAIL}...")
    raw_emails = fetch_emails_from_imap(IMAP_SERVER, EMAIL, PASSWORD, since_date=since)
    
    # Преобразуем в обращения
    appeals = []
    for raw in raw_emails:
        appeal = parse_appeal_from_email(raw['msg'], raw['uid'])
        appeals.append(appeal)
    
    print(f"Найдено {len(appeals)} писем. Сохраняю в БД...")
    save_appeals(appeals)
    print('Готово!')

if __name__ == '__main__':
    main()