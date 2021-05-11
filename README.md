# tinkoff_investing_notifier
Надстройка над API Тинькофф Инвестиций и API Telegram для уведомлений пользователя о каких либо изменениях в портфеле.

## Features
- ежедневные уведомления
- уведомления о покупке/продаже акций (*пока не умеет уведомлять при покупке уже имеющихся или частичной продаже*)

## Запуск

### Python
```bash
cp config.yml.default config.yml
pip install -r requirements.txt
python tinkoff.py
```

### Docker
```bash
docker-compose up -d
```

## Переменные окружения
- **TIMEZONE** - часовой пояс в формате "Europe/Moscow" (искать [здесь](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), столбец "TZ database name")
- **MARIADB_HOST** - хост базы данных
- **MARIADB_DB** - имя базы данных
- **MARIADB_USER** - пользователь базы данных
- **MARIADB_PASSWORD** - пароль пользователя базы данных
- **TELEGRAM_GROUP** - группа в Telegram (формат: "-123456789")
- **TELEGRAM_TOKEN** - токен бота в Telegram

## Ближайшие планы
- собрать образ docker для быстрого развёртывания
