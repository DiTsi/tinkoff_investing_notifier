import os
import asyncio
# import tinvest
from tinvest import AsyncClient, SyncClient, InstrumentType


def get_portfolio(TOKEN):
    client = SyncClient(TOKEN)
    portfolio = client.get_portfolio()
    return portfolio


def get_portfolio_currencies(TOKEN):
    client = SyncClient(TOKEN)
    portfolio_currencies = client.get_portfolio_currencies()
    return portfolio_currencies


def get_market_stocks(TOKEN):
    client = SyncClient(TOKEN)
    market_stocks = client.get_market_stocks()
    return market_stocks.payload.instruments


def get_stock_price(TOKEN, ticker):
    stocks = get_market_stocks(TOKEN)
    matches = [stock for stock in stocks if stock.ticker == ticker]
    if len(matches) == 1:
        return matches[0]


def get_stocks(portfolio):
    stocks = list()
    payload = portfolio.payload
    for position in payload.positions:
        if position.instrument_type == InstrumentType.stock:
            stocks.append(position)
    return stocks


def buy_price(stocks, tickers='ALL'):
    if tickers == 'ALL':
        tickers = ''
        for stock in stocks:
            tickers = tickers + stock.ticker + ','
    for stock in stocks:
        if stock.ticker in tickers.split(','):
            print(f'Name: {stock.name}, Buy price: {stock.balance * stock.average_position_price.value}$')


def currency_price(TOKEN, currency='USD'):
    price = 0
    currencies = get_portfolio_currencies(TOKEN)
    if currency == 'USD':
        for currency in currencies.payload.currencies:
            price = price + currency.balance * currency.currency


def main():
    TOKEN = os.getenv('TOKEN')
    portfolio = get_portfolio(TOKEN)
    currencies = get_portfolio_currencies(TOKEN)
    stocks = get_stocks(portfolio)
    # buy_price(stocks, tickers='ENDP,ACAD')
    e = get_stock_price(TOKEN, 'ACAD')
    pass


async def test():
    TOKEN = os.getenv('TOKEN')
    client = AsyncClient(TOKEN, use_sandbox=True)
    await client.get_market_stocks()


# asyncio.run(test())
main()
