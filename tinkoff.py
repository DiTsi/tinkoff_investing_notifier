import os
from time import sleep
import tinvest
import pytz
from tinvest import SyncClient, InstrumentType, OperationType, OperationTypeWithCommission
from database import Base, Stock, Operations
from datetime import datetime, timedelta
from sqlalchemy import insert, create_engine, Table, MetaData
from bot import daily_report, send_message
from sqlalchemy.orm import relationship, backref, sessionmaker


# notify_operation_types = [
#     OperationTypeWithCommission.sell
# ]
#
# operation_types = {
#     "OperationTypeWithCommission.sell": "sell"
# }

currency_types = {
    'Currency.usd': "$"
}

def get_figi_by_ticker(client, ticker):
    instrument = client.get_market_search_by_ticker(ticker=ticker)
    return instrument.payload.instruments[0].figi


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


def stocks_to_set(stocks):
    return set([stock.ticker for stock in stocks])


def stocks_list_to_stocks_dict(client, stocks_list, stocks_set):
    result = dict()
    for stock in stocks_list:
        if stock.ticker in stocks_set:
            ticker = stock.ticker
            name = stock.name
            buy_price = stock.average_position_price.value
            currency = str(stock.average_position_price.currency)
            amount = stock.balance
            current_price = get_current_price(client, stock.figi)

            result[stock.ticker] = {
                'ticker': ticker,
                'name': name,
                'buy_price': buy_price,
                'currency': currency,
                'amount': amount,
                'current_price': current_price
            }
    return result


def stocks_to_dict(stocks):
    result = dict()
    for stock in stocks:
        ticker = stock.ticker
        name = stock.name
        buy_price = stock.average_position_price.value
        currency = str(stock.average_position_price.currency)
        amount = stock.balance

        result[stock.ticker] = {
            'ticker': ticker,
            'name': name,
            'buy_price': buy_price,
            'currency': currency,
            'amount': amount
        }
    return result


# def get_operations():
#     # check for operations:
#     to_ = datetime.now()
#     from_ = to_ - timedelta(hours=3)
#     operations = client.get_operations(
#         from_=from_, to=to_, figi=get_figi_by_ticker(client, 'RIG')).payload.operations
#     if len(operations) != 0:
#         for operation in operations:
#             if operation.status == OperationStatus.done and operation.operation_type in notify_operation_types:
#                 quantity = operation.quantity
#                 currency = str(operation.currency)
#                 commission = operation.commission.value
#                 type_ = operation_types[str(operation.operation_type)]
#                 datetime_ = operation.date
#                 such_ops = session.query(Operations).filter(Operations.datetime == datetime_).filter(
#                     Operations.ticker == ticker).all()
#                 session.add({'ticker': ticker, 'quantity': quantity, 'currency': currency, 'commission': commission,
#                              'type': type_, 'datetime': datetime_})


def main():
    TOKEN = os.getenv('TOKEN')
    # TIMEZONE = os.getenv('TIMEZONE')
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
    portfolio_stocks = filter_stocks(portfolio)
    portfolio_stocks_set = stocks_to_set(portfolio_stocks)
    portfolio_stocks_dict = stocks_list_to_stocks_dicts(client, portfolio_stocks, portfolio_stocks_set)

    database_stocks = session.query(Stock).all()
    database_stocks_set = set([stock.ticker for stock in database_stocks])

    # new stock bought
    new_stocks = portfolio_stocks_set.difference(database_stocks_set)
    new_stocks = ('RIG', 'OSUR') #!
    if len(new_stocks) > 0:
        message = "<b>Bought stocks:</b>\n\n"
        for stock in new_stocks:
            append_message = (
                f'Stock: <a href="https://www.tinkoff.ru/invest/stocks/{stock}/">{portfolio_stocks_dict[stock]["name"]}</a>\n'
                f'Buy price: {portfolio_stocks_dict[stock]["buy_price"]} {currency_types[portfolio_stocks_dict[stock]["currency"]]}\n'
                f'Amount: {portfolio_stocks_dict[stock]["amount"]}\n\n'
            )
            message = message + append_message
        send_message(message)

    # sell stocks
    sell_stocks_set = database_stocks_set.difference(portfolio_stocks_set)
    if len(sell_stocks_set) > 0:
        message = "<b>Sell stocks:</b>\n\n"
        for stock in sell_stocks_set:
            append_message = (
                f'Stock: <a href="https://www.tinkoff.ru/invest/stocks/{stock}/">{database_stocks_dict[stock]["name"]}</a>\n'
                f'Amount: {database_stocks_dict[stock]["amount"]}\n\n'
            )
            message = message + append_message
        send_message(message)

    # Update database
    new_stocks_dict = stocks_list_to_stocks_dicts(client, portfolio_stocks, [stock])
    if len(new_stocks) > 0:
        for stock in new_stocks:
            session.add(new_stocks_dict[stock])

    # Update data
    for c in session.query(Stock).all():
        ticker = c.ticker
        c.amount = portfolio_stocks_dict[ticker]['amount']
        c.buy_price = portfolio_stocks_dict[ticker]['buy_price']
        c.update_timestamp = datetime.now()
        c.current_price = portfolio_stocks_dict[ticker]['current_price']

    session.commit()


main()
