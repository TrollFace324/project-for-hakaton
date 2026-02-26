from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()

# Перечисление для эмоционального окраса
class SentimentEnum(enum.Enum):
    POSITIVE = "позитив"
    NEUTRAL = "нейтраль"
    NEGATIVE = "негатив"

# ========== ТАБЛИЦА 1: Обращения ==========
class Appeal(Base):
    __tablename__ = 'appeals'

    id = Column(Integer, primary_key=True)
    
    # Основные поля (как и были)
    received_date = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String(200))
    facility = Column(String(300))
    phone = Column(String(50))
    email = Column(String(100))
    device_serial_numbers = Column(Text)
    device_type = Column(String(200))
    sentiment = Column(Enum(SentimentEnum), default=SentimentEnum.NEUTRAL)
    issue_description = Column(Text)
    
    # UID сообщения - это ключ для связи со второй таблицей
    original_uid = Column(String(100), unique=True)  # уникальный ключ
    
    # Сырой текст письма (оставляем для истории)
    
    # Дата создания записи в БД
    
    # Связь с таблицей conversation (один-к-одному)
    conversation = relationship("Conversation", back_populates="appeal", uselist=False)

# ========== ТАБЛИЦА 2: Переписка ==========
class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    
    # Связь с обращением (внешний ключ на original_uid)
    appeal_uid = Column(String(100), ForeignKey('appeals.original_uid'), unique=True)
    
    # Поля переписки
    operator_message = Column(Text)           # сообщение от оператора
    ai_response = Column(Text)                 # ответ-1 от ИИ
    operator_response = Column(Text)           # ответ-2 от оператора
    ai_confidence = Column(Float, default=0.0) # параметр уверенности ответа ИИ
    
    # Дата создания записи
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Обратная связь с обращением
    appeal = relationship("Appeal", back_populates="conversation")

# Создаём подключение к базе
engine = create_engine('sqlite:///appeals.db', echo=True)

# Создаём таблицы
Base.metadata.create_all(engine)

# Фабрика сессий
Session = sessionmaker(bind=engine)