import os
import asyncio
from time import sleep
import tinvest
from tinvest import AsyncClient, SyncClient, InstrumentType, CandleResolution, Streaming
from database import init_db
from sqlalchemy import create_engine
from bot import daily_report


def main():
    TOKEN = os.getenv('TOKEN')
    MARIADB_HOST = os.getenv('MARIADB_HOST')
    MARIADB_DB = os.getenv('MARIADB_DB')
    MARIADB_USER = os.getenv('MARIADB_USER')
    MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')

    client = SyncClient(TOKEN)

    engine = create_engine(
        f'mysql+pymysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_HOST}/{MARIADB_DB}?charset=utf8mb4')
    init_db(engine)

    portfolio = client.get_portfolio()

    my_figies = list()
    for position in portfolio.payload.positions:
        if position.instrument_type == InstrumentType.stock:
            my_figies.append(position.figi)

    for figi in my_figies:
        a = client.get_market_orderbook(figi, 0)
        timestamp_ = timestamp
        last_price = client.get_market_orderbook(figi, 0).payload.last_price


main()

# daily_report()
