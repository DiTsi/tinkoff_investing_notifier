import telegram
import os
from app_types import currency_types


def daily_report(stocks_dict):
    message = '<b>Daily Report:</b>\n\n'
    for stockkey in stocks_dict.keys():
        dif_perc = (float(stocks_dict[stockkey]['current_price']) - stocks_dict[stockkey]['buy_price']) / stocks_dict[stockkey]['buy_price'] * 100
        if dif_perc > 0:
            str_dif_perc = '+' + str("{:.2f}".format(dif_perc))
        else:
            str_dif_perc = str("{:.2f}".format(dif_perc))
        stock_text = (
            f'Stock: <a href="https://www.tinkoff.ru/invest/stocks/{stocks_dict[stockkey]["ticker"]}/">{stocks_dict[stockkey]["name"]}</a>\n'
            f'Buy price: {stocks_dict[stockkey]["buy_price"]} {currency_types[stocks_dict[stockkey]["currency"]]}\n'
            # f'Today morning price: 13.4 $ (+3%)\n'
            f'Current price: {stocks_dict[stockkey]["current_price"]} $ ({str_dif_perc} %)\n\n'
        )
        message = message + stock_text
    send_message(message)


def send_message(html_text):
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_group = os.getenv('TELEGRAM_GROUP')
    bot = telegram.Bot(token=telegram_token)
    bot.sendMessage(chat_id=telegram_group, text=html_text, parse_mode='HTML', disable_web_page_preview=True)
