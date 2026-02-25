import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime

def fetch_emails(imap_server, email_address, password, mailbox='INBOX', since_date=None):
    """
    Подключается к почтовому ящику и возвращает список писем.
    since_date – опционально, забирать письма только после указанной даты (datetime).
    """
    # Подключение к серверу
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, password)
    mail.select(mailbox)

    # Поиск писем (например, все непрочитанные, или за период)
    if since_date:
        # Формат даты для IMAP: "01-Jan-2025"
        date_str = since_date.strftime('%d-%b-%Y')
        search_criteria = f'(SINCE {date_str})'
    else:
        search_criteria = 'ALL'

    status, messages = mail.search(None, search_criteria)
    msg_uids = messages[0].split()

    emails = []
    for uid in msg_uids:
        res, msg_data = mail.fetch(uid, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        # Декодируем тему и отправителя
        subject, encoding = decode_header(msg['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8', errors='replace')

        from_ = msg.get('From')
        date_str = msg.get('Date')

        # Парсим дату (формат может быть разным, лучше использовать email.utils)
        from email.utils import parsedate_to_datetime
        date = parsedate_to_datetime(date_str)

        # Тело письма
        body = get_email_body(msg)

        emails.append({
            'uid': uid.decode(),
            'subject': subject,
            'from': from_,
            'date': date,
            'body': body,
        })

    mail.close()
    mail.logout()
    return emails

def get_email_body(msg):
    """Извлекает текст из письма (поддерживает plain и html)."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
    else:
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='replace')
    return ''