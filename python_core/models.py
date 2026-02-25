from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Создаём базовый класс для моделей
Base = declarative_base()

# Определяем модель таблицы emails
class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    uid = Column(String(100), unique=True, nullable=False)
    subject = Column(String(500))
    sender = Column(String(200))
    received_date = Column(DateTime, default=datetime.utcnow)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Настройка БД
engine = create_engine('sqlite:///emails.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)