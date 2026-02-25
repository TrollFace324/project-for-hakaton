from models import Session, Email

def save_emails(emails_list):
    """Сохраняет список писем в БД (пропускает уже существующие по uid)."""
    session = Session()
    try:
        for email_data in emails_list:
            # Проверяем, есть ли уже письмо с таким uid
            exists = session.query(Email).filter_by(uid=email_data['uid']).first()
            if not exists:
                new_email = Email(
                    uid=email_data['uid'],
                    subject=email_data['subject'],
                    sender=email_data['from'],
                    received_date=email_data['date'],
                    body=email_data['body']
                )
                session.add(new_email)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving emails: {e}")
    finally:
        session.close()

def get_all_emails():
    session = Session()
    emails = session.query(Email).order_by(Email.received_date.desc()).all()
    session.close()
    return emails
