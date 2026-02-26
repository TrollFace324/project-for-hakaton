from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

# Перечисление для эмоционального окраса
class SentimentEnum(enum.Enum):
    POSITIVE = "позитив"
    NEUTRAL = "нейтраль"
    NEGATIVE = "негатив"

class Appeal(Base):
    __tablename__ = 'appeals'

    id = Column(Integer, primary_key=True)
    
    # 1. Дата поступления письма
    received_date = Column(DateTime, default=datetime.utcnow)
    
    # 2. ФИО отправителя
    full_name = Column(String(200))
    
    # 3. Объект/предприятие
    facility = Column(String(300))
    
    # 4. Телефон
    phone = Column(String(50))
    
    # 5. Email
    email = Column(String(100))
    
    # 6. Заводские номера приборов (может быть несколько)
    device_serial_numbers = Column(Text)  # Храним через запятую или как JSON
    
    # 7. Тип приборов
    device_type = Column(String(200))
    
    # 8. Эмоциональный окрас
    sentiment = Column(Enum(SentimentEnum), default=SentimentEnum.NEUTRAL)
    
    # 9. Суть вопроса
    issue_description = Column(Text)

    # 🔥 НОВОЕ: UID сообщения (уже было, но добавим комментарий)
    original_uid = Column(String(100), unique=True)
    
    # 🔥 НОВОЕ: Параметр уверенности (числовой)
    confidence_score = Column(Float, default=0.0)  # от 0.0 до 1.0
    
    # Сырой текст письма (на всякий случай)
    raw_body = Column(Text)
    
    # Ссылка на оригинальное письмо (UID)
    original_uid = Column(String(100), unique=True)
    
    # Дата создания записи в БД
    created_at = Column(DateTime, default=datetime.utcnow)

# Создаём подключение к базе
engine = create_engine('sqlite:///appeals.db', echo=True)

# Создаём таблицы
Base.metadata.create_all(engine)

# Фабрика сессий
Session = sessionmaker(bind=engine)