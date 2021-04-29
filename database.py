from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, nullable=False)
    ticker = Column(String(20), nullable=False, server_default='', unique=True)
    name = Column(String(80))
    buy_price = Column(Float, nullable=False, server_default='0.0')
    currency = Column(String(30), nullable=False, server_default='Currency.usd')
    amount = Column(Float, nullable=False, server_default='0.0')
    current_price = Column(Float)
    last_notification_price = Column(Float)
    update_timestamp = Column(TIMESTAMP)
