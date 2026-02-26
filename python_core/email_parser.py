import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import re
from datetime import datetime
from models import Appeal, SentimentEnum

def fetch_emails_from_imap(imap_server, email_address, password, mailbox='INBOX', since_date=7):
    """
    Подключается к почтовому ящику и возвращает список писем.
    since_date – опционально, забирать письма только после указанной даты (datetime).
    """
    # Подключение к серверу
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, password)
    mail.select(mailbox)

    # Поиск писем
    if since_date:
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
        
        emails.append({
            'uid': uid.decode(),
            'msg': msg
        })

    mail.close()
    mail.logout()
    return emails

def extract_full_name(from_string):
    """Извлекает ФИО из строки 'Имя Фамилия <email@domain.com>'"""
    match = re.search(r'"?(.*?)"?\s*<', from_string)
    if match:
        name = match.group(1).strip()
        if name:
            return name
    email_part = from_string.split('<')[-1].replace('>', '') if '<' in from_string else from_string
    return email_part.split('@')[0]

def extract_phone(text):
    """Ищет телефон в тексте (российские номера)"""
    patterns = [
        r'\+7[\d]{10}',
        r'8[\d]{10}',
        r'[\d]{10,11}',
        r'\+7[\s\-]?[\d]{3}[\s\-]?[\d]{3}[\s\-]?[\d]{2}[\s\-]?[\d]{2}',
        r'8[\s\-]?[\d]{3}[\s\-]?[\d]{3}[\s\-]?[\d]{2}[\s\-]?[\d]{2}'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = re.sub(r'[\s\-]', '', match.group())
            return phone
    return None

def extract_device_serials(text):
    """Ищет заводские номера (цифры, буквы, дефисы, длиной от 5 до 20 символов)"""
    pattern = r'\b[A-Z0-9\-]{5,20}\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    serials = []
    for match in matches:
        if not match.isdigit() or len(match) > 8:
            serials.append(match.upper())
    return ', '.join(serials) if serials else None

def extract_facility(text):
    """Пытается определить название предприятия/объекта"""
    keywords = ['объект', 'предприятие', 'завод', 'организация', 'ООО', 'ЗАО', 'АО', 'ИП']
    sentences = text.split('\n')
    
    for sentence in sentences[:20]:
        lower_sent = sentence.lower()
        for keyword in keywords:
            if keyword in lower_sent:
                return sentence.strip()
    return None

def analyze_sentiment(text):
    """Простой анализ тональности"""
    positive_words = ['спасибо', 'благодарю', 'отлично', 'хорошо', 'помогли', 'решили']
    negative_words = ['плохо', 'ужасно', 'не работает', 'сломалось', 'жалоба', 'проблема', 'неисправность']
    
    text_lower = text.lower()
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return SentimentEnum.POSITIVE
    elif neg_count > pos_count:
        return SentimentEnum.NEGATIVE
    else:
        return SentimentEnum.NEUTRAL

def calculate_confidence(body, extracted_fields):
    """
    Вычисляет уверенность в правильности извлечения данных
    extracted_fields = {
        'phone': найден_или_нет,
        'serials': найден_или_нет,
        'facility': найден_или_нет,
        'device_type': найден_или_нет
    }
    """
    total_fields = len(extracted_fields)
    if total_fields == 0:
        return 0.0
    
    found_fields = sum(1 for v in extracted_fields.values() if v)
    return round(found_fields / total_fields, 2)


def parse_appeal_from_email(msg, uid):
    """Парсит письмо и возвращает объект Appeal"""
    
    # Декодируем тему
    subject, encoding = decode_header(msg['Subject'])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or 'utf-8', errors='replace')
    
    # Отправитель
    from_str = msg.get('From', '')
    
    # Дата
    date_str = msg.get('Date')
    received_date = parsedate_to_datetime(date_str) if date_str else datetime.now()
    
    # Тело письма
    body = get_email_body(msg)
    
    # Извлекаем структурированные данные
    full_name = extract_full_name(from_str)
    email_addr = re.search(r'<(.+?)>', from_str)
    email_addr = email_addr.group(1) if email_addr else from_str
    
    phone = extract_phone(body)
    serials = extract_device_serials(body)
    facility = extract_facility(body)
    sentiment = analyze_sentiment(body)
    
    # Пробуем определить тип прибора по ключевым словам
    device_type = None
    device_keywords = ['газоанализатор', 'анализатор', 'прибор', 'датчик', 'сенсор']
    for keyword in device_keywords:
        if keyword.lower() in body.lower():
            lines = body.split('\n')
            for line in lines:
                if keyword.lower() in line.lower():
                    device_type = line.strip()
                    break
            break
    extracted_fields = {
        'phone': phone,
        'serials': serials,
        'facility': facility,
        'device_type': device_type
    }
    confidence = calculate_confidence(body, extracted_fields)
    # Суть вопроса (первые 200 символов тела)
    issue = body[:200].replace('\n', ' ').strip() + '...'
    
    return Appeal(
        received_date=received_date,
        full_name=full_name,
        facility=facility,
        phone=phone,
        email=email_addr,
        device_serial_numbers=serials,
        device_type=device_type,
        sentiment=sentiment,
        issue_description=issue,
        original_uid=uid,
    )

def get_email_body(msg):
    """Извлекает текст из письма"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
    else:
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='replace')
    return ''
