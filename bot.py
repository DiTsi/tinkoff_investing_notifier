import telegram
import os


def daily_report():
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_group = os.getenv('TELEGRAM_GROUP')
    bot = telegram.Bot(token=telegram_token)

    text = (
        f'<b>Stock: <a href="https://www.tinkoff.ru/invest/stocks/AAPL/">This is an example</a></b>\n'
        f'Buy price: 13.3 $\n'
        f'Today morning price: 13.4 $ (+3%)\n'
        f'Current price: 13.6 $ (+3.1%)\n'
        f'\n'
        f'<b>Stock: Name of Stock_2</b>\n'
        f'...\n'
    )

    bot.sendMessage(chat_id=telegram_group, text=text, parse_mode='HTML', disable_web_page_preview=True)


def send_message(html_text):
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_group = os.getenv('TELEGRAM_GROUP')
    bot = telegram.Bot(token=telegram_token)
    bot.sendMessage(chat_id=telegram_group, text=html_text, parse_mode='HTML', disable_web_page_preview=True)
