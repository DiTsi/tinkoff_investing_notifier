import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date, String, Float, TIMESTAMP


def init_db(engine):
    stocks_table = 'stocks'
    currencies_table = 'currencies'

    if not engine.dialect.has_table(engine, stocks_table):
        metadata = MetaData(engine)
        Table(
            stocks_table,
            metadata,
            Column('id', Integer, primary_key=True, nullable=False),
            Column('ticker', String, nullable=False),
            Column('name', String),
            Column('buy_price', Float, nullable=False),
            Column('amount', Float, nullable=False),
            Column('current_price', Float, nullable=False),
            Column('last_notification_price', Float),
            Column('update_timestamp', TIMESTAMP)
        )
        metadata.create_all()

    if not engine.dialect.has_table(engine, currencies_table):
        metadata = MetaData(engine)
        Table(
            currencies_table,
            metadata,
            Column('id', Integer, primary_key=True, nullable=False),
            Column('ticker', String, nullable=False),
            Column('name', String),
            Column('buy_price', Float, nullable=False),
            Column('amount', Float, nullable=False),
            Column('current_price', Float, nullable=False),
            Column('last_notification_price', Float),
            Column('update_timestamp', TIMESTAMP)
        )
        # Implement the creation
        metadata.create_all()

