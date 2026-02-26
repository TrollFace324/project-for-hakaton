from models import Session, Appeal

def save_appeals(appeals_list):
    """Сохраняет список обращений в БД"""
    session = Session()
    try:
        for appeal in appeals_list:
            # Проверяем, есть ли уже такое обращение по UID
            exists = session.query(Appeal).filter_by(original_uid=appeal.original_uid).first()
            if not exists:
                session.add(appeal)
        session.commit()
        print(f"Сохранено {len(appeals_list)} обращений")
    except Exception as e:
        session.rollback()
        print(f"Ошибка сохранения: {e}")
    finally:
        session.close()

def get_all_appeals():
    """Возвращает все обращения"""
    session = Session()
    appeals = session.query(Appeal).order_by(Appeal.received_date.desc()).all()
    session.close()
    return appeals

def get_appeals_by_sentiment(sentiment):
    """Фильтр по эмоциональному окрасу"""
    session = Session()
    appeals = session.query(Appeal).filter_by(sentiment=sentiment).all()
    session.close()
    return appeals