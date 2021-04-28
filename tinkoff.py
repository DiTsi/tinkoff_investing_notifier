import os
import asyncio
from time import sleep
import tinvest
import pytz
from tinvest import AsyncClient, SyncClient, InstrumentType, CandleResolution, Streaming
from database import Base, Stock
from datetime import datetime
from sqlalchemy import insert, create_engine, table, Table, MetaData
from bot import daily_report
from sqlalchemy.orm import relationship, backref, sessionmaker


def get_current_price(client, figi):
    orderbook = client.get_market_orderbook(figi=figi, depth='1').payload
    return orderbook.last_price


def filter_stocks(portfolio):
    stocks = list()
    payload = portfolio.payload
    for position in payload.positions:
        if position.instrument_type == InstrumentType.stock:
            stocks.append(position)
    return stocks


def get_stocks_dicts(client, stocks):
    result = dict()
    for stock in stocks:
        ticker = stock.ticker
        name = stock.name
        buy_price = stock.average_position_price.value
        currency = str(stock.average_position_price.currency)
        amount = stock.balance
        current_price = get_current_price(client, stock.figi)
        # last_notification_price =
        # update_timestamp =

        result[stock.ticker] = {
            'ticker': ticker,
            'name': name,
            'buy_price': buy_price,
            'currency': currency,
            'amount': amount,
            'current_price': current_price
        }
    return result


def main():
    TOKEN = os.getenv('TOKEN')
    TIMEZONE = os.getenv('TIMEZONE')
    MARIADB_HOST = os.getenv('MARIADB_HOST')
    MARIADB_DB = os.getenv('MARIADB_DB')
    MARIADB_USER = os.getenv('MARIADB_USER')
    MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')

    client = SyncClient(TOKEN)

    engine = create_engine(
        f'mysql+pymysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_HOST}/{MARIADB_DB}?charset=utf8mb4')
    Base.metadata.create_all(engine, checkfirst=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio = client.get_portfolio()
    stocks = filter_stocks(portfolio)
    stocks_dict = get_stocks_dicts(client, stocks)

    # Update data
    for c in session.query(Stock).all():
        ticker = c.ticker
        if c.amount != stocks_dict[ticker]['amount'] or c.buy_price != stocks_dict[ticker]['buy_price']:
            c.amount = stocks_dict[ticker]['amount']
            c.buy_price = stocks_dict[ticker]['buy_price']
        c.update_timestamp = datetime.now()
        c.current_price = stocks_dict[ticker]['current_price']
    session.commit()


main()
