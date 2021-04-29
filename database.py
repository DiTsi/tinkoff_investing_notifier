import sqlalchemy
from sqlalchemy import MetaData, Table, Column, Integer, Date, String, Float, TIMESTAMP, inspect, DATETIME
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


# class Operations(Base):
#     __tablename__ = 'operations'
#     id = Column(Integer, primary_key=True, nullable=False)
#     ticker = Column(String(20), nullable=False, server_default='', unique=True)
#     quantity = Column(Float, nullable=False)
#     currency = Column(String(30), nullable=False, server_default='Currency.usd')
#     commission = Column(Float, nullable=False)
#     type = Column(String(30), nullable=False)
#     datetime = Column(DATETIME, nullable=False)
