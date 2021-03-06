import os
from tinvest import SyncClient, InstrumentType
from database import Base, Stock
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot import send_message, daily_report
from app_types import currency_types
from pytz import timezone
from apscheduler.schedulers.background import BlockingScheduler
import collections
from yaml import load, Loader


scheduler = BlockingScheduler()


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


def stocks_database_list_to_stocks_dict(stocks_list, stocks_set):
    result = dict()
    for stock in stocks_list:
        if stock.ticker in stocks_set:
            result[stock.ticker] = {
                'ticker': stock.ticker,
                'name': stock.name,
                'buy_price': stock.buy_price,
                'currency': stock.currency,
                'amount': stock.amount
            }
    return result


def stocks_to_dict(client, stocks):
    result = dict()
    for stock in stocks:
        result[stock.name] = {
            'ticker': stock.ticker,
            'name': stock.name,
            'buy_price': stock.buy_price,
            'currency': stock.currency,
            'amount': stock.amount,
            'current_price': stock.current_price
        }
    return result


def report():
    investing_token = os.getenv('TOKEN')
    mariadb_host = os.getenv('MARIADB_HOST')
    mariadb_port = os.getenv('MARIADB_PORT')
    mariadb_db = os.getenv('MARIADB_DB')
    mariadb_user = os.getenv('MARIADB_USER')
    mariadb_password = os.getenv('MARIADB_PASSWORD')

    client = SyncClient(investing_token)

    engine = create_engine(
        f'mysql+pymysql://{mariadb_user}:{mariadb_password}@{mariadb_host}:{mariadb_port}/{mariadb_db}?charset=utf8mb4')
    Base.metadata.create_all(engine, checkfirst=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    database_stocks = session.query(Stock).all()
    database_stocks_dict = stocks_to_dict(client, database_stocks)

    sorted_dict = collections.OrderedDict(sorted(database_stocks_dict.items()))

    daily_report(sorted_dict)


def delta(prev, now):
    d = now.replace(tzinfo=None) - prev.replace(tzinfo=None)
    days = d.days
    hours = d.seconds // 3600
    minutes = (d.seconds // 60) % 60
    if hours > 72:
        return f'{days} days'
    elif hours > 1:
        return f'{hours} hours'
    elif minutes > 1:
        return f'{minutes} minutes'
    else:
        return f'{d.seconds} seconds'


@scheduler.scheduled_job(trigger='cron', minute='*')
def update_database():
    investing_token = os.getenv('TOKEN')
    tz = os.getenv('TIMEZONE')
    mariadb_host = os.getenv('MARIADB_HOST')
    mariadb_port = os.getenv('MARIADB_PORT')
    mariadb_db = os.getenv('MARIADB_DB')
    mariadb_user = os.getenv('MARIADB_USER')
    mariadb_password = os.getenv('MARIADB_PASSWORD')

    with open('config.yml', 'r') as f:
        config = load(f, Loader=Loader)
    notifications_stock_change_percent = config['notifications']['stock_change']['percent']

    client = SyncClient(investing_token)

    engine = create_engine(
        f'mysql+pymysql://{mariadb_user}:{mariadb_password}@{mariadb_host}:{mariadb_port}/{mariadb_db}?charset=utf8mb4')
    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio = client.get_portfolio()
    portfolio_stocks = filter_stocks(portfolio)
    portfolio_stocks_set = stocks_to_set(portfolio_stocks)
    portfolio_stocks_dict = stocks_list_to_stocks_dict(client, portfolio_stocks, portfolio_stocks_set)

    database_stocks = session.query(Stock).all()
    database_stocks_set = set([stock.ticker for stock in database_stocks])

    # new stock bought
    new_stocks = portfolio_stocks_set.difference(database_stocks_set)
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
    sell_stocks_dict = stocks_database_list_to_stocks_dict(database_stocks, sell_stocks_set)
    if len(sell_stocks_set) > 0:
        message = "<b>Sell stocks:</b>\n\n"
        for stock in sell_stocks_set:
            append_message = (
                f'Stock: <a href="https://www.tinkoff.ru/invest/stocks/{stock}/">{sell_stocks_dict[stock]["name"]}</a>\n'
                f'Amount: {sell_stocks_dict[stock]["amount"]}\n\n'
            )
            message = message + append_message
        send_message(message)

    # Update database
    new_stocks_dict = stocks_list_to_stocks_dict(client, portfolio_stocks, new_stocks)
    if len(new_stocks) > 0:
        for stock in new_stocks:
            session.add(Stock(
                ticker=new_stocks_dict[stock]['ticker'],
                name=new_stocks_dict[stock]['name'],
                buy_price=new_stocks_dict[stock]['buy_price'],
                currency=new_stocks_dict[stock]['currency'],
                amount=new_stocks_dict[stock]['amount']
            ))
    if len(sell_stocks_set) > 0:
        for stock in sell_stocks_set:
            session.query(Stock).filter(Stock.ticker == stock).delete()

    # Update existing instruments
    for c in session.query(Stock).all():
        ticker = c.ticker
        c.name = portfolio_stocks_dict[ticker]['name']
        c.buy_price = portfolio_stocks_dict[ticker]['buy_price']
        c.amount = portfolio_stocks_dict[ticker]['amount']
        c.current_price = portfolio_stocks_dict[ticker]['current_price']
        c.update_timestamp = datetime.now(tz=timezone(tz))

    # Value change notify
    for stock in session.query(Stock).all():
        if stock.last_notification_price is None:
            stock.last_notification_price = stock.current_price
        if stock.last_notification_date is None:
            stock.last_notification_date = stock.update_timestamp

        change_perc = (float(stock.current_price) - float(stock.last_notification_price)) / float(stock.last_notification_price) * 100
        if abs(change_perc) >= notifications_stock_change_percent:
            moving_symbol = '???' if change_perc > 0 else '???'
            timedelta_ = delta(stock.last_notification_date, stock.update_timestamp)
            message = f'<a href="https://www.tinkoff.ru/invest/stocks/{stock.ticker}/">{stock.name}</a> {moving_symbol}\n'
            message += f'{change_perc:.2f}% for the last {timedelta_}'
            send_message(message)

            stock.last_notification_date = stock.update_timestamp
            stock.last_notification_price = stock.current_price

    session.commit()


def init():
    # check env exists
    for env in ['TIMEZONE', 'TOKEN', 'TELEGRAM_GROUP', 'TELEGRAM_TOKEN',
                'MARIADB_HOST', 'MARIADB_DB', 'MARIADB_USER', 'MARIADB_PASSWORD']:
        if os.getenv(env) is None:
            print(f'There is no {env} environment variable')
            exit(0)

    # check config exists
    if not os.path.exists('config.yml'):
        print(f'There is no config.yml file. Create one with \'cp config.yml.default config.yml\'')
        exit(0)

    # create database structure
    mariadb_host = os.getenv('MARIADB_HOST')
    mariadb_port = os.getenv('MARIADB_PORT')
    mariadb_db = os.getenv('MARIADB_DB')
    mariadb_user = os.getenv('MARIADB_USER')
    mariadb_password = os.getenv('MARIADB_PASSWORD')
    engine = create_engine(
        f'mysql+pymysql://{mariadb_user}:{mariadb_password}@{mariadb_host}:{mariadb_port}/{mariadb_db}?charset=utf8mb4')
    Base.metadata.create_all(engine, checkfirst=True)


def main():
    init()
    scheduler.start()


main()
