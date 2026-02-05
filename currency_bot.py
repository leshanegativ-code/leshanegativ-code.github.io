#!/usr/bin/env python3
"""Телеграм-бот для проверки курсов валют к доллару США."""

import logging
import os
from datetime import datetime

import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Флаги и названия валют
CURRENCIES = {
    "CNY": {"name": "Китайский юань", "flag": "🇨🇳"},
    "KZT": {"name": "Казахстанский тенге", "flag": "🇰🇿"},
    "RUB": {"name": "Российский рубль", "flag": "🇷🇺"},
    "UAH": {"name": "Украинская гривна", "flag": "🇺🇦"},
    "EUR": {"name": "Евро", "flag": "🇪🇺"},
    "GBP": {"name": "Британский фунт", "flag": "🇬🇧"},
}


def get_exchange_rates():
    """Получить курсы валют к доллару США через API exchangerate-api.com."""
    try:
        # Используем бесплатный API (без регистрации)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start - приветствие."""
    user = update.effective_user
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я помогу узнать актуальный курс доллара США к разным валютам.\n\n"
        "📊 Доступные команды:\n"
        "/rates - Показать все курсы\n"
        "/help - Справка"
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help - помощь."""
    help_text = (
        "💱 <b>Бот курсов валют</b>\n\n"
        "Команды:\n"
        "/rates - Показать актуальные курсы доллара США\n"
        "/start - Начать работу\n"
        "/help - Эта справка\n\n"
        "Данные обновляются в реальном времени с помощью API exchangerate-api.com"
    )
    await update.message.reply_html(help_text)


async def rates_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /rates - показать курсы валют."""
    await update.message.reply_text("⏳ Получаю актуальные курсы...")

    rates = get_exchange_rates()
    
    if not rates:
        await update.message.reply_text(
            "❌ Не удалось получить данные о курсах. Попробуйте позже."
        )
        return

    # Формируем сообщение с курсами
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    message = f"💵 <b>Курс доллара США (USD)</b>\n🕐 {now}\n\n"

    for code, info in CURRENCIES.items():
        rate = rates.get(code)
        if rate:
            flag = info["flag"]
            name = info["name"]
            message += f"{flag} <b>{name}</b>\n1 USD = {rate:.4f} {code}\n\n"
        else:
            message += f"{info['flag']} {info['name']}: данные недоступны\n\n"

    await update.message.reply_html(message)


async def main() -> None:
    """Главная функция для запуска бота."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "❌ Не найден токен! Установите переменную окружения TELEGRAM_BOT_TOKEN"
        )

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rates", rates_command))

    # Запускаем бота
    logger.info("🚀 Бот запущен!")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
