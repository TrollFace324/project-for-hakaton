from email_parser import fetch_emails
from db_utils import save_emails
from datetime import datetime, timedelta

def main():
    # Настройки (лучше вынести в конфиг или переменные окружения)
    IMAP_SERVER = 'imap.gmail.com'
    EMAIL = 'your.email@gmail.com'
    PASSWORD = 'password_for_email'

    # Забираем письма за последние сутки (чтобы не грузить всё подряд)
    since = datetime.now() - timedelta(days=1)
    emails = fetch_emails(IMAP_SERVER, EMAIL, PASSWORD, since_date=since)
    save_emails(emails)
    print(f'Обработано {len(emails)} писем.')

if __name__ == '__main__':
    main()