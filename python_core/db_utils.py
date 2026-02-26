from models import Session, Appeal, Conversation

# === РАБОТА С ОБРАЩЕНИЯМИ (почти без изменений) ===

def save_appeals(appeals_list):
    """Сохраняет список обращений в БД"""
    session = Session()
    try:
        for appeal in appeals_list:
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

def get_appeal_by_uid(uid):
    """Находит обращение по UID"""
    session = Session()
    appeal = session.query(Appeal).filter_by(original_uid=uid).first()
    session.close()
    return appeal

# === НОВЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ПЕРЕПИСКОЙ ===

def save_conversation(conversation_data):
    """Сохраняет или обновляет переписку по UID обращения"""
    session = Session()
    try:
        # Проверяем, есть ли уже запись
        conv = session.query(Conversation).filter_by(appeal_uid=conversation_data['appeal_uid']).first()
        
        if not conv:
            # Создаём новую
            conv = Conversation(**conversation_data)
            session.add(conv)
        else:
            # Обновляем существующую
            for key, value in conversation_data.items():
                if key != 'appeal_uid':  # не обновляем ключ
                    setattr(conv, key, value)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Ошибка сохранения переписки: {e}")
        return False
    finally:
        session.close()

def get_conversation_by_appeal_uid(uid):
    """Получает переписку по UID обращения"""
    session = Session()
    conv = session.query(Conversation).filter_by(appeal_uid=uid).first()
    session.close()
    return conv

def get_all_conversations():
    """Получает всю переписку"""
    session = Session()
    convs = session.query(Conversation).all()
    session.close()
    return convs

# === ФУНКЦИИ ДЛЯ СВЯЗАННЫХ ДАННЫХ ===

def get_appeal_with_conversation(uid):
    """Получает обращение вместе с перепиской"""
    session = Session()
    appeal = session.query(Appeal).filter_by(original_uid=uid).first()
    result = None
    if appeal:
        result = {
            'appeal': appeal,
            'conversation': appeal.conversation
        }
    session.close()
    return result

def get_all_appeals_with_conversations():
    """Получает все обращения с перепиской"""
    session = Session()
    appeals = session.query(Appeal).order_by(Appeal.received_date.desc()).all()
    result = []
    for a in appeals:
        result.append({
            'appeal': a,
            'conversation': a.conversation
        })
    session.close()
    return result